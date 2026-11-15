# Tesla Investor Tracking Dashboard

An automated tracking system for Tesla's key milestones across AI chips, autonomy, robotics, batteries, and production. Built with React + TypeScript; researched and updated with `/tesla-update-v2`.

![Dashboard Preview](https://img.shields.io/badge/Status-Active-success)
[![Deployed](https://img.shields.io/badge/Live-GitHub%20Pages-brightgreen)](https://gsolis31.github.io/Tesla_Research/)

## What This Tracks

**9 categories** (dashboard tabs + weekly keyChanges):

1. **Cybercab Production** — robotaxi fleet, city launches, Cybercab manufacturing
2. **FSD Country Approvals** — regulatory approvals, NHTSA/NTSB, EU homologation
3. **FSD v15 Software** — OTA versions, HW3/HW4 ceilings, training-mile milestones
4. **Optimus Production** — humanoid ramp, factory deployment
5. **AI Chip Production** — AI5/AI6, Samsung/TSMC, Dojo (chip design/foundry — not fab politics)
6. **4680 Battery Cell Production** — cell lines, yield, dry electrode, GWh
7. **Terafab In-House Chip Manufacturing** — fab site, JETI tax deals, permits (not chip tape-outs)
8. **Job Postings** — AI/robotics/Optimus hiring signals
9. **Vehicle Production & Delivery** — quarterly P&D, IR consensus, market entries

**Also:**
- Robotaxi fleet metrics and city breakdown
- Weekly summaries with headline vs reality sentiment
- Interactive charts + TradingView TSLA widget

## Quick Start

### Live dashboard

**https://gsolis31.github.io/Tesla_Research/**

### Local development

```bash
npm install
npm run dev          # http://localhost:5173
npm run build        # production → dist/
```

### Research update

**Only path (all cases):**

```bash
/tesla-update-v2
```

That run researches, curates, and finalizes. The finalize step is:

```bash
python3 scripts/finalize_update.py research/findings/YYYY-MM-DD.json
```

V2 pipeline:
1. `spawn_researcher.py --all` archives leftover raw files, then writes configs under `research/configs/` (gitignored)
2. Nine researchers and the coverage scout run together. Researchers use `web_search` (about 6 searches) then `web_fetch`. Raw output is `research/raw/findings-*.json` (gitignored; must include `searchLog`). Scout output is `research/logs/YYYY-MM-DD/coverage.json`
3. `lint_findings.py --raw` → `research/logs/YYYY-MM-DD/` (committed; diffs scout vs researchers)
4. `spawn_curator.py` copies the raw files into a draft. The curator judges close calls (coverage gaps, sentiment, cache hits, metric basis) → `research/findings/YYYY-MM-DD.json`
5. `finalize_update.py` chains: lint-curated → merge → url-cache → archive → validate (Python + Zod) → build

## Project Structure

```
Research/
├── src/                         # React dashboard (Vite + TypeScript)
├── dist/                        # Production build (gitignored — CI builds fresh)
├── data/
│   ├── tesla-tracking-data.json # Live tracking data (source of truth)
│   └── archives/                # Year archives of old metrics/summaries
├── research/
│   ├── configs/                 # Gitignored — generated research-config-*.json + curator-config
│   ├── raw/                     # Gitignored — per-category findings-{category}.json
│   ├── logs/                    # Committed per-run searchLog, lint, run.json
│   └── findings/                # Curated YYYY-MM-DD.json, reports, url-cache, schema
├── scripts/
│   ├── paths.py                 # Canonical paths (import this; don't hardcode)
│   ├── spawn_researcher.py      # slim configs (titles + seenUrls) → research/configs/
│   ├── assemble_findings.py     # raw files → curated draft + curator review list
│   ├── spawn_curator.py         # writes the draft, then curator-config (review, not the URL cache)
│   ├── lint_findings.py         # Mechanical quality gate + run ledger
│   ├── finalize_update.py       # lint-curated → merge → cache → archive → validate → build
│   ├── merge_findings.py        # curated findings → data/
│   ├── validate_data.py         # Python structure + invariants
│   ├── validate-zod-schema.ts   # Zod check (finalize + CI)
│   ├── update_url_cache.py      # Canonical article URLs only
│   ├── url_cache.py             # Cache primitives + noise filters
│   └── archive_old_data.py      # → data/archives/
├── docs/                        # Architecture notes (see below)
├── .claude/
│   ├── agents/                  # tesla-researcher, tesla-coverage-scout, tesla-curator
│   └── skills/                  # tesla-update-v2 (preferred), tesla-update (retired)
├── .github/workflows/deploy.yml # Validate → build → GitHub Pages
├── package.json
└── README.md
```

All script paths go through `scripts/paths.py` so layout stays consistent.

## How Updates Work (V2)

```
spawn_researcher.py --all   # archives leftover raw files, writes configs
        ↓
9× tesla-researcher + tesla-coverage-scout   # one wave
        ↓
research/raw/findings-{category}.json
research/logs/YYYY-MM-DD/coverage.json
        ↓
lint_findings.py --raw → research/logs/YYYY-MM-DD/
        ↓
spawn_curator.py   # assembles the draft
tesla-curator      # edits the close calls
        ↓
research/findings/YYYY-MM-DD.json
        ↓
finalize_update.py   # curated lint, merge, cache, archive, validate, build
        ↓
git commit + push → GitHub Actions deploys Pages
```

### Quality gates built into the pipeline

| Gate | What it does |
|------|----------------|
| **Category ownership** | Each researcher has `owns` / `doesNotOwn` (e.g. AI5 tape-out → aiChip, not terafab; FSD OTA → fsdv15, not fsd) |
| **searchLog + run ledger** | Every researcher records queries/skips; `research/logs/YYYY-MM-DD/run.json` shows ok / empty / lint_error / missing |
| **Coverage scout** | Independent news sweep. Lint diffs it against the 9 researchers; unmatched items become curator `coverageGaps` |
| **lint_findings.py** | Deterministic gates (registration-as-fleet, stale dates, Electrek-only, ownership trespass). Gold evals in `tests/evals/` |
| **Assemble** | Copies raw keyChanges and metrics into the draft. Drops lint errors, exact duplicates, and registry counts filed as fleet or production. Lists cache hits; does not delete them |
| **Curator** | Judges the review list: sentiment flips, cache hits, coverage gaps, weak claims, trend wording |
| **Canonical URL cache** | Only article source URLs are cached (no search pages, RSS, homepages) |
| **Dual validation** | Python `validate_data.py` + Zod `src/schema.ts` (CI + build) |

## Technical Stack

**Frontend:** React 18, TypeScript, Vite, Tailwind, Chart.js, TradingView  
**Data:** JSON source of truth (`data/tesla-tracking-data.json`), imported directly by Vite  
**Research:** Grok agents + Python assemble/merge/validate scripts  
**Deploy:** GitHub Actions → GitHub Pages on every push to `main`

## Dashboard Features

### Charts & Metrics
- Production & delivery (filter by year/quarter)
- Cybercab production and robotaxi fleet series
- Job postings trend
- City-by-city robotaxi status

### Weekly Summary
- Key changes with status (positive / negative / neutral)
- Headline vs reality sentiment + evidence signals
- Source links

### Categories
Tabs for all nine categories (including **FSD v15 Software**): critical news, key points, timeline where applicable.

## Data Sources

**Tier 1 (primary):**
- [Tesla IR](https://ir.tesla.com) — official production/delivery
- [Teslarati](https://teslarati.com), [TeslaNorth](https://teslanorth.com), [Tesla Oracle](https://teslaoracle.com)
- [Basenor](https://basenor.com), [Optimusk Blog](https://optimusk.blog), [Not a Tesla App](https://www.notateslaapp.com)
- [Robotaxi Tracker](https://robotaxitracker.com) — fleet deployment

**Tier 2 (corroboration only — never sole source):**
- [Electrek](https://electrek.co), InsideEVs, etc.

## Deployment

Every push to `main`:

```
push main
  → pip install -r requirements-dev.txt && python3 -m pytest
  → python3 scripts/validate_data.py
  → npm ci
  → npx tsx scripts/validate-zod-schema.ts
  → npm run build
  → deploy dist/ to GitHub Pages
```

Live: https://gsolis31.github.io/Tesla_Research/  
Actions: https://github.com/gsolis31/Tesla_Research/actions

```bash
git add data/tesla-tracking-data.json \
        research/findings/YYYY-MM-DD.json \
        research/findings/curator-report-YYYY-MM-DD.md \
        research/findings/url-cache.json \
        research/logs/YYYY-MM-DD
git commit -m "Update: Research for YYYY-MM-DD"
git push origin main
```

## Validation & Maintenance

### Local pre-commit (slim)

One-time per clone (also runs on `npm install` via `prepare`):

```bash
npm run hooks:install
# or: bash scripts/install_hooks.sh
```

Every `git commit` then runs `python3 -m pytest` when pytest is installed.

`finalize_update.py` is the one local pass for lint, data validation, Zod, and the production build. GitHub Actions runs those again, plus the tests, before the site updates. Bypass the hook: `git commit --no-verify`.

### Manual checks

```bash
# Structure + invariants + UI coverage
python3 scripts/validate_data.py

# Zod schema (same as CI)
npx tsx scripts/validate-zod-schema.ts

# Unit tests (merge logic regressions — no network)
python3 -m pytest
# or: npm test

# Keep only current + previous year in main file
python3 scripts/archive_old_data.py

# Cache article URLs from a curated findings file
python3 scripts/update_url_cache.py research/findings/YYYY-MM-DD.json

# Optional: strip non-canonical URLs from cache
python3 scripts/update_url_cache.py --prune
```

## Docs

| Doc | Topic |
|-----|--------|
| [docs/SCHEMA_BOUND_ARCHITECTURE.md](docs/SCHEMA_BOUND_ARCHITECTURE.md) | Findings → merge → main data |
| [docs/VALIDATION_UPGRADE.md](docs/VALIDATION_UPGRADE.md) | Python + Zod validation |
| [docs/PARALLEL_RESEARCH.md](docs/PARALLEL_RESEARCH.md) | Parallel / batched research design |
| [research/README.md](research/README.md) | Pipeline folder layout |

## Contributing

Personal research project; issues and corrections welcome (data fixes, bugs, category ideas).

## License

Personal research project for educational and investment tracking. Not financial advice — verify with official sources.

## Credits

- **Research pipeline:** Grok agents (tesla-researcher, tesla-coverage-scout, tesla-curator) + `/tesla-update-v2`
- **Dashboard:** React + TypeScript + Tailwind
- **Deploy:** GitHub Actions + GitHub Pages
