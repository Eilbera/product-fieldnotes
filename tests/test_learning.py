import copy
import json
from pathlib import Path

import hashlib
import subprocess
from html.parser import HTMLParser
from urllib.parse import urlsplit

import pytest
from jinja2 import Environment, FileSystemLoader, select_autoescape

from scripts.build import load_reports
from scripts.editorial_gates import GateError

ROOT = Path(__file__).resolve().parents[1]


def learning_report():
    example = {
        "kind": "hypothetical", "label": "Hypothetical worked example",
        "situation": "A team is choosing an onboarding approach.",
        "input": "The test uses a realistic invitation and a prototype.",
        "alternatives": "Compare a guided flow with a direct invitation.",
        "decision": "Test the invitation before implementing the full flow.",
        "artifact": "Decision record: keep the guided option for another test.",
        "limitations": "These are invented teaching inputs, not measured outcomes."
    }
    return {
        "edition_type": "learning_edition", "schema_version": 2,
        "slug": "2026-09-12-learning", "date": "September 12, 2026",
        "title": "Learn before building", "dek": "Three lessons for product judgment.",
        "reading_time": "10 min read", "topics": ["Discovery"],
        "editor_note": "General PM learning, not personalized advice.",
        "coverage_note": "No frontier item selected. Books and foundations have separate tracks.",
        "practice": {
            "title": "Test the difficult assumption", "learning_objective": "Separate test problems from product problems.",
            "evidence_type": "practitioner_self_report",
            "problem": "The prototype test confuses the participants.[1]",
            "old_approach": "The team revised labels before changing the test.[1]",
            "method": [{"title": "Change the setting", "body": "Observe the same task outside the confusing test setup.[1]"}],
            "evidence": "A practitioner describes changing the testing environment.[1]",
            "limitations": "The case does not establish a causal effect on revenue.",
            "worked_example": copy.deepcopy(example), "source_ids": [1]
        },
        "book": {
            "title": "A recent book", "author": "An author", "publication_date": "2025-02-07",
            "access_basis": "Author description only; the full book was not accessed.",
            "thesis": "Business outcomes matter more than process compliance.[1]",
            "ideas": [{"title": "Name the outcome", "body": "Make the business goal explicit before selecting work.[1]"}],
            "critique": "The description cannot establish the quality of the case studies.",
            "audience": "Product leaders deciding whether to sample the book.",
            "verdict": "Sample first", "verdict_reason": "Inspect a chapter before buying copies for the team.",
            "source_ids": [1]
        },
        "foundation": {
            "title": "Compare value with cost", "original": "Value and cost belong in the same decision.[1]",
            "misuse": "A preferred metric cannot stand in for every business result.",
            "worked_example": copy.deepcopy(example), "source_ids": [1]
        },
        "sources": [{"id": 1, "title": "Primary source", "url": "https://example.com/research"}]
    }


def load_one(tmp_path, report):
    (tmp_path / '2026-09-12-learning.json').write_text(json.dumps(report))
    return load_reports(tmp_path)[0]


def test_learning_edition_needs_no_vendor_news_and_keeps_both_tracks(tmp_path):
    report = load_one(tmp_path, learning_report())
    assert report['book'] and report['foundation']
    env = Environment(loader=FileSystemLoader(ROOT / 'templates'), autoescape=select_autoescape(['html']))
    html = env.get_template('report.html').render(report=report, base='../')
    assert 'Practice lesson' in html
    assert 'Hypothetical worked example' in html
    assert 'Author description only' in html
    assert 'Decision record: keep the guided option' in html
    assert 'Frontier developments' not in html
    assert 'href="#source-1"' in html


@pytest.mark.parametrize('section,key,match', [
    ('book', 'access_basis', 'access_basis'),
    ('book', 'publication_date', 'publication_date'),
    ('practice', 'evidence_type', 'evidence_type'),
    ('practice', 'method', 'method'),
    ('practice', 'source_ids', 'source_ids'),
    ('foundation', 'worked_example', 'worked_example'),
])
def test_learning_rejects_missing_editorial_basis(tmp_path, section, key, match):
    report = learning_report()
    del report[section][key]
    with pytest.raises(GateError, match=match):
        load_one(tmp_path, report)


@pytest.mark.parametrize('section', ['practice', 'foundation'])
def test_hypothetical_examples_require_visible_label(tmp_path, section):
    report = learning_report()
    report[section]['worked_example']['label'] = 'Actual customer results'
    with pytest.raises(GateError, match='hypothetical'):
        load_one(tmp_path, report)


def test_learning_rejects_unknown_inline_citation(tmp_path):
    report = learning_report()
    report['practice']['evidence'] += ' Missing source.[99]'
    with pytest.raises(GateError, match='citation'):
        load_one(tmp_path, report)


@pytest.mark.parametrize('section', ['practice', 'developments'])
@pytest.mark.parametrize('metadata', [False, True], ids=['singleton-source-ids', 'metadata-citation'])
def test_learning_rejects_missing_inline_citations(tmp_path, section, metadata):
    report = learning_report()
    if section == 'practice':
        # Remove prose references without changing the singleton source_ids list.
        references = report['practice'].pop('source_ids')
        item = json.loads(json.dumps(report['practice']).replace('[1]', ''))
        item['source_ids'] = references
        report['practice'] = item
    else:
        item = {key: 'An explained frontier development.' for key in
                ('title', 'new', 'not_new', 'pm_consequence', 'evidence', 'limitations')}
        item['source_ids'] = [1]
        report['developments'] = [item]
    if metadata:
        item['research_notes'] = 'Unrendered source note.[1]'
    with pytest.raises(GateError, match='citation IDs must match source_ids'):
        load_one(tmp_path, report)


def test_learning_rejects_missing_topics(tmp_path):
    report = learning_report()
    del report['topics']
    with pytest.raises(GateError, match='topics'):
        load_one(tmp_path, report)


@pytest.mark.parametrize('topics', [None, 'Discovery', {}, 1, [], [''], ['  '], [1], [None], ['Discovery', '']])
def test_learning_rejects_invalid_or_empty_topics(tmp_path, topics):
    report = learning_report()
    report['topics'] = topics
    with pytest.raises(GateError, match='topics'):
        load_one(tmp_path, report)


def test_learning_rejects_duplicate_source_ids(tmp_path):
    report = learning_report()
    report['sources'] *= 2
    with pytest.raises(GateError, match='source IDs'):
        load_one(tmp_path, report)


def test_learning_applies_readability_backstop(tmp_path):
    report = learning_report()
    report['book']['critique'] = ' '.join(['word'] * 33) + '.'
    with pytest.raises(ValueError, match='33 words'):
        load_one(tmp_path, report)


def test_learning_frontier_requires_prior_art_not_scores(tmp_path):
    report = learning_report()
    report['developments'] = [{'title': 'A release with no demonstrated learning'}]
    with pytest.raises(GateError, match='frontier'):
        load_one(tmp_path, report)


def test_learning_rotation_includes_practice(tmp_path):
    from scripts.editorial_gates import recent_rotation_values
    load_one(tmp_path, learning_report())
    assert 'test the difficult assumption' in recent_rotation_values(tmp_path)['techniques']


@pytest.mark.parametrize('slug', ['../../private/leak', 'bad slug', '2026-99-99'])
def test_learning_slug_cannot_escape_report_directory(tmp_path, slug):
    report = learning_report()
    report['slug'] = slug
    with pytest.raises(GateError, match='slug'):
        load_one(tmp_path, report)


def test_learning_can_publish_without_a_book(tmp_path):
    report = learning_report()
    report['book'] = None
    assert load_one(tmp_path, report)['book'] is None


def test_learning_rotation_respects_earlier_editions_only(tmp_path):
    from scripts.editorial_gates import recent_rotation_values
    for slug in ['2026-01-01', '2026-02-01', '2026-03-01']:
        (tmp_path / f'{slug}.json').write_text(json.dumps({'book': {'title': slug}}))
    assert recent_rotation_values(tmp_path, exclude_slug='2026-02-01')['books'] == {'2026 01 01'}


def test_past_editions_render_identically():
    expected = {
        '2026-08-28': '10af7deeff755b7cce44a0b4b751f76fcf16c26e787286fe20d33ad7915993cd',
        '2026-08-31': '9d5c433a848334132afa2747adf63b4af7f4e891f8245ca00a35c15c19b11fe4',
        '2026-09-07': '027ec0c7b2d629ba4472ec70db8e25b85dd535ab6a2329f0603e46123ed94d50',
    }
    env = Environment(loader=FileSystemLoader(ROOT / 'templates'), autoescape=select_autoescape(['html', 'xml']), trim_blocks=True, lstrip_blocks=True)
    for slug, digest in expected.items():
        report = json.loads((ROOT / 'content' / f'{slug}.json').read_text())
        html = env.get_template('report.html').render(report=report, base='../')
        assert hashlib.sha256(html.encode()).hexdigest() == digest


def test_real_private_directory_is_ignored_and_untracked():
    ignored = subprocess.run(['git', 'check-ignore', 'private/ellie-profile.json'], cwd=ROOT, capture_output=True, text=True)
    assert ignored.returncode == 0
    tracked = subprocess.run(['git', 'ls-files', 'private'], cwd=ROOT, capture_output=True, text=True, check=True)
    assert not tracked.stdout.strip()


def test_learning_template_escapes_untrusted_prose():
    report = learning_report()
    report['practice']['problem'] = '<script>alert(1)</script>[1]'
    env = Environment(loader=FileSystemLoader(ROOT / 'templates'), autoescape=select_autoescape(['html']))
    html = env.get_template('report.html').render(report=report, base='../')
    assert '<script>alert(1)</script>' not in html
    assert '&lt;script&gt;' in html


def test_generated_site_has_no_missing_local_assets_or_anchors():
    class Links(HTMLParser):
        def __init__(self):
            super().__init__()
            self.links = []
            self.ids = set()
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if 'id' in attrs:
                self.ids.add(attrs['id'])
            self.links.extend(attrs[key] for key in ('src', 'href') if key in attrs)
    pages = [ROOT / 'index.html', ROOT / 'archive.html', *sorted((ROOT / 'reports').glob('*.html'))]
    for page in pages:
        parser = Links()
        parser.feed(page.read_text())
        for link in parser.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            if url.path:
                assert (page.parent / url.path).resolve().is_file(), (page, link)
            elif url.fragment:
                assert url.fragment in parser.ids, (page, link)


def test_empty_book_track_requires_coverage_explanation(tmp_path):
    report = learning_report()
    report['book'] = None
    report['coverage_note'] = ''
    with pytest.raises(GateError, match='coverage_note'):
        load_one(tmp_path, report)
