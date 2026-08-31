#!/usr/bin/env python3
"""Editorial usefulness, novelty, rotation, and privacy gates."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


class GateError(ValueError):
    """Raised when an edition or candidate fails a publication gate."""


def _norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def _require_text(value: Any, label: str, minimum: int = 12) -> str:
    if not isinstance(value, str) or len(value.strip()) < minimum:
        raise GateError(f"{label} must be specific and non-empty")
    return value.strip()


def validate_candidate(item: dict[str, Any]) -> None:
    """Validate one proposed Radar item against editorial quality gates."""
    novelty_class = item.get("novelty_class")
    allowed = {"genuinely_new", "meaningful_extension", "distribution_update"}
    if novelty_class == "old_or_recycled" or novelty_class not in allowed:
        raise GateError("candidate is old or recycled")
    if novelty_class == "distribution_update":
        _require_text(item.get("material_consequence"), "material consequence", 24)

    for score in ("novelty_score", "evidence_score", "senior_pm_relevance_score", "applicability_score"):
        value = item.get(score)
        if not isinstance(value, int) or not 2 <= value <= 3:
            raise GateError(f"{score} must be an integer from 2 to 3")

    usefulness = _require_text(item.get("usefulness"), "specific usefulness", 32)
    generic = ("pay attention", "important for pms", "worth watching", "matters to product managers")
    if any(phrase in usefulness.casefold() for phrase in generic):
        raise GateError("specific usefulness must name a decision, question, experiment, or practice")

    trigger = item.get("decision_trigger")
    if not isinstance(trigger, dict):
        raise GateError("decision_trigger must contain act_when, monitor_when, and ignore_when")
    for key in ("act_when", "monitor_when", "ignore_when"):
        _require_text(trigger.get(key), f"decision_trigger.{key}", 18)

    _require_text(item.get("closest_analogue"), "closest_analogue", 10)
    _require_text(item.get("evidence_basis"), "evidence_basis", 16)


def recent_rotation_values(content_dir: Path, limit: int = 30, exclude_slug: str | None = None) -> dict[str, set[str]]:
    """Collect normalized titles from the most recent published editions."""
    recent: dict[str, set[str]] = {
        "techniques": set(), "books": set(), "foundations": set(), "framings": set()
    }
    paths = [
        path for path in sorted(content_dir.glob("*.json"), reverse=True)
        if path.stem != exclude_slug
    ][:limit]
    for path in paths:
        with path.open(encoding="utf-8") as handle:
            report = json.load(handle)
        mapping = (("technique", "techniques"), ("book", "books"), ("foundation", "foundations"))
        for section, bucket in mapping:
            title = report.get(section, {}).get("title")
            if title:
                recent[bucket].add(_norm(title))
        if report.get("title"):
            recent["framings"].add(_norm(report["title"]))
    return recent


def validate_weekly_report(report: dict[str, Any], recent: dict[str, set[str]]) -> None:
    """Validate a weekly dossier before it can enter the public site."""
    if report.get("edition_type") != "weekly_dossier":
        raise GateError("edition_type must be weekly_dossier")
    developments = report.get("developments")
    if not isinstance(developments, list) or not 2 <= len(developments) <= 4:
        raise GateError("weekly dossier must contain 2–4 developments")
    for item in developments:
        validate_candidate(item)

    technique_title = (report.get("technique") or {}).get("title")
    if not technique_title:
        raise GateError("technique title is required")
    if _norm(technique_title) in recent.get("techniques", set()):
        raise GateError("technique repeated within the rotation window")

    book_title = (report.get("book") or {}).get("title")
    foundation_title = (report.get("foundation") or {}).get("title")
    if bool(book_title) == bool(foundation_title):
        raise GateError("weekly dossier must include either one book or one foundation, not both")
    if book_title and _norm(book_title) in recent.get("books", set()):
        raise GateError("book repeated within the rotation window")
    if foundation_title and _norm(foundation_title) in recent.get("foundations", set()):
        raise GateError("foundation repeated within the rotation window")
    title = report.get("title")
    if title and _norm(title) in recent.get("framings", set()):
        raise GateError("central framing repeated within the rotation window")


def assert_no_private_leak(root: Path, profile: dict[str, Any]) -> None:
    """Fail if declared private markers appear in publishable text files."""
    markers = [m for m in profile.get("private_markers", []) if isinstance(m, str) and m.strip()]
    if not markers:
        return
    publishable: list[Path] = []
    for directory in ("content", "templates", "reports"):
        path = root / directory
        if path.exists():
            publishable.extend(p for p in path.rglob("*") if p.is_file() and p.suffix in {".json", ".html", ".md", ".txt"})
    for name in ("index.html", "archive.html", "reports.json"):
        path = root / name
        if path.exists():
            publishable.append(path)
    for path in publishable:
        text = path.read_text(encoding="utf-8", errors="ignore").casefold()
        for marker in markers:
            if marker.casefold() in text:
                raise GateError(f"private marker found in public file {path.relative_to(root)}")
