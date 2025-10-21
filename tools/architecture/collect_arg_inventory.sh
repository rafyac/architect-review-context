#!/usr/bin/env bash
# Collect Azure Resource Graph inventory for architectural review
# Usage: ./collect_arg_inventory.sh [-s SUBSCRIPTION_ID] [-g RESOURCE_GROUP]
# 
# Environment variables (used as fallbacks):
#   AZURE_SUBSCRIPTION_ID - Azure subscription ID
#   AZURE_RESOURCE_GROUP  - Azure resource group name

set -euo pipefail

# Parse command-line arguments
SUBSCRIPTION_ID="${AZURE_SUBSCRIPTION_ID:-}"
RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-}"
OUTPUT_DIR="architecture/evidence/$(date +%Y%m%d-%H%M%S)"

usage() {
  cat <<EOF
Usage: $0 [-s SUBSCRIPTION_ID] [-g RESOURCE_GROUP] [-o OUTPUT_DIR]

Collect Azure Resource Graph inventory data for architectural review.

Options:
  -s SUBSCRIPTION_ID   Azure subscription ID (overrides AZURE_SUBSCRIPTION_ID env var)
  -g RESOURCE_GROUP    Azure resource group name (overrides AZURE_RESOURCE_GROUP env var)
  -o OUTPUT_DIR        Output directory (default: architecture/evidence/TIMESTAMP)
  -h                   Show this help message

Environment variables:
  AZURE_SUBSCRIPTION_ID - Default subscription ID if -s not provided
  AZURE_RESOURCE_GROUP  - Default resource group if -g not provided

Examples:
  # Using environment variables
  AZURE_SUBSCRIPTION_ID=xxx AZURE_RESOURCE_GROUP=my-rg ./collect_arg_inventory.sh
  
  # Using command-line arguments
  ./collect_arg_inventory.sh -s xxx -g my-rg
  
  # Using both (command-line overrides env vars)
  AZURE_SUBSCRIPTION_ID=xxx ./collect_arg_inventory.sh -g my-rg

EOF
}

while getopts "s:g:o:h" opt; do
  case "$opt" in
    s) SUBSCRIPTION_ID="$OPTARG" ;;
    g) RESOURCE_GROUP="$OPTARG" ;;
    o) OUTPUT_DIR="$OPTARG" ;;
    h) usage; exit 0 ;;
    *) usage; exit 1 ;;
  esac
done

# Validate required parameters
if [[ -z "$SUBSCRIPTION_ID" ]]; then
  echo "Error: AZURE_SUBSCRIPTION_ID must be set via -s flag or AZURE_SUBSCRIPTION_ID environment variable" >&2
  usage
  exit 1
fi

echo "Collecting Azure Resource Graph inventory..."
echo "Subscription: $SUBSCRIPTION_ID"
[[ -n "$RESOURCE_GROUP" ]] && echo "Resource Group: $RESOURCE_GROUP"
echo "Output directory: $OUTPUT_DIR"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Save run metadata
cat > "$OUTPUT_DIR/run_meta.json" <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "subscription_id": "{SUBSCRIPTION_ID}",
  "resource_group": "${RESOURCE_GROUP:-all}",
  "script_version": "1.0.0"
}
EOF

# Build resource filter query
FILTER_CLAUSE=""
if [[ -n "$RESOURCE_GROUP" ]]; then
  FILTER_CLAUSE="| where resourceGroup == '$RESOURCE_GROUP'"
fi

# Query 1: General resource inventory
echo "Querying general resource inventory..."
az graph query -q "resources | where subscriptionId == '$SUBSCRIPTION_ID' $FILTER_CLAUSE | project name, type, location, resourceGroup, tags, sku | order by type, name" -o json > "$OUTPUT_DIR/resources.json"

# Query 2: Resource count by type
echo "Querying resource count by type..."
az graph query -q "resources | where subscriptionId == '$SUBSCRIPTION_ID' $FILTER_CLAUSE | summarize count() by type | order by count_ desc" -o json > "$OUTPUT_DIR/resource_counts.json"

# Query 3: Key Vaults (security focus)
echo "Querying Key Vaults..."
az graph query -q "resources | where type == 'microsoft.keyvault/vaults' | where subscriptionId == '$SUBSCRIPTION_ID' $FILTER_CLAUSE | project name, location, sku = properties.sku, tags" -o json > "$OUTPUT_DIR/keyvaults.json"

# Query 4: Application Insights (reliability focus)
echo "Querying Application Insights..."
az graph query -q "resources | where type == 'microsoft.insights/components' | where subscriptionId == '$SUBSCRIPTION_ID' $FILTER_CLAUSE | project name, location, appId = properties.appId, tags" -o json > "$OUTPUT_DIR/appinsights.json"

# Query 5: Logic Apps (operations focus)
echo "Querying Logic Apps..."
az graph query -q "resources | where type == 'microsoft.logic/workflows' | where subscriptionId == '$SUBSCRIPTION_ID' $FILTER_CLAUSE | project name, location, state = properties.state, tags" -o json > "$OUTPUT_DIR/logicapps.json"

# Query 6: Resources missing tags (cost/governance)
echo "Querying resources missing tags..."
az graph query -q "resources | where subscriptionId == '$SUBSCRIPTION_ID' $FILTER_CLAUSE | where tags == '' or isnull(tags) | project name, type, resourceGroup | order by type" -o json > "$OUTPUT_DIR/untagged_resources.json"

echo ""
echo "Collection complete! Results saved to: $OUTPUT_DIR"
echo ""
echo "Files created:"
ls -lh "$OUTPUT_DIR"
