import json
from pathlib import Path

import pytest

from scripts.editorial_gates import (
    GateError,
    assert_no_private_leak,
    recent_rotation_values,
    validate_candidate,
    validate_weekly_report,
)


def strong_candidate(**overrides):
    item = {
        "title": "Outcome-linked pricing for agent workflows",
        "novelty_class": "meaningful_extension",
        "novelty_score": 3,
        "evidence_score": 3,
        "senior_pm_relevance_score": 3,
        "applicability_score": 3,
        "usefulness": "Changes how a PM chooses pricing units and gross-margin guardrails.",
        "decision_trigger": {
            "act_when": "Inference cost varies materially by customer workflow.",
            "monitor_when": "Usage is too low to estimate cost distributions.",
            "ignore_when": "The model cost is immaterial relative to contract value."
        },
        "closest_analogue": "Usage-based cloud infrastructure pricing",
        "evidence_basis": "Primary pricing data plus two independent customer cases"
    }
    item.update(overrides)
    return item


def test_candidate_requires_specific_usefulness_and_decision_trigger():
    item = strong_candidate(usefulness="PMs should pay attention")
    with pytest.raises(GateError, match="specific usefulness"):
        validate_candidate(item)


def test_old_or_recycled_candidate_is_rejected():
    with pytest.raises(GateError, match="old or recycled"):
        validate_candidate(strong_candidate(novelty_class="old_or_recycled"))


def test_rollout_requires_material_consequence():
    with pytest.raises(GateError, match="material consequence"):
        validate_candidate(strong_candidate(novelty_class="distribution_update"))
    validate_candidate(strong_candidate(
        novelty_class="distribution_update",
        material_consequence="Moves an established capability to the dominant enterprise distribution channel."
    ))


def test_candidate_rejects_weak_gate_score():
    with pytest.raises(GateError, match="evidence_score"):
        validate_candidate(strong_candidate(evidence_score=1))


def test_weekly_report_has_two_to_four_items_and_no_quota_filler():
    report = {
        "edition_type": "weekly_dossier",
        "developments": [strong_candidate(), strong_candidate(title="Second item")],
        "technique": {"title": "A technique"},
        "book": {"title": "A book"},
        "foundation": None
    }
    validate_weekly_report(report, recent={"techniques": set(), "books": set(), "foundations": set(), "framings": set()})
    report["developments"] *= 3
    with pytest.raises(GateError, match="2–4 developments"):
        validate_weekly_report(report, recent={"techniques": set(), "books": set(), "foundations": set(), "framings": set()})


def test_weekly_report_rejects_recent_book_or_foundation():
    report = {
        "edition_type": "weekly_dossier",
        "title": "A distinct framing",
        "developments": [strong_candidate(), strong_candidate(title="Second item")],
        "technique": {"title": "New technique"},
        "book": {"title": "Crossing the Chasm"},
        "foundation": None
    }
    recent = {
        "techniques": set(),
        "books": {"crossing the chasm"},
        "foundations": {"one-way and two-way doors"},
        "framings": set()
    }
    with pytest.raises(GateError, match="book repeated"):
        validate_weekly_report(report, recent=recent)


def test_weekly_report_requires_exactly_one_book_or_foundation():
    report = {
        "edition_type": "weekly_dossier",
        "title": "Distinct framing",
        "developments": [strong_candidate(), strong_candidate(title="Second item")],
        "technique": {"title": "New technique"},
        "book": {"title": "New book"},
        "foundation": {"title": "New foundation"}
    }
    recent = {"techniques": set(), "books": set(), "foundations": set(), "framings": set()}
    with pytest.raises(GateError, match="either one book or one foundation"):
        validate_weekly_report(report, recent=recent)
    report["foundation"] = None
    validate_weekly_report(report, recent=recent)


def test_rotation_values_read_last_thirty_editions(tmp_path: Path):
    content = tmp_path / "content"
    content.mkdir()
    for i in range(31):
        (content / f"2026-01-{i+1:02d}.json").write_text(json.dumps({
            "title": f"Framing {i}",
            "technique": {"title": f"Technique {i}"},
            "book": {"title": f"Book {i}"},
            "foundation": {"title": f"Foundation {i}"}
        }))
    recent = recent_rotation_values(content, limit=30)
    assert "book 0" not in recent["books"]
    assert "book 30" in recent["books"]
    assert len(recent["books"]) == 30


def test_rotation_values_can_exclude_current_edition(tmp_path: Path):
    content = tmp_path / "content"
    content.mkdir()
    (content / "2026-02-01.json").write_text(json.dumps({
        "title": "Earlier framing",
        "technique": {"title": "Earlier technique"},
        "book": {"title": "Earlier book"},
        "foundation": {"title": "Earlier foundation"}
    }))
    (content / "2026-02-08.json").write_text(json.dumps({
        "title": "Current framing",
        "technique": {"title": "Current technique"},
        "book": {"title": "Current book"},
        "foundation": {"title": "Current foundation"}
    }))
    recent = recent_rotation_values(content, limit=30, exclude_slug="2026-02-08")
    assert "current book" not in recent["books"]
    assert "earlier book" in recent["books"]


def test_private_profile_markers_cannot_appear_in_public_files(tmp_path: Path):
    public = tmp_path / "content"
    public.mkdir()
    (public / "safe.json").write_text('{"title":"Public research"}')
    profile = {"private_markers": ["Project Nightingale", "customer-alpha@example.com"]}
    assert_no_private_leak(tmp_path, profile)
    (public / "unsafe.json").write_text('{"note":"Project Nightingale"}')
    with pytest.raises(GateError, match="private marker"):
        assert_no_private_leak(tmp_path, profile)


def test_private_directory_is_ignored_by_git(tmp_path: Path):
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("private/\n")
    assert "private/" in gitignore.read_text().splitlines()


def test_report_template_renders_decision_trigger_labels():
    root = Path(__file__).resolve().parents[1]
    template = (root / "templates" / "report.html").read_text()
    assert "Act when" in template
    assert "Monitor when" in template
    assert "Ignore when" in template
    assert "{% if report.book %}" in template
    assert "{% if report.foundation %}" in template
    assert "Mondays · 7:00 AM PST" in template
    archive = (root / "templates" / "archive.html").read_text()
    assert "Mondays · 7:00 AM PST" in archive
