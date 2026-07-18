# Curated Findings

Validated weekly packages produced by the **tesla-curator** agent.

## Purpose

Researchers write category files under `research/raw/`. The curator merges, dedupes, and validates them into:

- `YYYY-MM-DD.json` — accepted keyChanges, trends, metrics, categoryUpdates
- `curator-report-YYYY-MM-DD.md` — validation summary
- `url-cache.json` — canonical article URLs for cross-run dedup
- `schema.json` — JSON Schema for findings format

The merge script (`scripts/merge_findings.py`) is the only writer of `data/tesla-tracking-data.json`.

## Pipeline

```
research/raw/findings-*.json
        ↓ curator
research/findings/YYYY-MM-DD.json
        ↓ merge_findings.py
data/tesla-tracking-data.json
        ↓ validate + npm run build
dist/
```

See `../README.md` and `../../scripts/paths.py` for the full layout.
