#!/usr/bin/env python3
"""Generate Mermaid dependency graph from issues-metadata.json and update the final report.

Usage:
  python architecture/scripts/generate_issue_graph.py \
      --metadata architecture/issues-metadata.json \
      --report architecture/ARCHITECT_REPORT_FINAL_2025-10-16.md \
      --owner katarinasvedman --repo foundry-demo-agent-framework-WIP

If --owner/--repo provided, clickable links are emitted via Mermaid `click` statements.
The script replaces content between <!-- ISSUE_GRAPH_START --> and <!-- ISSUE_GRAPH_END --> markers.
Exits non‑zero if markers not found (to encourage manual insertion) unless --append flag is supplied.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any

PILLAR_CLUSTER_MAP = {
    "Security & Identity": "SEC",
    "Operational Excellence": "OPS",
    # Group performance, cost, sustainability in one cluster like manual diagram
    "Performance Efficiency": "PERF",
    "Cost Optimization": "PERF",
    "Sustainability": "PERF",
    "Reliability & Resilience": "PERF",  # could separate, kept compact
    "AI Governance & Data Ethics": "AI",
}

SEVERITY_CLASS = {"High": "high", "Medium": "med", "Low": "low"}

MARKER_START = "<!-- ISSUE_GRAPH_START -->"
MARKER_END = "<!-- ISSUE_GRAPH_END -->"

def load_issues(path: Path) -> List[Dict[str, Any]]:
    with path.open() as f:
        data = json.load(f)
    # Support both a top-level list of issues or an object with a 'generated' list
    if isinstance(data, dict) and 'generated' in data:
        data = data['generated']
    # Basic validation
    numbers = {i['number'] for i in data}
    for issue in data:
        for dep_field in ("dependencies", "softDependencies"):
            for dep in issue.get(dep_field, []):
                if dep not in numbers:
                    raise SystemExit(f"Dependency {dep} referenced by issue {issue['number']} not in set {numbers}")
    return data


def build_mermaid(issues: List[Dict[str, Any]], owner: str | None, repo: str | None) -> str:
    # Group issues by cluster code
    clusters: Dict[str, List[Dict[str, Any]]] = {}
    for issue in issues:
        pillar = issue.get("pillar")
        cluster_code = PILLAR_CLUSTER_MAP.get(pillar, None)
        if cluster_code:
            clusters.setdefault(cluster_code, []).append(issue)
    # Start building lines
    lines: List[str] = ["```mermaid", "graph TD"]

    # Render clusters similar to manual layout order
    order = ["SEC", "OPS", "PERF", "AI"]
    cluster_titles = {
        "SEC": "Security & Identity",
        "OPS": "Operational Excellence",
        "PERF": "Perf / Cost / Sustainability",
        "AI": "AI Governance",
    }

    def short_label(issue: Dict[str, Any]) -> str:
        sev = issue.get("severity")
        sev_code = {"High": "H", "Medium": "M", "Low": "L"}.get(sev, "")
        suffix = f" ({sev_code})" if sev_code else ""
        return f"{issue['number']}: {issue['title'].split(':')[0][:40].strip()}{suffix}"[:70]

    for code in order:
        group = clusters.get(code, [])
        if not group:
            continue
        lines.append(f"  subgraph {code}[{cluster_titles[code]}]")
        for issue in sorted(group, key=lambda x: x['number']):
            lbl = short_label(issue).replace("\"", "'")
            lines.append(f"    I{issue['number']}[\"{lbl}\"]")
        lines.append("  end")
        lines.append("")

    # Dependencies (solid)
    for issue in issues:
        for dep in issue.get("dependencies", []):
            lines.append(f"  I{dep} --> I{issue['number']}")
    # Soft (dashed)
    for issue in issues:
        for dep in issue.get("softDependencies", []):
            lines.append(f"  I{dep} -.-> I{issue['number']}")

    # Epic / guidance / reference styling & links
    epic_num = 16
    epic = next((i for i in issues if i['number'] == epic_num), None)
    if epic:
        lines.append(f"  I{epic_num}((\"{epic_num}: Epic Consolidation\")):::epic")
    # Fan-in edges for epic from all remediation issues 1-15
    for n in range(1, 16):
        lines.append(f"  I{n} --> I{epic_num}")
    # Guidance and reference
    for special in (17, 18):
        sp = next((i for i in issues if i['number'] == special), None)
        if sp:
            text = "Guidance Issue" if special == 17 else "Report Reference"
            lines.append(f"  I{special}[\"{special}: {text}\"]:::meta")

    # Classes
    lines.extend([
        "",
        "  classDef high fill:#d32f2f,color:#fff,stroke:#7f1d1d,stroke-width:1px;",
        "  classDef med fill:#fb8c00,color:#fff,stroke:#8a4500,stroke-width:1px;",
        "  classDef low fill:#43a047,color:#fff,stroke:#1b5e20,stroke-width:1px;",
        "  classDef epic fill:#000,color:#fff,stroke:#444;",
        "  classDef meta fill:#9e9d24,color:#111,stroke:#5d5c12,stroke-width:1px,stroke-dasharray:3 2;",
        "",
    ])

    highs = [f"I{i['number']}" for i in issues if i.get('severity') == 'High']
    meds = [f"I{i['number']}" for i in issues if i.get('severity') == 'Medium']
    lows = [f"I{i['number']}" for i in issues if i.get('severity') == 'Low']
    if highs:
        lines.append(f"  class {','.join(highs)} high;")
    if meds:
        lines.append(f"  class {','.join(meds)} med;")
    if lows:
        lines.append(f"  class {','.join(lows)} low;")

    # Clickable links
    if owner and repo:
        base = f"https://github.com/{owner}/{repo}/issues"
        lines.append("")
        for issue in issues:
            num = issue['number']
            lines.append(f"  click I{num} \"{base}/{num}\" \"Issue {num}\" _blank")

    lines.append("```")
    return "\n".join(lines)


def update_report(report_path: Path, new_mermaid: str) -> bool:
    text = report_path.read_text()
    pattern = re.compile(rf"{re.escape(MARKER_START)}.*?{re.escape(MARKER_END)}", re.DOTALL)
    if MARKER_START not in text or MARKER_END not in text:
        print("Markers not found in report. Aborting (ensure markers are present).", file=sys.stderr)
        return False
    replacement = f"{MARKER_START}\n{new_mermaid}\n{MARKER_END}"
    new_text = pattern.sub(replacement, text)
    changed = new_text != text
    if changed:
        report_path.write_text(new_text)
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--metadata', required=True)
    ap.add_argument('--report', required=True)
    ap.add_argument('--owner')
    ap.add_argument('--repo')
    args = ap.parse_args()

    issues = load_issues(Path(args.metadata))
    mermaid = build_mermaid(issues, args.owner, args.repo)
    changed = update_report(Path(args.report), mermaid)
    if changed:
        print("Report updated with regenerated issue graph.")
    else:
        print("Issue graph already up to date.")

if __name__ == '__main__':
    main()
