#!/usr/bin/env bash
# collect_arg_inventory.sh
# Purpose: Canonical Azure Resource Graph (ARG) evidence collection for architecture review.
# Captures resource inventories, coverage metrics, and region distribution WITHOUT inference.
# Output: JSON + markdown summary stored under architecture/evidence/<timestamp>/
# Requirements: az CLI logged in with appropriate permissions, 'resource-graph' extension (auto-installed), jq.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
EVIDENCE_ROOT="${REPO_ROOT}/architecture/evidence"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="${EVIDENCE_ROOT}/${TIMESTAMP}"
SUMMARY_MD="${RUN_DIR}/SUMMARY.md"
SUMMARY_JSON="${RUN_DIR}/summary.json"
SUBSCRIPTION="${AZ_SUBSCRIPTION_ID:-}"  # Allow override via env

usage() {
  cat <<'EOF'
Usage: collect_arg_inventory.sh [-s <subscriptionId>] [-o <outputDir>] [--no-paging]

Options:
  -s  Subscription ID (falls back to $AZ_SUBSCRIPTION_ID or current az context)
  -o  Override output directory root (default: architecture/evidence)
  --no-paging  Use single-call queries (may truncate >1000 rows)
  -h  Help

This script:
  1. Verifies az + jq.
  2. Ensures ARG extension available.
  3. Runs a set of mandatory KQL queries.
  4. Handles paging for large result sets unless --no-paging provided.
  5. Produces raw JSON files + a markdown rollup + machine summary JSON.

Exit codes:
  0 success, non-zero on failure.
EOF
}

NO_PAGING=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    -s) SUBSCRIPTION="$2"; shift 2;;
    -o) EVIDENCE_ROOT="$2"; shift 2;;
    --no-paging) NO_PAGING=true; shift;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1" >&2; usage; exit 1;;
  esac
done

mkdir -p "$RUN_DIR"

# --- Dependency Checks ---
command -v az >/dev/null 2>&1 || { echo "az CLI not found" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "jq not found" >&2; exit 1; }

# Ensure ARG extension
if ! az extension show --name resource-graph >/dev/null 2>&1; then
  echo "Installing resource-graph extension..." >&2
  az extension add --name resource-graph >/dev/null
fi

# Resolve subscription if not provided
if [[ -z "$SUBSCRIPTION" ]]; then
  SUBSCRIPTION=$(az account show --query id -o tsv 2>/dev/null || true)
fi
if [[ -z "$SUBSCRIPTION" ]]; then
  echo "Subscription ID not resolved. Provide -s or set AZ_SUBSCRIPTION_ID." >&2
  exit 1
fi

# Write run metadata
cat > "${RUN_DIR}/run_meta.json" <<META
{
  "timestampUtc": "${TIMESTAMP}",
  "subscriptionId": "${SUBSCRIPTION}",
  "noPaging": ${NO_PAGING}
}
META

# --- Query Definitions ---
# name | filename | KQL
read -r -d '' QUERIES <<'QEOF'
baseline|baseline|resources | where subscriptionId == '{sub}' | project name, type, location, resourceGroup, tags
logicApps|logic_apps|resources | where subscriptionId == '{sub}' and type =~ 'microsoft.logic/workflows' | project name, location, resourceGroup
functionApps|function_apps|resources | where subscriptionId == '{sub}' and type =~ 'microsoft.web/sites' | project name, kind=tostring(properties.kind), location, resourceGroup
appServicePlans|app_service_plans|resources | where subscriptionId == '{sub}' and type =~ 'microsoft.web/serverfarms' | project name, location, sku=tostring(sku.tier), workerSize=tostring(sku.size), resourceGroup
keyVaults|key_vaults|resources | where subscriptionId == '{sub}' and type =~ 'microsoft.keyvault/vaults' | project name, location, resourceGroup
storageAccounts|storage_accounts|resources | where subscriptionId == '{sub}' and type =~ 'microsoft.storage/storageaccounts' | project name, location, resourceGroup
appInsights|app_insights|resources | where subscriptionId == '{sub}' and type =~ 'microsoft.insights/components' | project name, location, resourceGroup
containerApps|container_apps|resources | where subscriptionId == '{sub}' and type =~ 'microsoft.app/containerapps' | project name, location, resourceGroup
cognitiveAccounts|cognitive_accounts|resources | where subscriptionId == '{sub}' and type =~ 'microsoft.cognitiveservices/accounts' | project name, location, resourceGroup
regionDistribution|region_distribution|resources | where subscriptionId == '{sub}' | summarize count() by location | order by count_ desc
tagCoverage|tag_coverage|resources | where subscriptionId == '{sub}' | summarize total=count(), tagged=countif(isnotempty(tags)) | project tagCoveragePercent=round(100.0*tagged/total,2), total, tagged
QEOF

# Paging helper using skip tokens if available
run_query() {
  local name="$1"; local fileStem="$2"; local kqlTemplate="$3"; local kql
  kql="${kqlTemplate//\{sub\}/$SUBSCRIPTION}"
  local outFileJson="${RUN_DIR}/${fileStem}.json"
  local tmpFile="${RUN_DIR}/${fileStem}.page.json"
  local all='[]'
  local first=1000
  local skipToken=""
  if $NO_PAGING; then
    az graph query -q "$kql" --subscriptions "$SUBSCRIPTION" -o json > "$outFileJson" || { echo "Query failed: $name" >&2; return 1; }
    return 0
  fi
  while true; do
    if [[ -n "$skipToken" ]]; then
      az graph query -q "$kql" --subscriptions "$SUBSCRIPTION" --skip-token "$skipToken" --first $first -o json > "$tmpFile" || break
    else
      az graph query -q "$kql" --subscriptions "$SUBSCRIPTION" --first $first -o json > "$tmpFile" || break
    fi
    page=$(jq '.data' "$tmpFile")
    all=$(jq -c --argjson a "$all" --argjson b "$page" '$a + $b' <<<"null" | jq '.[0]') 2>/dev/null || all=$(jq -c --argjson a "$all" --argjson b "$page" '$a + $b')
    skipToken=$(jq -r '.skipToken // empty' "$tmpFile")
    [[ -z "$skipToken" ]] && break
  done
  echo "$all" > "$outFileJson"
}

printf "Collecting Azure Resource Graph evidence into %s\n" "$RUN_DIR"

while IFS='|' read -r name stem kql; do
  [[ -z "$name" ]] && continue
  echo "[ARG] $name ..."
  if run_query "$name" "$stem" "$kql"; then
    count=$(jq 'length' "${RUN_DIR}/${stem}.json" 2>/dev/null || echo 0)
    echo "  -> rows: $count"
  else
    echo "  !! failed"
  fi
done <<<"$QUERIES"

# Build summary JSON
jq -n '{
  subscription: $s,
  timestampUtc: $t,
  counts: {
    baseline: (input_filename|path|0),
    logicApps: (input_filename|path|0)
  }
}' 2>/dev/null >/dev/null || true  # Placeholder (we'll build below)

# Produce counts map
SUMMARY_OBJ='{}'
for f in baseline logic_apps function_apps app_service_plans key_vaults storage_accounts app_insights container_apps cognitive_accounts region_distribution tag_coverage; do
  if [[ -f "${RUN_DIR}/${f}.json" ]]; then
    c=$(jq 'length' "${RUN_DIR}/${f}.json" 2>/dev/null || echo 0)
    SUMMARY_OBJ=$(jq -c --arg k "$f" --argjson v $c '. + {($k): $v}' <<<"$SUMMARY_OBJ")
  fi
done

TAG_COVERAGE=$(jq -r '.[0].tagCoveragePercent // empty' "${RUN_DIR}/tag_coverage.json" 2>/dev/null || true)

cat > "$SUMMARY_JSON" <<SUMMARY
{
  "subscriptionId": "${SUBSCRIPTION}",
  "timestampUtc": "${TIMESTAMP}",
  "counts": ${SUMMARY_OBJ},
  "tagCoveragePercent": ${TAG_COVERAGE:-null}
}
SUMMARY

# Markdown summary
{
  echo "# ARG Inventory Summary (${TIMESTAMP})";
  echo "Subscription: ${SUBSCRIPTION}";
  echo "";
  echo "| Dataset | Rows | File |";
  echo "|---------|------|------|";
  for f in baseline logic_apps function_apps app_service_plans key_vaults storage_accounts app_insights container_apps cognitive_accounts region_distribution tag_coverage; do
    if [[ -f "${RUN_DIR}/${f}.json" ]]; then
      c=$(jq 'length' "${RUN_DIR}/${f}.json")
      echo "| $f | $c | ${f}.json |"
    fi
  done
  echo "";
  if [[ -n "$TAG_COVERAGE" ]]; then
    echo "Tag Coverage: ${TAG_COVERAGE}%";
  fi
  echo "";
  echo "Data collected via Azure Resource Graph. No inference.";
} > "$SUMMARY_MD"

echo "\nEvidence collection complete. Summary: $SUMMARY_MD"

echo "Next steps:"
cat <<'NX'
1. Reference SUMMARY.md in the report's Evidence Source section.
2. Use baseline JSON to compute region dispersion & resource type counts.
3. If any dataset suspiciously small, re-run with --no-paging to verify.
4. Commit the entire timestamp directory for audit traceability.
NX
