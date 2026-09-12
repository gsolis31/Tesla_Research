# Curated Findings

Validated weekly packages produced by the **tesla-curator** agent.

## Purpose

Researchers write category files under `research/raw/`. The coverage scout writes `research/logs/YYYY-MM-DD/coverage.json` (not findings). Lint extracts `searchLog` and diffs the scout list into `coverage-gaps.json`. The curator merges, dedupes, addresses gaps, and validates them into:

- `YYYY-MM-DD.json` — accepted keyChanges, trends, metrics, categoryUpdates
- `curator-report-YYYY-MM-DD.md` — validation summary
- `url-cache.json` — canonical article URLs for cross-run dedup
- `schema.json` — JSON Schema for curated findings
- `raw-schema.json` — JSON Schema for researcher output (`searchLog` required)

The merge script (`scripts/merge_findings.py`) is the only writer of `data/tesla-tracking-data.json`.

## Pipeline

```
research/raw/findings-*.json
        ↓ lint_findings.py --raw → research/logs/YYYY-MM-DD/
        ↓ curator
research/findings/YYYY-MM-DD.json
        ↓ lint_findings.py --curated
        ↓ merge_findings.py
data/tesla-tracking-data.json
        ↓ validate + npm run build
dist/
```

See `../README.md` and `../../scripts/paths.py` for the full layout.
