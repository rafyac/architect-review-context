import pytest
from tools.architecture.create_arch_issues import parse_report, build_issue_payloads


def test_parse_report_dummy(tmp_path):
    content = """
## 5. Recommendations
| Pillar | Action | Rationale | Effort | Owner | Reference |
|-----|-----|-----|-----|-----|-----|
| Security | Implement Key Vault | Protect secrets | S | Security Lead | architecture/README.md |

## 6. Issue Draft Table
| Title | Labels | Description | Acceptance Criteria | References |
|-----|-----|-----|-----|-----|
| Test Issue | bug, triage | Example | - Must run | architecture/README.md |
"""
    p = tmp_path / "report.md"
    p.write_text(content)
    data = parse_report(str(p))
    assert len(data["recommendations"]) == 1
    assert len(data["drafts"]) == 1


def test_build_payloads():
    rec = type("R", (), {"pillar":"Security","action":"Implement Key Vault","rationale":"Protect secrets","effort":"S","owner":"Security Lead","reference":"architecture/README.md"})
    data = {"recommendations":[rec], "drafts":[]}
    payloads = build_issue_payloads(data, "recommendations", None, {})
    assert payloads[0].title.startswith("Arch Rec")
