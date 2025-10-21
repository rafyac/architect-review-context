#!/usr/bin/env python3
"""
create_arch_issues.py

Parses an architecture assessment report (Markdown) and creates GitHub issues via REST API.
Supports optional splitting of recommendations into parent issue + subtasks (checklist items or separate issues).
Dry-run by default; pass --apply to actually create issues.

Report expectations:
- Recommendations table under heading '## 5. Recommendations'
- Issue Draft table under heading '## 6. Issue Draft Table'

Environment variables:
- GITHUB_TOKEN: Personal Access Token with repo scope.
- GITHUB_OWNER: Repository owner (user or org).
- GITHUB_REPO: Repository name.

Usage examples:
  python tools/architecture/create_arch_issues.py --report docs/architecture/ARCHITECT_REPORT_SAMPLE.md --mode draft
  python tools/architecture/create_arch_issues.py --report docs/architecture/ARCHITECT_REPORT_SAMPLE.md --mode recommendations --apply
  python tools/architecture/create_arch_issues.py --report docs/architecture/ARCHITECT_REPORT_SAMPLE.md --mode recommendations --subtasks split --apply

Subtasks modes:
- checklist: Parent issue with markdown checklist items
- split: Each recommendation becomes its own issue; parent issue contains links

MCP integration idea:
Return JSON describing planned issue objects so an MCP GitHub server can consume and create them.
Add --emit-json to print the JSON structure to stdout.
"""
from __future__ import annotations
import os
import re
import sys
import json
import argparse
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
import urllib.request
import urllib.error

RECOMMENDATIONS_HEADING = re.compile(r"^##\s+5\.\s+Recommendations", re.IGNORECASE)
ISSUE_TABLE_HEADING = re.compile(r"^##\s+6\.\s+Issue Draft Table", re.IGNORECASE)
TABLE_ROW_PATTERN = re.compile(r"^\|.*\|$")

@dataclass
class Recommendation:
    pillar: str
    action: str
    rationale: str
    effort: str
    owner: str
    reference: str

@dataclass
class IssueDraft:
    title: str
    labels: str
    description: str
    acceptance: str
    references: str

@dataclass
class IssuePayload:
    title: str
    body: str
    labels: List[str]
    parent: Optional[str] = None  # parent issue URL if any

GITHUB_API = "https://api.github.com"

class GitHubClient:
    def __init__(self, token: str, owner: str, repo: str):
        self.token = token
        self.owner = owner
        self.repo = repo

    def create_issue(self, title: str, body: str, labels: List[str]) -> Dict:
        url = f"{GITHUB_API}/repos/{self.owner}/{self.repo}/issues"
        data = json.dumps({"title": title, "body": body, "labels": labels}).encode()
        req = urllib.request.Request(url, data=data, headers={
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json"
        })
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            text = e.read().decode()
            raise RuntimeError(f"GitHub API error {e.code}: {text}")


def parse_table(lines: List[str], start_index: int) -> List[List[str]]:
    table = []
    for i in range(start_index, len(lines)):
        line = lines[i].strip()
        if not TABLE_ROW_PATTERN.match(line):
            # stop when table ends
            if table:
                break
            else:
                continue
        # split row
        parts = [p.strip() for p in line.split("|")][1:-1]  # drop leading and trailing empty from pipes
        if len(parts) < 2:
            continue
        table.append(parts)
    return table


def parse_report(path: str) -> Dict[str, List]:
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    recs: List[Recommendation] = []
    drafts: List[IssueDraft] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if RECOMMENDATIONS_HEADING.match(line):
            # skip header separator row lines
            table = parse_table(lines, i + 1)
            # Expect columns: Pillar | Action | Rationale | Effort (S/M/L) | Owner Role | Reference
            for row in table[2:]:  # first two rows header/separator
                if len(row) < 6:
                    continue
                recs.append(Recommendation(row[0], row[1], row[2], row[3], row[4], row[5]))
        if ISSUE_TABLE_HEADING.match(line):
            table = parse_table(lines, i + 1)
            # Expect columns: Title | Labels | Description | Acceptance Criteria | References
            for row in table[2:]:
                if len(row) < 5:
                    continue
                drafts.append(IssueDraft(row[0], row[1], row[2], row[3], row[4]))
        i += 1
    return {"recommendations": recs, "drafts": drafts}


def load_severity_map(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        # Normalize keys to lowercase
        norm = {}
        for level, words in raw.items():
            norm[level.lower()] = [w.lower() for w in words]
        return norm
    except Exception as e:
        print(f"Warning: could not load severity map '{path}': {e}")
        return {}

def infer_severity_labels(action: str, rationale: str, severity_map: Dict[str, List[str]]) -> List[str]:
    text = f"{action} {rationale}".lower()
    matched = []
    for level, words in severity_map.items():
        if any(w in text for w in words):
            matched.append(f"severity-{level}")
    return matched

def build_issue_payloads(data: Dict[str, List], mode: str, subtasks: Optional[str], severity_map: Dict[str, List[str]]) -> List[IssuePayload]:
    payloads: List[IssuePayload] = []
    if mode == "recommendations":
        for rec in data["recommendations"]:
            body = (f"**Pillar:** {rec.pillar}\n\n**Action:** {rec.action}\n\n**Rationale:** {rec.rationale}\n\n"
                    f"**Effort:** {rec.effort}\n\n**Owner Role:** {rec.owner}\n\n**Reference:** {rec.reference}\n")
            labels = ["architecture", rec.pillar.lower().replace(" ", "-"), "recommendation"]
            # add severity labels if mapping provided
            labels.extend(infer_severity_labels(rec.action, rec.rationale, severity_map))
            payloads.append(IssuePayload(title=f"Arch Rec: {rec.action}", body=body, labels=labels))
        if subtasks == "split":
            # parent meta issue summarizing all
            checklist = "\n".join([f"- [ ] {p.title}" for p in payloads])
            parent = IssuePayload(title="Architecture Recommendations (Meta)", body="Checklist of created recommendation issues:\n\n" + checklist, labels=["architecture","meta"], parent=None)
            payloads.insert(0, parent)
        elif subtasks == "checklist":
            # single issue with checklist only
            checklist = "\n".join([f"- [ ] {p.title}" for p in payloads])
            solo = IssuePayload(title="Architecture Recommendations (Checklist)", body="Proposed recommendations:\n\n" + checklist, labels=["architecture","recommendation"], parent=None)
            payloads = [solo]
    elif mode == "draft":
        for d in data["drafts"]:
            body = (f"**Description:** {d.description}\n\n**Acceptance Criteria:** {d.acceptance}\n\n**References:** {d.references}\n")
            labels = [l.strip() for l in d.labels.split(",") if l.strip()]
            if "architecture" not in [l.lower() for l in labels]:
                labels.append("architecture")
            payloads.append(IssuePayload(title=d.title, body=body, labels=labels))
    return payloads


def main():
    parser = argparse.ArgumentParser(description="Create GitHub issues from architecture report")
    parser.add_argument("--report", required=True, help="Path to architecture report markdown")
    parser.add_argument("--mode", choices=["recommendations","draft"], default="draft", help="Which table to parse")
    parser.add_argument("--subtasks", choices=["checklist","split"], help="Subtask handling for recommendations mode")
    parser.add_argument("--apply", action="store_true", help="Actually create issues instead of dry-run")
    parser.add_argument("--emit-json", action="store_true", help="Output JSON payload list to stdout")
    parser.add_argument("--severity-map", help="Path to JSON mapping severity levels to keyword arrays (e.g. { 'high': ['breach','exposed'], 'medium': ['optimize'], 'low': ['refactor'] })")
    args = parser.parse_args()

    data = parse_report(args.report)
    severity_map = load_severity_map(args.severity_map)
    payloads = build_issue_payloads(data, args.mode, args.subtasks, severity_map)

    if args.emit_json:
        print(json.dumps([asdict(p) for p in payloads], indent=2))
    else:
        print(f"Prepared {len(payloads)} issue payload(s). Use --emit-json to view details.")

    if not args.apply:
        print("Dry-run: no issues created. Use --apply to create issues.")
        return

    token = os.getenv("GITHUB_TOKEN")
    owner = os.getenv("GITHUB_OWNER")
    repo = os.getenv("GITHUB_REPO")
    if not token or not owner or not repo:
        print("Missing env vars GITHUB_TOKEN/GITHUB_OWNER/GITHUB_REPO; aborting.", file=sys.stderr)
        sys.exit(1)

    client = GitHubClient(token, owner, repo)
    parent_url = None
    created = []
    for payload in payloads:
        issue = client.create_issue(payload.title, payload.body, payload.labels)
        url = issue.get("html_url")
        created.append(url)
        if payload.title.startswith("Architecture Recommendations (Meta)"):
            parent_url = url
    # If split mode, append parent links to child bodies (simpler than GraphQL mutation)
    if parent_url and args.subtasks == "split":
        print(f"Meta issue created: {parent_url}")
        for u in created:
            if u == parent_url:
                continue
            print(f"Child issue: {u}")
    print("Created issues:\n" + "\n".join(created))

if __name__ == "__main__":
    main()
