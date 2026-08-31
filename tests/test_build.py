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
