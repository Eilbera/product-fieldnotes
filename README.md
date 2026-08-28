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

GitHub Pages serves the `main` branch from the repository root. The daily Hermes publishing cron updates the content, runs the build, verifies the output, commits, and pushes.
