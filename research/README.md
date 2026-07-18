# Research Pipeline

Intermediate artifacts for `/tesla-update-v2` (and V1).

## Layout

```
research/
├── configs/          # Generated per-run configs (not hand-edited)
│   ├── research-config-{category}.json
│   └── curator-config.json
├── raw/              # Researcher outputs (one file per category)
│   └── findings-{category}.json
└── findings/         # Curated weekly packages + cache
    ├── YYYY-MM-DD.json
    ├── curator-report-YYYY-MM-DD.md
    ├── url-cache.json
    ├── schema.json
    └── README.md
```

## Flow

1. `python3 scripts/spawn_researcher.py --all` → `configs/`
2. Researcher agents write → `raw/findings-*.json`
3. `python3 scripts/spawn_curator.py` → `configs/curator-config.json`
4. Curator writes → `findings/YYYY-MM-DD.json`
5. `python3 scripts/merge_findings.py research/findings/YYYY-MM-DD.json` → `data/tesla-tracking-data.json`
6. `python3 scripts/update_url_cache.py research/findings/YYYY-MM-DD.json`

Canonical paths live in `scripts/paths.py`.
