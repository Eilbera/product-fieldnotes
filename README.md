# Product Fieldnotes

A static editorial archive for senior product-management intelligence reports.

## Build

```bash
python scripts/build.py
```

The build validates cited source IDs, renders every JSON edition under `reports/`, updates the latest edition at `index.html`, and rebuilds `archive.html`.

## Content

Add one JSON file per edition under `content/YYYY-MM-DD.json`. Keep images under `assets/images/` and use analytically useful, attributed media only.

## Deployment

GitHub Pages serves the `main` branch from the repository root. Build and verify locally, then commit and push authorized public changes. Scheduler configuration is managed separately.

## Learning editions

Use `edition_type: learning_edition` with `schema_version: 2` for new learning reports. Practice, books, and foundations have separate tracks. Frontier developments are optional, with no vendor-news quota. See [EDITORIAL.md](EDITORIAL.md) for fields, selection rules, evidence labels, and publication checks.

The complete pilot is `content/2026-09-12-learning.json`, rendered at `reports/2026-09-12-learning.html`. Earlier editions keep their existing schema and URLs.

```bash
.venv/bin/python -m pytest tests/ -q
.venv/bin/python scripts/build.py
```

Research queues, source captures, citation ledgers, and reader context remain under the Git-ignored `private/` directory. Never force-add that directory.
