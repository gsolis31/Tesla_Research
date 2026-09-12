# Research Pipeline

Intermediate artifacts for `/tesla-update-v2` (and V1).

## Layout

```
research/
├── configs/          # Generated per-run configs (not hand-edited)
│   ├── research-config-{category}.json
│   ├── coverage-scout-config.json
│   └── curator-config.json
├── raw/              # Researcher outputs (gitignored)
│   └── findings-{category}.json
├── logs/             # Committed per-run audit trail
│   └── YYYY-MM-DD/
│       ├── {category}.json   # extracted searchLog
│       ├── lint-raw.json
│       ├── lint-curated.json
│       └── run.json
└── findings/         # Curated weekly packages + cache
    ├── YYYY-MM-DD.json
    ├── curator-report-YYYY-MM-DD.md
    ├── url-cache.json
    ├── schema.json
    ├── raw-schema.json
    └── README.md
```

## Flow

1. `python3 scripts/spawn_researcher.py --all` → `configs/`
2. Researcher agents write → `raw/findings-*.json` (must include `searchLog`)
   Coverage scout writes → `logs/YYYY-MM-DD/coverage.json` (does not write raw/)
3. `python3 scripts/lint_findings.py --raw --date YYYY-MM-DD --write-logs` → `logs/`
   (diffs scout vs researchers → `coverage-gaps.json`)
4. `python3 scripts/spawn_curator.py` → `configs/curator-config.json` (includes `coverageGaps`)
5. Curator writes → `findings/YYYY-MM-DD.json`
6. `python3 scripts/lint_findings.py --curated research/findings/YYYY-MM-DD.json --write-logs`
7. `python3 scripts/merge_findings.py research/findings/YYYY-MM-DD.json` → `data/tesla-tracking-data.json`
8. `python3 scripts/update_url_cache.py research/findings/YYYY-MM-DD.json`

Canonical paths live in `scripts/paths.py`.
