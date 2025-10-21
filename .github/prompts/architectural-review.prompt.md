## Title

Enterprise Cloud & AI Architect Chat Mode

## Quick Reference

**Chatmode:** `.github/chatmodes/enterprise-cloud-ai-architect.chatmode.md`  
**Detailed Instructions:** `architecture/ARCHITECT_CHAT_MODE_INSTRUCTIONS.md`  
**Report Template:** `architecture/ARCHITECT_REPORT_TEMPLATE.md`

---

## How to Use This Prompt

This prompt document provides **tactical execution guidance** (drift comparison, ARG queries, resource inventory patterns) to support the structured review process defined in the chatmode and instructions.

**Usage Pattern:**

1. Load the chatmode: `enterprise-cloud-ai-architect.chatmode.md`
2. Reference detailed process: `ARCHITECT_CHAT_MODE_INSTRUCTIONS.md` (Phase 1-4)
3. Use ARG queries below to gather live resource inventory
4. Follow drift comparison process to identify resource alignment gaps
5. Return results to chatmode for pillar analysis and recommendation generation

---

## Drift Comparison Process

Drift comparison identifies misalignment between Bicep infrastructure definitions (repo) and deployed Azure resources (live subscription).

### Execution Steps

1. **Collect Live Resources** (read-only ARG query):
   - Query subscription via Azure Resource Graph: `resources | where subscriptionId == '{SUBSCRIPTION_ID}'`
   - Extract: resource name, type, location, resource group, tags, SKU/tier
   - Focus on resource group: {RESOURCE_GROUP}

2. **Extract Bicep Definitions**:
   - Parse all `.bicep` files under `infra/modules/` and `infra/main*.bicep`
   - Identify expected resources by module: name patterns, types, locations, SKUs, tags
   - Document parameterized defaults (e.g., `location`, `skuName`, `enabledForDeployment`)

3. **Cross-Reference & Classify**:
   - **Aligned (✅):** Resource exists in Azure AND matches Bicep definition (within acceptable config variance)
   - **Undocumented (⚠️):** Resource exists in Azure BUT NOT defined in Bicep (manually created, legacy, or orphaned)
   - **Missing (⚠️):** Resource defined in Bicep BUT NOT deployed in Azure (not executed or decommissioned)
   - **Misconfigured (⚠️):** Resource exists in Azure BUT configuration diverges from Bicep (SKU, tags, access policies, network settings)

4. **Document Drift Matrix**:
   - Create table: Resource | Repo State | Azure State | Drift Type | Severity | Notes
   - Severity scoring: HIGH = security exposure or cost risk; MEDIUM = functionality/compliance gap; LOW = tagging or hygiene

5. **Highlight Cross-Pillar Impact**:
   - Security: Undocumented Key Vaults, missing network isolation, open public access
   - Cost: Untagged or orphaned resources
   - Reliability: Missing redundancy, unmonitored dependencies
   - Operations: Manual changes outside version control

### ARG Query Templates (Read-Only)

**⚠️ IMPORTANT: Use Azure MCP tools, NOT terminal commands**

```kql
# General inventory (subscription-scoped)
resources
| where subscriptionId == '{SUBSCRIPTION_ID}'
| project name, type, location, resourceGroup, tags, sku
| order by type, name

# Count resources by type
resources
| where subscriptionId == '{SUBSCRIPTION_ID}'
| summarize count() by type
| order by count() desc

# Key Vaults (security focus)
resources
| where type == 'microsoft.keyvault/vaults'
| where subscriptionId == '{SUBSCRIPTION_ID}'
| project name, location, sku = properties.sku, tags

# App Insights (reliability focus)
resources
| where type == 'microsoft.insights/components'
| where subscriptionId == '{SUBSCRIPTION_ID}'
| project name, location, appId = properties.appId, tags

# Logic Apps (operations focus)
resources
| where type == 'microsoft.logic/workflows'
| where subscriptionId == '{SUBSCRIPTION_ID}'
| project name, location, state = properties.state, tags

# Resources missing tags (cost/governance)
resources
| where subscriptionId == '{SUBSCRIPTION_ID}'
| where tags == '' or isnull(tags)
| project name, type, resourceGroup
| order by type
```

### Drift Severity Mapping

| Drift Type | Severity | Action |
|---|---|---|
| Undocumented security resource (Key Vault, NSG) | HIGH | Audit immediately; document or delete; add to Bicep |
| Undocumented cost resource (Storage, Compute) | MEDIUM | Evaluate necessity; cost chargeback; add or delete |
| Misconfigured security settings (public access, empty policies) | HIGH | Correct immediately; update Bicep; audit trail |
| Misconfigured cost settings (SKU downgrade) | MEDIUM | Validate intent; update Bicep; cost impact |
| Missing tags (all resources) | MEDIUM | Add FinOps tags; enforce via Azure Policy |
| Missing deployed resource (defined in Bicep but not in Azure) | LOW | Verify intentional (e.g., not deployed yet); update status |

### Drift Report Output Format

Include in final report:

- **Drift Summary:** X resources aligned, Y undocumented, Z misconfigured, W missing
- **Drift Matrix Table:** Resource | State | Drift Type | Severity | Reference | Recommendation
- **Top Drift Risks:** List HIGH-severity drifts with immediate remediation actions
- **Future-State Recommendation:** IaC enforcement strategy (e.g., Azure Policy, resource locks, deployment validation)

## Guardrails

- Avoid speculative technology not present unless recommending future adoption (prefix "Future:" ).
- Cite specific file paths or resource IDs for each recommendation.
- Use clear action verbs ("Implement", "Establish", "Refactor" (only for docs), "Adopt policy").
- If evidence missing, mark as "Observation: Data not available – recommend validation".

## Severity & Effort Guidance

| Severity | Definition |
|----------|------------|
| High | Non‑compliance, security exposure, material reliability risk |
| Medium | Improvement yields measurable benefit but not critical |
| Low | Optimization / hygiene |

| Effort | Definition |
|--------|------------|
| S | ≤ 1 day |
| M | ≤ 1 sprint |
| L | > 1 sprint |

## Sample Prompts (Facilitator)

- "Architect: produce the Findings Snapshot using provided inventory."
- "Architect: generate final report now."
- "Architect: convert top 5 recommendations to GitHub issue markdown rows."

## Non‑Goals

- Performance benchmarking execution.
- Live cost estimation using pricing calculators.

## Quality Check Before Output

Confirm each recommendation references either a resource group item or repo path; ensure no secrets; word count within limits.
