import json
from pathlib import Path
import subprocess
import sys

import pytest

from scripts.build import load_reports
from scripts.editorial_gates import GateError


def test_build_rejects_invalid_weekly_dossier(tmp_path: Path):
    content = tmp_path / "content"
    content.mkdir()
    report = {
        "slug": "2026-09-07",
        "date": "September 7, 2026",
        "title": "Weak weekly dossier",
        "dek": "A dossier that should not publish.",
        "reading_time": "8 min read",
        "topics": ["Strategy"],
        "edition_type": "weekly_dossier",
        "developments": [],
        "technique": {"title": "New technique", "source_ids": []},
        "book": {"title": "New book", "source_ids": []},
        "foundation": {"title": "New foundation", "source_ids": []},
        "sources": []
    }
    (content / "2026-09-07.json").write_text(json.dumps(report))
    with pytest.raises(GateError, match="2–4 developments"):
        load_reports(content_dir=content)


def test_direct_build_command_works_from_repository_root():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/build.py"],
        cwd=root,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
    assert "Built" in result.stdout


def test_build_accepts_weekly_dossier_with_book_and_no_foundation(tmp_path: Path):
    content = tmp_path / "content"
    content.mkdir()
    candidate = {
        "title": "A material development",
        "novelty_class": "meaningful_extension",
        "novelty_score": 3,
        "evidence_score": 3,
        "senior_pm_relevance_score": 3,
        "applicability_score": 3,
        "usefulness": "Changes how a senior PM allocates capacity across a constrained portfolio.",
        "decision_trigger": {
            "act_when": "A measurable constraint blocks a strategic outcome.",
            "monitor_when": "The constraint has not yet affected delivery or economics.",
            "ignore_when": "The change is cosmetic and has no decision consequence."
        },
        "closest_analogue": "Constraint-based portfolio management",
        "evidence_basis": "Primary evidence with an independent operating case",
        "source_ids": [1]
    }
    report = {
        "slug": "2026-09-07",
        "date": "September 7, 2026",
        "title": "A useful weekly dossier",
        "dek": "A valid weekly dossier.",
        "reading_time": "10 min read",
        "topics": ["Strategy"],
        "edition_type": "weekly_dossier",
        "developments": [candidate, {**candidate, "title": "A second material development"}],
        "technique": {"title": "A new technique", "source_ids": [1]},
        "book": {"title": "A new book", "source_ids": [1]},
        "foundation": None,
        "sources": [{"id": 1, "title": "Primary source", "url": "https://example.com"}]
    }
    (content / "2026-09-07.json").write_text(json.dumps(report))
    loaded = load_reports(content_dir=content)
    assert loaded[0]["book"]["title"] == "A new book"
    assert loaded[0]["foundation"] is None
