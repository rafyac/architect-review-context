# Architecture Constitution

Foundational principles guiding decisions for the Foundry Demo Agent Framework. Use these as governance anchors when evaluating changes.

## 1. Security by Design
- Enforce least privilege (RBAC scoping, managed identities, avoid broad * Contributor roles).
- Centralize secrets in Azure Key Vault; no secrets in `appsettings.json` or source.
- Apply defense-in-depth: isolate cognitive services, restrict public endpoints where feasible.
- Implement continuous secret rotation policy (Key Vault versioning / automation).

## 2. Reliability & Resilience
- Prefer multi-zone capable services in region (Sweden Central) and plan secondary region readiness option.
- Externalize state; keep Functions and Container Apps stateless for rapid recovery.
- Define recovery objectives (RPO/RTO) per critical agent (Orchestrator, RemoteData).
- Instrument with Application Insights & actionable alert rules (error rate, dependency failures).

## 3. Performance Efficiency
- Right-size compute (Functions consumption, Container Apps min/max replicas) with periodic review.
- Adopt asynchronous event-driven patterns (Event Grid) for decoupling remote data triggers.
- Cache repeated external reads when ethically permissible and consistent.

## 4. Cost Optimization (FinOps)
- Tag all resources (`env`, `owner`, `costCenter`, `app=foundry-demo`).
- Eliminate unused system topics / stale cognitive projects.
- Schedule usage reviews; decommission orphaned storage or monitoring assets.

## 5. Operational Excellence
- Treat infrastructure as product: modular Bicep (`infra/modules`) with versioned parameters.
- Separation of concerns: dev vs complete templates (`main-dev.bicep`, `main-complete.bicep`).
- CI/CD pipeline to validate Bicep (what-if) & run tests before merge.
- Maintain runbooks for agent incident triage (log query shortcuts).

## 6. Sustainability & Efficiency
- Favor region with lower carbon intensity when expansion considered; evaluate multi-region carbon trade-offs.
- Consolidate lightly used resources; avoid over-provisioning reserved capacity.
- Instrument energy and utilization metrics (where supported) to inform scaling.

## 7. Data & AI Governance (Responsible AI)
- Track prompt versions (`Agents/*Instructions.md`) with change history & review sign-off.
- Enforce input/output content logging (PII-safe) for generated emails and reports.
- Apply Responsible AI assessment for new cognitive service or model integrations (bias, misuse risk).
- Provide clear user transparency disclaimers for AI-generated content.

## 8. Observability
- Structured logging with correlation IDs linking agent steps.
- Dashboard: latency (remote data retrieval), error %, cost drivers.
- Use sampling strategy to balance telemetry volume & cost.

## 9. Change Management & Compliance
- All architectural deviations must cite this constitution section and justification.
- Use GitHub issues labeled `arch-variance` for tracking exceptions with expiry date.

## 10. Simplicity & Evolution
- Prefer simple, composable modules before introducing complex orchestration.
- Periodically reassess architecture against Azure Well-Architected to drive continuous improvement.

## Decision Record Template (Lightweight)
```
Title: <Short decision>
Date: <YYYY-MM-DD>
Context: <Relevant principles & drivers>
Options: <Enumerate>
Decision: <Chosen option + rationale>
Consequences: <Positive / Negative>
Review Date: <Future reassessment>
```

## Mapping to Frameworks
| Principle | Azure WAF Pillar | CAF Area | Responsible AI |
|-----------|------------------|----------|----------------|
| Security by Design | Security | Governance | Privacy & Security |
| Reliability & Resilience | Reliability | Platform / Operations | Reliability & Safety |
| Performance Efficiency | Performance Efficiency | Platform | Reliability & Safety |
| Cost Optimization | Cost Optimization | Strategy / Governance | Accountability |
| Operational Excellence | Operational Excellence | Operations | Transparency |
| Sustainability & Efficiency | Sustainability | Strategy | Inclusiveness |
| Data & AI Governance | Security / Operational Excellence | Governance | All (Fairness etc.) |
| Observability | Operational Excellence | Operations | Transparency |
| Change Mgmt & Compliance | Operational Excellence | Governance | Accountability |
| Simplicity & Evolution | Performance Efficiency / Operational Excellence | Strategy | Reliability & Safety |

---
Use this constitution to evaluate architecture changes and recommendations; deviations must be explicitly justified.