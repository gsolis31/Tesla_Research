# Research run logs

Committed audit trail for `/tesla-update-v2`. `research/raw/` stays gitignored; this directory is what we keep.

Each run writes `research/logs/YYYY-MM-DD/`:

| File | Source | Purpose |
|---|---|---|
| `{category}.json` | extracted from raw `searchLog` | queries, fetches, skips, metric rejects |
| `coverage.json` | tesla-coverage-scout | independent candidate list (not findings) |
| `coverage-gaps.json` | `lint_findings.py --raw` | scout stories no researcher filed or considered |
| `lint-raw.json` | `lint_findings.py --raw` | mechanical errors/warnings per category |
| `lint-curated.json` | `lint_findings.py --curated` | gates that must be clean before merge |
| `run.json` | both lint passes | per-agent status, coverage gaps, curator totals |

`run.json` `agents.*.status`:

- `ok` — filed ≥1 keyChange, no lint errors
- `empty` — quiet week with `skipReason` + queries
- `lint_error` — mechanical reject (registration-as-fleet, missing searchLog, …)
- `missing` — no `research/raw/findings-{category}.json`

`run.json` `coverage.status`:

- `ok` — scout ran; `gaps` are unmatched stories for the curator
- `missing` — no `coverage.json` (scout failed or skipped; week still proceeds)
- `invalid` — `coverage.json` did not parse

Do not hand-edit these files. Re-run `python3 scripts/lint_findings.py --raw|--curated --write-logs`.
