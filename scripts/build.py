#!/usr/bin/env python3
"""Build the Product Fieldnotes static site from JSON editions."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
REPORTS = ROOT / "reports"

def load_reports() -> list[dict]:
    reports = []
    for path in sorted(CONTENT.glob("*.json"), reverse=True):
        with path.open(encoding="utf-8") as handle:
            report = json.load(handle)
        required = {"slug", "date", "title", "dek", "developments", "sources"}
        missing = required - report.keys()
        if missing:
            raise ValueError(f"{path.name} missing: {', '.join(sorted(missing))}")
        source_ids = {int(item["id"]) for item in report["sources"]}
        used_ids: set[int] = set()
        for item in report.get("developments", []):
            used_ids.update(map(int, item.get("source_ids", [])))
        for section in ("technique", "book", "foundation"):
            used_ids.update(map(int, report.get(section, {}).get("source_ids", [])))
        if not used_ids.issubset(source_ids):
            raise ValueError(f"{path.name} cites missing sources: {sorted(used_ids - source_ids)}")
        reports.append(report)
    if not reports:
        raise ValueError("No report JSON files found")
    return reports

def build() -> None:
    env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(["html", "xml"]), trim_blocks=True, lstrip_blocks=True)
    report_template = env.get_template("report.html")
    archive_template = env.get_template("archive.html")
    reports = load_reports()
    REPORTS.mkdir(parents=True, exist_ok=True)

    for report in reports:
        output = report_template.render(report=report, base="../")
        (REPORTS / f"{report['slug']}.html").write_text(output, encoding="utf-8")

    latest = reports[0]
    (ROOT / "index.html").write_text(report_template.render(report=latest, base=""), encoding="utf-8")
    (ROOT / "archive.html").write_text(archive_template.render(reports=reports), encoding="utf-8")
    (ROOT / "reports.json").write_text(json.dumps([
        {key: report[key] for key in ("slug", "date", "title", "dek", "reading_time", "topics")}
        for report in reports
    ], indent=2), encoding="utf-8")
    print(f"Built {len(reports)} edition(s); latest={latest['slug']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.parse_args()
    build()
