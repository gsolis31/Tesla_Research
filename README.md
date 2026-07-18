# Tesla Investor Tracking Dashboard

An automated tracking system for Tesla's key milestones across AI chips, autonomy, robotics, batteries, and production. Built with React + TypeScript; researched and updated via Claude skills (`/tesla-update-v2` preferred).

![Dashboard Preview](https://img.shields.io/badge/Status-Active-success)
![Last Updated](https://img.shields.io/badge/Updated-2026--07--17-blue)
[![Deployed](https://img.shields.io/badge/Live-GitHub%20Pages-brightgreen)](https://gsolis31.github.io/Tesla_Research/)

## What This Tracks

**9 categories** (dashboard tabs + weekly keyChanges):

1. **Cybercab Production** — robotaxi fleet, city launches, Cybercab manufacturing
2. **FSD Country Approvals** — regulatory approvals, NHTSA/NTSB, EU homologation
3. **FSD v15 Software** — OTA versions, HW3/HW4 ceilings, training-mile milestones
4. **Optimus Production** — humanoid ramp, factory deployment
5. **AI Chip Production** — AI5/AI6, Samsung/TSMC, Dojo (chip design/foundry — not fab politics)
6. **4680 Battery Cell Production** — cell lines, yield, dry electrode, GWh
7. **Terafab Manufacturing** — fab site, JETI tax deals, permits (not chip tape-outs)
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

### Research update (Claude Code)

**Preferred (batched, ~12–15 min):**

```bash
/tesla-update-v2
```

**Simpler sequential (low-news weeks):**

```bash
/tesla-update
```

V2 pipeline:
1. Generates configs under `research/configs/`
2. Spawns 9 researchers in 3 batches → `research/raw/findings-*.json`
3. Curator validates/dedupes/sentiment-corrects → `research/findings/YYYY-MM-DD.json`
4. Merges into `data/tesla-tracking-data.json`
5. Updates URL cache (canonical article URLs only)
6. Archives old years, validates, builds, **commits and pushes**

## Project Structure

```
Research/
├── src/                         # React dashboard (Vite + TypeScript)
├── dist/                        # Production build (GitHub Pages)
├── data/
│   ├── tesla-tracking-data.json # Live tracking data (source of truth)
│   └── archives/                # Year archives of old metrics/summaries
├── research/
│   ├── configs/                 # Generated research-config-*.json + curator-config
│   ├── raw/                     # Per-category findings-{category}.json
│   └── findings/                # Curated YYYY-MM-DD.json, reports, url-cache, schema
├── scripts/
│   ├── paths.py                 # Canonical paths (import this; don't hardcode)
│   ├── spawn_researcher.py      # → research/configs/
│   ├── spawn_curator.py         # → research/configs/curator-config.json
│   ├── merge_findings.py        # curated findings → data/
│   ├── validate_data.py         # Python structure + invariants
│   ├── validate-zod-schema.ts   # CI Zod check
│   ├── update_url_cache.py      # Canonical article URLs only
│   ├── url_cache.py             # Cache primitives + noise filters
│   └── archive_old_data.py      # → data/archives/
├── docs/                        # Architecture notes (see below)
├── .claude/
│   ├── agents/                  # tesla-researcher, tesla-curator
│   └── skills/                  # tesla-update-v2 (preferred), tesla-update, …
├── .github/workflows/deploy.yml # Validate → build → GitHub Pages
├── package.json
└── README.md
```

All script paths go through `scripts/paths.py` so layout stays consistent.

## How Updates Work (V2)

```
spawn_researcher.py --all
        ↓
research/configs/research-config-*.json
        ↓
9× tesla-researcher (3 batches of 3)
        ↓
research/raw/findings-{category}.json
        ↓
spawn_curator.py + tesla-curator
        ↓
research/findings/YYYY-MM-DD.json
        ↓
merge_findings.py → data/tesla-tracking-data.json
        ↓
update_url_cache.py · archive_old_data.py · validate · npm run build
        ↓
git commit + push → GitHub Actions deploys Pages
```

### Quality gates built into the pipeline

| Gate | What it does |
|------|----------------|
| **Category ownership** | Each researcher has `owns` / `doesNotOwn` (e.g. AI5 tape-out → aiChip, not terafab; FSD OTA → fsdv15, not fsd) |
| **Curator** | Dedupes vs last week + URL cache; auto-corrects sugar-coated sentiment; rejects weak Electrek-only claims |
| **Canonical URL cache** | Only article source URLs are cached (no search pages, RSS, homepages) |
| **Dual validation** | Python `validate_data.py` + Zod `src/schema.ts` (CI + build) |

## Technical Stack

**Frontend:** React 18, TypeScript, Vite, Tailwind, Chart.js, TradingView  
**Data:** JSON source of truth (`data/tesla-tracking-data.json`), imported directly by Vite  
**Research:** Claude agents + Python merge/validate scripts  
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
  → python3 scripts/validate_data.py
  → npx tsx scripts/validate-zod-schema.ts
  → npm ci && npm run build
  → deploy dist/ to GitHub Pages
```

Live: https://gsolis31.github.io/Tesla_Research/  
Actions: https://github.com/gsolis31/Tesla_Research/actions

```bash
npm run build
git add data/ research/ dist/   # typical research update paths
git commit -m "Update: …"
git push origin main
```

## Validation & Maintenance

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
| [docs/DEAD_FILES.md](docs/DEAD_FILES.md) | Obsolete workflows / cleanup notes |

## Contributing

Personal research project; issues and corrections welcome (data fixes, bugs, category ideas).

## License

Personal research project for educational and investment tracking. Not financial advice — verify with official sources.

## Credits

- **Research pipeline:** Claude agents (tesla-researcher / tesla-curator) + `/tesla-update-v2`
- **Dashboard:** React + TypeScript + Tailwind
- **Deploy:** GitHub Actions + GitHub Pages

---

**Last data update:** 2026-07-17 · [Live dashboard](https://gsolis31.github.io/Tesla_Research/)
