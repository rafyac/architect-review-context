# GitHub Issues Roadmap: Architectural Review Implementation

**Date Created:** October 28, 2024  
**Total Issues:** 15 (1 Epic + 14 Implementation Tasks)  
**Total Effort:** 50-60 developer-days  
**Timeline:** 6 weeks (3 sprints)  
**Status:** ✅ All issues created and ready for assignment

---

## Executive Summary

All 15 GitHub issues from the architectural review have been created and linked to Epic #102. This document provides:
1. Issue roadmap with dependencies
2. Sprint sequencing (priority ordering)
3. Team assignment recommendations
4. Acceptance criteria checklists
5. Risk mitigation tracking

---

## Issue Inventory

### Epic & Sprint Organization

| Sprint | Focus | Issues | Effort | Risk Impact |
|--------|-------|--------|--------|-------------|
| **Sprint 1** | 🔴 Critical Security & Compliance | #103-#107 (5 issues) | 15-20 days | 🔴 → 🟡 |
| **Sprint 2** | 🟡 Operational Resilience & Automation | #108-#112 (5 issues) | 20-25 days | 🟡 → 🟢 |
| **Sprint 3+** | 🟢 Optimization & Excellence | #113-#117 (5 issues) | 15-20 days | 🟢 (Maintenance) |

---

## Sprint 1: Critical Security & Compliance (Weeks 1-1.5)

**Theme:** Eliminate public endpoints; implement compliance; establish security baseline

### Issue #103: Enable Private Endpoint for Key Vault - Restrict to Private Network
**Status:** Created ✅  
**Assigned To:** [Infrastructure Team Lead]  
**Effort:** 1-2 days  
**Severity:** 🔴 CRITICAL  
**Dependencies:** None  
**Blockers for:** #104, #105  

**Description:**
- Enable private endpoint for Key Vault
- Disable public network access
- Create network rules for vnet/subnet access
- Test connectivity via private endpoint

**Acceptance Criteria:**
```
[ ] Private endpoint created and functional
[ ] publicNetworkAccess: 'Disabled' in Bicep
[ ] Network ACLs configured (default: Deny)
[ ] Container App can access via private endpoint
[ ] Security testing: curl from external IP fails (403)
```

**Implementation:**
- Bicep: Create private endpoint resource
- NSG: Add network rules for container app subnet
- Validate connectivity through private link

---

### Issue #104: Disable Public Access & Enforce RBAC on AI Foundry
**Status:** Created ✅  
**Assigned To:** [Security Engineer]  
**Effort:** 1-2 days  
**Severity:** 🔴 CRITICAL  
**Dependencies:** #105 (RBAC implementation)  
**Blockers for:** None  

**Description:**
- Disable public network access on AI Foundry
- Implement RBAC for model endpoint access
- Configure private endpoint (future enhancement)

**Acceptance Criteria:**
```
[ ] publicNetworkAccess: 'Disabled' on AI Foundry Hub & Project
[ ] RBAC role: 'Cognitive Services User' assigned to Container Apps identity
[ ] Container App can access models via private network
[ ] External users cannot access model endpoints (403)
```

---

### Issue #105: Implement Key Vault RBAC - Replace Default Policies with Least-Privilege Roles
**Status:** Created ✅  
**Assigned To:** [Security Engineer]  
**Effort:** 1-2 days  
**Severity:** 🔴 CRITICAL  
**Dependencies:** #103 (Private endpoint)  
**Blockers for:** None  

**Description:**
- Replace empty accessPolicies with RBAC role assignments
- Assign minimum required roles to:
  - Container Apps (SystemAssigned identity)
  - Function App (SystemAssigned identity)
  - Logic Apps (managed connections)

**Acceptance Criteria:**
```
[ ] accessPolicies: [] (empty) removed from Key Vault Bicep
[ ] RBAC role assignment for Container Apps identity (Key Vault Secrets User)
[ ] RBAC role assignment for Function App identity
[ ] All services can retrieve secrets without errors
[ ] No wildcard permissions (*) on any role
```

---

### Issue #106: Audit & Inventory All Storage Accounts - Remove Orphaned Resources
**Status:** Created ✅  
**Assigned To:** [Cloud Cost Analyst]  
**Effort:** 1-2 days  
**Severity:** 🟡 HIGH  
**Dependencies:** None  
**Blockers for:** #111 (FinOps tagging), #116 (consolidation)  

**Description:**
- Audit all 14 storage accounts in {RESOURCE_GROUP}
- Document purpose, owner, creation date, size
- Identify candidates for consolidation/deletion
- Estimate cost savings

**Acceptance Criteria:**
```
[ ] Audit report: all 14 accounts listed with metadata
[ ] Consolidation decision matrix: Keep/Archive/Delete for each
[ ] Cost savings calculated (estimated $25-30/month)
[ ] Decommission candidates identified
[ ] Retention policy recommendations documented
```

---

### Issue #107: Implement Model Inference Logging - Enable AI Governance Audit Trail
**Status:** Created ✅  
**Assigned To:** [AI/Compliance Engineer]  
**Effort:** 2-3 days  
**Severity:** 🔴 CRITICAL  
**Dependencies:** None  
**Blockers for:** None  

**Description:**
- Add Application Insights logging to all AI Foundry API calls
- Log: timestamp, caller identity, prompt/input, output, latency, cost
- Create KQL queries for audit & compliance reporting
- Add safeguard checks (harmful content flagging)

**Acceptance Criteria:**
```
[ ] C# middleware logs all AI Foundry calls to Application Insights
[ ] Log schema includes: timestamp, caller, input, output, cost, safety_score
[ ] KQL query created: "Show all inference calls in last 7 days"
[ ] KQL query created: "Show inferences by caller/team"
[ ] GDPR audit trail generation tested
[ ] Dashboard shows inference volume & cost trends
```

---

## Sprint 2: Operational Resilience & Automation (Weeks 2-3)

**Theme:** Build disaster recovery; automate deployment; validate infrastructure

### Issue #108: Plan Multi-Region Failover Strategy & Disaster Recovery
**Status:** Created ✅  
**Assigned To:** [Infrastructure Architect]  
**Effort:** 2-3 days  
**Severity:** 🟡 HIGH  
**Dependencies:** None  
**Blockers for:** #109 (multi-region deployment)  

**Description:**
- Design active-passive multi-region setup
- Define RTO (< 4 hours) & RPO (< 1 hour) targets
- Create failover runbook
- Plan monthly failover drills

**Acceptance Criteria:**
```
[ ] Multi-region architecture diagram created (primary: swedencentral, secondary: west europe)
[ ] Failover runbook documented (10+ steps)
[ ] RTO/RPO targets defined and documented
[ ] Cost estimate for standby resources provided
[ ] First failover drill completed successfully
```

---

### Issue #109: Automate Post-Deployment Configuration - Eliminate Manual Steps
**Status:** Created ✅  
**Assigned To:** [DevOps Engineer]  
**Effort:** 1-2 days  
**Severity:** 🟡 HIGH  
**Dependencies:** None  
**Blockers for:** None  

**Description:**
- Automate 3+ manual deployment steps in Bicep/PowerShell
- Steps: AI Foundry connector config, Office 365 auth, Key Vault secrets
- Create post-deployment validation script
- Update README to "just run deploy.ps1"

**Acceptance Criteria:**
```
[ ] All manual post-deployment steps automated in Bicep
[ ] PowerShell post-deployment script created
[ ] AI Foundry connector configured automatically
[ ] Key Vault secrets pre-populated
[ ] Deployment validation script passes
[ ] README updated: zero manual steps documented
```

---

### Issue #110: Add IaC Validation Testing - Detect Breaking Changes in CI/CD
**Status:** Created ✅  
**Assigned To:** [DevOps Engineer]  
**Effort:** 1-2 days  
**Severity:** 🟡 MEDIUM  
**Dependencies:** None  
**Blockers for:** None  

**Description:**
- Create GitHub Actions workflow for Bicep validation
- Add template linting & syntax checks
- Implement cost estimation on PRs
- Block merge if validation fails

**Acceptance Criteria:**
```
[ ] .github/workflows/validate-bicep.yml created
[ ] Bicep build/validate runs on all PRs
[ ] Bicep linter enforces style standards
[ ] Cost estimation run on PRs (az deployment what-if)
[ ] Branch protection: validation must pass to merge
[ ] All existing Bicep files pass validation
```

---

### Issue #111: Implement FinOps Tagging Strategy - Enable Cost Allocation & Chargeback
**Status:** Created ✅  
**Assigned To:** [Cloud Cost Analyst]  
**Effort:** 0.5-1 day  
**Severity:** 🟡 MEDIUM  
**Dependencies:** #106 (storage audit)  
**Blockers for:** None  

**Description:**
- Add standardized tags to all resources:
  - environment (dev/test/prod)
  - team (owner)
  - project (project code)
  - cost-center (billing dept)
  - created-by (creator email)
- Update Bicep with tags parameter
- Create Cost Management dashboard

**Acceptance Criteria:**
```
[ ] Tags parameter added to all Bicep modules
[ ] All new resources deployed with tags
[ ] Existing resources tagged (manual or script)
[ ] Cost Management view created (group by team/project)
[ ] Budget alerts configured
```

---

### Issue #112: Update Container Image Reference - Enable Foundry Agents Deployment
**Status:** Created ✅  
**Assigned To:** [Application Developer]  
**Effort:** 0.5-1 day  
**Severity:** 🟡 MEDIUM  
**Dependencies:** None  
**Blockers for:** #113 (health probes)  

**Description:**
- Update Container Apps Bicep: hardcoded placeholder image → ACR reference
- Create Dockerfile for Foundry.Agents
- Create GitHub Actions workflow: build/push to ACR on release
- Test deployment with real application image

**Acceptance Criteria:**
```
[ ] src/Foundry.Agents/Dockerfile created
[ ] Container image builds successfully
[ ] Image pushed to Azure Container Registry
[ ] Container App deployment uses new image
[ ] Foundry Agents start successfully (verify logs)
```

---

## Sprint 3+: Optimization & Excellence (Weeks 4-6)

**Theme:** Enhance reliability; enable governance; consolidate resources

### Issue #113: Add Container App Health Probes & Liveness Detection
**Status:** Created ✅  
**Assigned To:** [Application Developer]  
**Effort:** 0.5-1 day  
**Severity:** 🟢 LOW  
**Dependencies:** #112 (container image)  
**Blockers for:** None  

**Description:**
- Add /health endpoint to Foundry Agents
- Implement readiness probe (dependencies initialized)
- Implement liveness probe (process alive)
- Update Container Apps Bicep with probe configuration

**Acceptance Criteria:**
```
[ ] /health endpoint returns HTTP 200 + JSON status
[ ] Readiness probe configured (initialDelaySeconds: 5)
[ ] Liveness probe configured (initialDelaySeconds: 30)
[ ] Test: stop process → Azure restarts within 1-2 min
[ ] No cascading failures when replica unhealthy
```

---

### Issue #114: Upgrade AI Foundry to Standard Tier - Enable Multi-Model Deployments
**Status:** Created ✅  
**Assigned To:** [AI Engineer]  
**Effort:** 0.5-1 day  
**Severity:** 🟢 LOW  
**Dependencies:** None  
**Blockers for:** None  

**Description:**
- Upgrade AI Foundry Hub from Free to Standard tier
- Verify quotas allow 3+ concurrent model deployments
- Document cost difference ($X/month increase)
- Deploy multiple models for agents

**Acceptance Criteria:**
```
[ ] AI Foundry upgraded to Standard tier
[ ] Quota check: 3+ deployments allowed
[ ] Cost estimate provided and approved
[ ] Test: deploy 2-3 models simultaneously
[ ] All models accessible and callable
```

---

### Issue #115: Enable Logic App Workflow Version Control & CI/CD
**Status:** Created ✅  
**Assigned To:** [DevOps Engineer]  
**Effort:** 1-2 days  
**Severity:** 🟢 LOW  
**Dependencies:** None  
**Blockers for:** None  

**Description:**
- Export Logic App workflows to Git as JSON
- Create GitHub Actions workflow for deployment
- Implement PR approval workflow for production changes
- Enable easy rollback to previous versions

**Acceptance Criteria:**
```
[ ] Current Logic App workflows exported to workflows/ dir
[ ] GitHub Actions workflow created for deployment
[ ] PR approval required for production changes
[ ] Staging deployment before prod
[ ] Rollback tested: revert commit → old workflow restored
```

---

### Issue #116: Consolidate Storage Accounts - Reduce Resource Sprawl & Costs
**Status:** Created ✅  
**Assigned To:** [Cloud Architect]  
**Effort:** 1-2 days  
**Severity:** 🟢 LOW  
**Dependencies:** #106 (audit), #111 (tagging)  
**Blockers for:** None  

**Description:**
- Consolidate 14 storage accounts to 3-5 with clear purpose:
  1. foundrydata (production app data)
  2. foundrydiag (logs, backups, diagnostics)
  3. foundrydev (development/test)
- Implement blob lifecycle policies (archive/delete old data)
- Decommission orphaned accounts

**Acceptance Criteria:**
```
[ ] Consolidation plan approved
[ ] Data migrated from old accounts
[ ] New account names documented
[ ] Lifecycle policies configured
[ ] Old accounts decommissioned/deleted
[ ] Monthly cost savings verified ($25-30/month)
```

---

### Issue #117: Implement AI Output Content Moderation Filter
**Status:** Created ✅  
**Assigned To:** [AI Governance Engineer]  
**Effort:** 1-2 days  
**Severity:** 🟢 LOW  
**Dependencies:** #107 (inference logging)  
**Blockers for:** None  

**Description:**
- Add Azure AI Content Safety to agent response pipeline
- Filter harmful content before returning to user
- Log moderation results to Application Insights
- Create monitoring dashboard

**Acceptance Criteria:**
```
[ ] Content Safety resource created in Bicep
[ ] C# middleware: filter responses before returning
[ ] Harmful content detection tested
[ ] Moderation events logged to Application Insights
[ ] Dashboard shows moderation metrics
[ ] Performance impact < 100ms added latency
```

---

## Dependency Graph

```
No Dependencies
├── #106 (Storage Audit)
├── #107 (Inference Logging)
├── #108 (Multi-Region Strategy)
├── #110 (IaC Validation)
├── #111 (FinOps Tagging) → depends on #106
├── #114 (AI Tier Upgrade)
├── #115 (Logic App CI/CD)
└── #117 (Content Moderation) → depends on #107

Blocks/Depends On
├── #103 (KV Private Endpoint) → blocks #104, #105
├── #104 (AI Foundry RBAC)
├── #105 (KV RBAC) → depends on #103
├── #109 (Post-Deploy Automation)
├── #112 (Container Image) → blocks #113
├── #113 (Health Probes) → depends on #112
└── #116 (Storage Consolidation) → depends on #106, #111
```

---

## Team Assignment Recommendations

### Security Team (2 engineers, Weeks 1-1.5)
- **Primary:** #103, #104, #105
- **Secondary:** #107 (audit trail), #111 (tagging)
- **Effort:** 5-7 days

### DevOps Team (2 engineers, Weeks 1-3)
- **Sprint 1:** #109 (post-deploy)
- **Sprint 2:** #110 (IaC validation), #109 (post-deploy), #112 (container image)
- **Sprint 3:** #115 (Logic App CI/CD)
- **Effort:** 5-7 days

### Infrastructure Architect (1 engineer, Weeks 1-3)
- **Sprint 1:** #106 (audit)
- **Sprint 2:** #108 (multi-region)
- **Sprint 3:** #116 (consolidation)
- **Effort:** 4-6 days

### AI/Data Engineer (1 engineer, Week 1 + 3)
- **Sprint 1:** #107 (inference logging)
- **Sprint 3:** #114 (tier upgrade), #117 (content moderation)
- **Effort:** 3-5 days

### Application Developer (1 engineer, Sprint 2-3)
- **Sprint 2:** #112 (container image)
- **Sprint 3:** #113 (health probes)
- **Effort:** 2-3 days

### Cost/Finance Analyst (0.5 engineer, Week 1)
- **Sprint 1:** #106 (audit), #111 (tagging)
- **Sprint 3:** #116 (consolidation)
- **Effort:** 2-3 days (part-time)

---

## Sprint Execution Checklist

### Sprint 1 Kickoff

- [ ] Assign owners for each issue (#103-#107)
- [ ] Schedule daily standups (10:30 AM weekly review)
- [ ] Create shared Slack channel for sprint updates
- [ ] Set up Azure DevOps sprint board (if using ADO)
- [ ] Document acceptance criteria definitions

**Pre-Sprint Validation:**
- [ ] All dependencies resolved (none for Sprint 1)
- [ ] Bicep templates ready for modification
- [ ] Azure subscription access verified
- [ ] Cost estimates approved ($X for Key Vault PE, etc.)

**During Sprint 1:**
- [ ] #103: KV PE implementation (Days 1-2)
- [ ] #105: KV RBAC (Days 2-3)
- [ ] #106: Storage audit (Days 3-4)
- [ ] #104: AI Foundry RBAC (Days 3-4)
- [ ] #107: Inference logging (Days 4-6)

**Sprint 1 Review:**
- [ ] All 5 issues resolved/closed
- [ ] Security validation completed
- [ ] No critical regressions found
- [ ] Cost baseline established

---

### Sprint 2 Planning

**Pre-Sprint:**
- [ ] Review Sprint 1 outcomes
- [ ] Verify dependencies resolved
- [ ] Assign Sprint 2 owners (#108-#112)
- [ ] Update cost projections

**During Sprint 2:**
- [ ] #108: Multi-region architecture design (Days 1-3)
- [ ] #109: Post-deploy automation (Days 2-3)
- [ ] #110: IaC CI/CD setup (Days 4-5)
- [ ] #111: FinOps tagging (Day 5)
- [ ] #112: Container image update (Day 6)

**Sprint 2 Review:**
- [ ] All 5 issues resolved
- [ ] Multi-region strategy approved
- [ ] CI/CD pipeline validated
- [ ] Tagging applied to all resources

---

### Sprint 3 Planning

**Pre-Sprint:**
- [ ] Review Sprint 2 outcomes
- [ ] Verify all dependencies satisfied
- [ ] Assign Sprint 3 owners (#113-#117)

**During Sprint 3:**
- [ ] #113: Health probes (Days 1-2)
- [ ] #114: AI tier upgrade (Day 2)
- [ ] #115: Logic App CI/CD (Days 3-4)
- [ ] #116: Storage consolidation (Days 4-5)
- [ ] #117: Content moderation (Days 5-6)

**Sprint 3 Review:**
- [ ] All 5 issues resolved
- [ ] Resource consolidation completed
- [ ] Governance enhancements validated
- [ ] Final security/compliance audit passed

---

## Success Metrics

### By End of Sprint 1
- ✅ Security score: 🔴 → 🟡 (8 HIGH risks → 3 HIGH risks)
- ✅ Public endpoints: 2 → 0
- ✅ Inference logging: 0% → 100% of calls
- ✅ Storage audit: complete inventory

### By End of Sprint 2
- ✅ Disaster recovery: Plan → Implementation started
- ✅ Post-deployment: 3+ manual steps → 0 (fully automated)
- ✅ IaC validation: 0% → 100% coverage
- ✅ Cost visibility: 0% → 100% (all resources tagged)
- ✅ Container deployment: placeholder → real application image

### By End of Sprint 3
- ✅ Container reliability: no health checks → liveness + readiness
- ✅ AI capabilities: free tier (1 model) → standard tier (3+ models)
- ✅ Governance: manual workflows → version-controlled CI/CD
- ✅ Costs: $25-30/month waste → zero waste (consolidation complete)
- ✅ Content safety: unfiltered → filtered with moderation dashboard

---

## Escalation Path

### Issues Requiring Decision
- **#108 (Multi-region):** Requires approval on $X/month standby costs
- **#114 (AI tier upgrade):** Requires approval on cost increase
- **#116 (Storage consolidation):** Requires business approval on data archival

### Escalation Process
1. **Issue Blocker:** Notify project manager in Slack
2. **Owner Escalation:** Engineering lead → Product manager
3. **Budget Escalation:** Project manager → Finance/CFO
4. **Decision Made:** Update GitHub issue with decision & reasoning

---

## Risk Tracking

### Sprint 1 Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Key Vault PE causes connectivity issues | Low | High | Thorough testing in dev first |
| RBAC role assignments incorrect | Medium | High | Security review before prod |
| Storage audit incomplete/inaccurate | Low | Medium | Script validation + manual review |
| Inference logging adds latency | Low | High | Performance test before prod |

### Sprint 2 Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Multi-region failover untested | Medium | Critical | Monthly failover drills scheduled |
| Post-deploy script breaks existing deployments | Medium | High | Test in dev/test env first |
| IaC validation too strict (blocks valid changes) | Low | Medium | Refinement based on feedback |

### Sprint 3 Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Storage consolidation data loss | Low | Critical | Backup all data before deletion |
| Content moderation false positives | Medium | Medium | Tuning & review process |
| Health probe misconfiguration causes cascading restarts | Low | High | Careful timing/threshold tuning |

---

## Post-Completion Maintenance

### Monthly Tasks
- [ ] Review inference logging dashboards (cost trends, suspicious activity)
- [ ] Run failover drill (test multi-region failover)
- [ ] Audit Key Vault access logs (unusual access patterns)
- [ ] Review Cost Management dashboard (unexpected cost spikes)

### Quarterly Reviews
- [ ] Storage account usage analysis (consolidation working?)
- [ ] RBAC role assignment audit (least privilege maintained?)
- [ ] AI governance compliance check (moderation effectiveness?)
- [ ] Security posture assessment (new vulnerabilities?)

### Annual Planning
- [ ] Tier upgrades/downgrades based on capacity
- [ ] Multi-region expansion (if business demands)
- [ ] Disaster recovery plan updates
- [ ] Budget/cost baseline reset

---

**Report Created:** October 28, 2024  
**Status:** ✅ COMPLETE - Ready for Team Assignment & Execution  
**Epic GitHub Link:** #102  
**Individual Issue Links:** #103-#117
