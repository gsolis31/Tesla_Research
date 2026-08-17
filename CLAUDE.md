# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Tesla Investor Tracking Dashboard — Developer Guide

**Project**: Tesla Investor Tracking Dashboard  
**Type**: React + TypeScript frontend + Python research pipeline  
**Purpose**: Automated tracking system for Tesla's key milestones across 9 categories (Cybercab Production, FSD Country Approvals, FSD v15 Software, Optimus Production, AI Chip Production, 4680 Battery Cell Production, Terafab In-House Chip Manufacturing, Job Postings, Vehicle Production & Delivery)  
**Live**: https://gsolis31.github.io/Tesla_Research/  
**Stack**: React 18, TypeScript, Vite, Tailwind, Chart.js, TradingView widget; Claude API agents for research  

---

## Quick Start

### Development

```bash
npm install
npm run dev          # http://localhost:5173
npm run build        # production build → dist/
npm run lint         # ESLint
npm test             # Python pytest (merge pipeline)
```

### Research Updates (Claude Code)

**Only path (all cases):**
```bash
/tesla-update-v2     # 12–15 min, ~$0.02/run
```

`/tesla-update` (V1) is retired — it bypassed the merge pipeline.

### Post-Research Finalization

After the curator writes `research/findings/YYYY-MM-DD.json`:

```bash
python3 scripts/finalize_update.py research/findings/YYYY-MM-DD.json
# chains: merge → url-cache → archive → python-validate → zod-validate → build
```

### Deployment

```bash
git add data/tesla-tracking-data.json research/findings/YYYY-MM-DD.json research/findings/url-cache.json
git commit -m "Update: …"
git push origin main # CI/CD: validate → build → GitHub Pages
# Note: dist/ is NOT committed — CI rebuilds it fresh
```

---

## Build, Lint, Test Commands

| Command | Purpose | Notes |
|---------|---------|-------|
| `npm run dev` | Local dev server | Vite, hot reload on `:5173` |
| `npm run build` | Production build | Runs `tsc -b` then `vite build` → `dist/` |
| `npm run lint` | ESLint check | Config: `.eslintrc.cjs` |
| `npm test` | Unit tests | `python3 -m pytest tests/` |
| `npm test:merge` | Merge logic tests only | `pytest tests/test_merge_findings.py` |
| `python3 scripts/validate_data.py` | Python validation | Structure, types, invariants, UI coverage |
| `npx tsx scripts/validate-zod-schema.ts` | Zod validation | Same schema as build-time check |
| `python3 -m pytest` | Full pytest suite | 3 test suites; `pytest.ini` in root |

**CI/CD Pipeline** (GitHub Actions on every push to `main`):
```
1. Checkout
2. Python unit tests (merge regressions)
3. Python validation (data structure + invariants)
4. Node setup (v20, npm cache)
5. npm ci (install)
6. Zod schema validation
7. npm run build (TypeScript + Vite)
8. Deploy to GitHub Pages
```

---

## High-Level Architecture

### What This Project Does

**Tesla Investor Tracking Dashboard** is a public-facing React web app + research pipeline that tracks 9 key Tesla business areas:

1. **Cybercab Production** — robotaxi fleet size, city launches, vehicle production
2. **FSD Country Approvals** — regulatory status, NHTSA/NTSB, EU homologation
3. **FSD v15 Software** — OTA versions, HW3/HW4 ceilings, training-mile milestones
4. **Optimus Production** — humanoid robot ramp, factory deployment
5. **AI Chip Production** — AI5/AI6 design, Samsung/TSMC foundry, Dojo
6. **4680 Battery Cell Production** — cell lines, yield, dry electrode, GWh
7. **Terafab In-House Chip Manufacturing** — fab site, JETI tax deals, permits
8. **Job Postings** — AI/robotics hiring signals
9. **Vehicle Production & Delivery** — quarterly P&D, IR consensus, market entries

**Dashboard Features**:
- Weekly summaries with sentiment (headline vs. reality)
- Interactive charts (production, deliveries, job postings, city breakdown)
- 9 category tabs with critical news, key points, timelines
- Robotaxi city-by-city status
- TradingView TSLA stock price widget

**Data Flow**:
```
Research Agents (Claude)
  ↓
research/findings/YYYY-MM-DD.json (weekly findings)
  ↓
Merge Script (Python, deterministic)
  ↓
data/tesla-tracking-data.json (source of truth, ~170KB)
  ↓
Validation (Python + Zod)
  ↓
npm run build (Vite + TypeScript)
  ↓
dist/ (GitHub Pages)
```

---

## Architecture: Three-Layer Design

### Layer 1: Research Pipeline (Python + Claude Agents)

**Purpose**: Collect, curate, and validate weekly findings.

**Components**:

1. **Agents** (`.claude/agents/`)
   - `tesla-researcher.md` — Researches one category; outputs `research/raw/findings-{category}.json`
   - `tesla-curator.md` — Deduplicates/validates findings; outputs `research/findings/YYYY-MM-DD.json`

2. **Config Generators** (`scripts/`)
   - `spawn_researcher.py` — Generates per-category research configs
   - `spawn_curator.py` — Generates curator config
   - `paths.py` — Canonical paths (import this, don't hardcode)

3. **Pipeline Orchestrators** (Skills in `.claude/skills/`)
   - `/tesla-update-v2` (PREFERRED) — Orchestrates batched parallel research + curator
   - `/tesla-update` (RETIRED) — Bypassed merge pipeline; tombstoned

4. **Merge & Validation** (`scripts/`)
   - `merge_findings.py` — Deterministic merge: findings → main data file
     - Append-only for metrics (no overwrites)
     - Caps: keyPoints ≤15, timeline ≤15, weeklySummaries ≤52
   - `finalize_update.py` — One command: merge → cache → archive → validate → build
   - `validate_data.py` — Python structure + business logic invariants
   - `url_cache.py` — Deduplication cache (canonical URLs only)
   - `archive_old_data.py` — Move old years to `data/archives/`

5. **Research Directory** (`research/`)
   ```
   research/
   ├── configs/          # Generated (gitignored — spawn_researcher.py, spawn_curator.py)
   ├── raw/              # Per-category findings (gitignored — researcher agent outputs)
   └── findings/         # Curated weekly packages (committed audit trail)
       ├── YYYY-MM-DD.json         # Curated findings (curator output)
       ├── curator-report-YYYY-MM-DD.md
       ├── url-cache.json          # Seen URLs (deduplication)
       └── schema.json             # Findings validation schema
   ```

**Key Pattern: Schema-Bound Append-Only Architecture**

- **Findings files** (~5–10KB) are lightweight intermediate artifacts
- **Merge script** is deterministic (same inputs → same output)
- **URL cache** deduplicates research (avoid re-analyzing same articles)
- **Growth caps** prevent unbounded array sizes (keyPoints, timeline, summaries)
- **Auditable**: See findings before merge; findings preserved after merge
- **Resumable**: Research failure doesn't corrupt main data
- **Cost**: 87% reduction vs. old "god-file" architecture ($0.15 → $0.02/run)

**Category Ownership** (prevents cross-researcher duplicates):
Each researcher has `owns` / `doesNotOwn` boundaries. Example:
- AI5 tape-out → `aiChip`, not `terafab`
- FSD OTA version → `fsdv15`, not `fsd`
- Robotaxi city launch → `cybercab`, not `fsd`

### Layer 2: Data Layer (JSON + Validation)

**Source of Truth**: `data/tesla-tracking-data.json` (~170KB)

**Schema** (`src/schema.ts` — Zod, single source of truth):
```typescript
{
  "lastUpdated": "2026-07-17",
  "weeklySummaries": [
    {
      "weekOf": "2026-07-13",
      "keyChanges": [
        {
          "title": "...",
          "description": "...",
          "date": "2026-07-13",
          "category": "Cybercab Production",
          "status": "positive|negative|neutral",
          "sentiment": {
            "headline": "...",
            "reality": "...",
            "confidence": "high|medium|low"
          },
          "evidence": {
            "positive_signals": ["..."],
            "negative_signals": ["..."],
            "key_metrics": { "actual": "...", "target": "...", "trajectory": "..." }
          },
          "source": "https://..."
        }
      ],
      "trends": ["..."]
    }
  ],
  "metrics": {
    "cybercab": {
      "title": "...",
      "data": [{ "date": "2026-07-17", "count": 160, "note": "..." }]
    },
    "robotaxiFleet": { ... },
    "robotaxiCities": {
      "cities": [
        {
          "name": "San Francisco",
          "status": "active|mapped",
          "serviceType": "unsupervised|mixed|safety-monitor-only",
          "activeVehicles": 45,
          "serviceArea": "...",
          "notes": "..."
        }
      ]
    },
    "jobPostings": { ... },
    ...
  },
  "categories": {
    "cybercab": {
      "categoryName": "Cybercab Production",
      "criticalNews": "...",
      "keyPoints": [{ "text": "..." }],
      "timeline": [{ "date": "2026-07-17", "event": "..." }]
    },
    ...  // 8 more categories
  }
}
```

**Growth Caps** (enforced by merge script):
- `keyPoints`: Max 15 per category (FIFO)
- `timeline`: Max 15 events per category (FIFO)
- `weeklySummaries`: Max 52 weeks in main file (rest archived to `data/archives/YYYY.json`)

**Validation Layers**:

1. **Python** (`scripts/validate_data.py`):
   - JSON parseable, required fields exist
   - Date formats (YYYY-MM-DD)
   - Status enums (positive/negative/neutral)
   - URLs valid
   - Invariants: weekly summaries reverse-chronological, no duplicates, metrics chronological
   - UI coverage: data rendered in React

2. **Zod** (`src/schema.ts`):
   - TypeScript types generated from schema
   - Runtime validation at build time
   - Same schema enforced in CI/CD

3. **Data Integrity**:
   - Merge script applies caps retrospectively
   - URL cache prevents duplicate research
   - Findings validated before merge
   - Result validated after merge

### Layer 3: UI Layer (React + TypeScript)

**Tech Stack**:
- React 18 (hooks, functional components)
- TypeScript 5.5
- Vite (dev server, build)
- Tailwind CSS (styling)
- Chart.js + react-chartjs-2 (charts)
- Zod (runtime validation)

**Components** (`src/components/`):

| Component | Purpose |
|-----------|---------|
| `App.tsx` | Root; loads data, tabs (Summary/Charts/Categories) |
| `WeeklySummary.tsx` | Displays keyChanges + sentiment + evidence for current week |
| `MetricsCharts.tsx` | Line charts: production, deliveries, job postings; filters by year/quarter |
| `Categories.tsx` | Tabs for 9 categories; displays criticalNews, keyPoints, timeline |
| `ProductionDelivery.tsx` | Quarterly P&D table, all-time totals, annual summary |
| `StockPriceTile.tsx` | Fetches TSLA price from Alpha Vantage API |
| `TradingViewWidget.tsx` | Embedded TradingView chart |

**Data Import**:
```typescript
import teslaDataRaw from '../data/tesla-tracking-data.json'

// Validate at build time
const validationResult = validateTeslaData(teslaDataRaw)
if (!validationResult.success) {
  console.error('Validation failed:', validationResult.errors)
  // Continue with fallback or exit
}
```

**Validation at Runtime**:
- Zod schema validation in `App.tsx`
- Fallback to unsafe cast if validation fails (non-blocking)
- Invariant checks (warns but doesn't crash)

---

## Project Structure

```
Research/
├── src/                              # React dashboard (Vite + TypeScript)
│   ├── App.tsx                       # Root component
│   ├── schema.ts                     # Zod schema (single source of truth)
│   ├── components/
│   │   ├── WeeklySummary.tsx
│   │   ├── MetricsCharts.tsx
│   │   ├── Categories.tsx
│   │   ├── ProductionDelivery.tsx
│   │   ├── StockPriceTile.tsx
│   │   └── TradingViewWidget.tsx
│   ├── types/index.ts                # Generated from schema.ts
│   ├── App.css
│   ├── index.css
│   └── main.tsx                      # Entry point
├── dist/                             # Production build (gitignored — CI builds fresh)
├── data/
│   ├── tesla-tracking-data.json      # Source of truth (170KB)
│   └── archives/
│       └── YYYY.json                 # Old years (≥2 years)
├── research/
│   ├── configs/                      # Gitignored — generated by spawn_researcher.py / spawn_curator.py
│   ├── raw/                          # Gitignored — per-category findings (researcher outputs)
│   ├── findings/                     # Curated weekly packages (committed audit trail)
│   │   ├── YYYY-MM-DD.json           # Curated findings (curator output)
│   │   ├── curator-report-YYYY-MM-DD.md
│   │   ├── url-cache.json            # Seen URLs (deduplication)
│   │   └── schema.json               # Findings validation schema
│   └── README.md                     # Pipeline documentation
├── scripts/
│   ├── paths.py                      # Canonical paths (import this)
│   ├── spawn_researcher.py           # Generate research configs
│   ├── spawn_curator.py              # Generate curator config
│   ├── finalize_update.py            # One command: merge → cache → archive → validate → build
│   ├── merge_findings.py             # Deterministic merge (ONLY script that writes main data)
│   ├── validate_data.py              # Python validation (structure + invariants)
│   ├── validate-zod-schema.ts        # Zod validation (CI/CD + pre-commit)
│   ├── url_cache.py                  # URL cache primitives
│   ├── update_url_cache.py           # Update cache from findings
│   └── archive_old_data.py           # Move old years to archives/
├── .claude/
│   ├── agents/
│   │   ├── tesla-researcher.md       # Research agent prompt
│   │   └── tesla-curator.md          # Curation agent prompt
│   └── skills/
│       ├── tesla-update/             # V1 skill (RETIRED — tombstoned)
│       └── tesla-update-v2/          # Batched skill (PREFERRED)
├── .github/
│   └── workflows/
│       └── deploy.yml                # CI/CD: test → validate → build → GitHub Pages
├── docs/
│   ├── SCHEMA_BOUND_ARCHITECTURE.md  # Grok #1: append-only design
│   ├── VALIDATION_UPGRADE.md         # Grok #2: Zod schema + validation
│   ├── PARALLEL_RESEARCH.md          # Grok #3: batched agents design
│   ├── CURATION_SUMMARY.md
│   └── tesla-investor-tracking.md
├── tests/
│   ├── conftest.py                   # Pytest fixtures
│   ├── test_merge_findings.py        # Merge logic regressions (3 suites)
│   └── README.md
├── package.json                      # Node dependencies + scripts
├── requirements.txt                  # Python runtime (anthropic, requests, beautifulsoup4)
├── requirements-dev.txt              # Python dev (pytest)
├── pytest.ini                        # Pytest config
├── vite.config.ts                    # Vite config (React plugin, relative base)
├── tsconfig.json, tsconfig.*.json    # TypeScript configs
├── postcss.config.js, tailwind.config.js
├── .gitignore
└── README.md                         # Project overview
```

---

## Key Patterns & Non-Obvious Decisions

### 1. Schema-Bound Append-Only Architecture (Grok #1)

**Problem Solved**: Old "god-file" loop read 167KB JSON + rewrote entire file on each update.

**Solution**:
- **Findings files** (~5–10KB) are ephemeral intermediates
- **Merge script** is deterministic (append-only, no overwrites for metrics)
- **URL cache** deduplicates research
- **Growth caps** prevent unbounded arrays
- **87% cost reduction** ($0.15 → $0.02/run)
- **Resumable**: Research failure → main data unchanged
- **Auditable**: See findings before merge

**Key Insight**: Main data file is only written by `merge_findings.py`. No agent writes directly. This ensures:
- Deterministic output (testable)
- No merge conflicts
- Clear audit trail
- Easy rollback

### 2. Zod Schema as Single Source of Truth (Grok #2)

**Problem Solved**: 5 conflicting schema definitions (types, JSON, UI, validation, agents).

**Solution**:
- `src/schema.ts` (Zod) is the canonical definition
- TypeScript types auto-generated via `z.infer<typeof Schema>`
- Python validates against same invariants
- Findings and main data both validated

**Key Insight**: Schema drift causes silent data bugs. By making schema the contract, we:
- Type-check at build time
- Validate at runtime (Zod)
- Prevent silent failures
- Know exactly what data shape the UI expects

### 3. Category Ownership Boundaries

**Problem Solved**: Cross-researcher duplicates (two agents research the same news).

**Solution**:
Each category has explicit `owns` and `doesNotOwn` boundaries. Example:
- AI5 tape-out → `aiChip` (owns "AI chip design/production"), not `terafab` (doesn't own "chip fabrication")
- FSD OTA version → `fsdv15` (owns "software versions"), not `fsd` (doesn't own "software"; owns "regulatory approvals")

**Key Insight**: This cuts duplicate research by forcing researchers to own specific aspects, not topics.

### 4. Sentiment System (Headline vs. Reality)

**Purpose**: Track whether headlines match underlying reality.

**Structure**:
```json
{
  "sentiment": {
    "headline": "positive|negative|neutral",  // What headlines say
    "reality": "positive|negative|neutral",   // What data shows
    "confidence": "high|medium|low",
    "rationale": "Why they differ (optional)"
  }
}
```

**Example**: Samsung AI5 tape-out news
- Headline: "positive" (foundry milestone reached)
- Reality: "neutral" (tape-out ≠ production; 2 years behind schedule)

**Key Insight**: This prevents headline-chasing. Investors see the underlying reality, not just what makes headlines.

### 5. Evidence System

**Purpose**: Provide structured signals behind each claim.

**Structure**:
```json
{
  "evidence": {
    "positive_signals": ["...", "..."],
    "negative_signals": ["...", "..."],
    "key_metrics": {
      "actual": "160 vehicles",
      "target": "1000 by 2027",
      "trajectory": "linear growth continuing"
    }
  }
}
```

**Key Insight**: By tracking both positive and negative signals, we avoid narrative bias. A story isn't "good" or "bad"—it has both sides, weighted by evidence.

### 6. Weekly Summaries (Reverse Chronological)

**Structure**: Latest week first (index 0).

```json
"weeklySummaries": [
  { "weekOf": "2026-07-13", "keyChanges": [...] },  // Latest
  { "weekOf": "2026-07-06", "keyChanges": [...] },
  ...
  { "weekOf": "2025-06-09", "keyChanges": [...] }   // Oldest (52 weeks back)
]
```

**Key Insight**: Reverse chronological order makes React rendering fast (just slice first N). Archive old data when you hit 52 weeks.

### 7. Metrics as Append-Only Time Series

**Structure**: Chronological order (oldest first), deduplicated by date.

```json
"metrics": {
  "cybercab": {
    "title": "Cybercab Production",
    "data": [
      { "date": "2026-01-15", "count": 50, "note": "..." },
      { "date": "2026-02-20", "count": 85, "note": "..." },
      ...
      { "date": "2026-07-17", "count": 160, "note": "..." }
    ]
  }
}
```

**Key Insight**: Append-only time series are:
- Immutable (no rewrites)
- Auditable (see exact history)
- Testable (merge is straightforward)
- Queryable (filter by date range)

### 8. Robotaxi Cities Breakdown

**Purpose**: Track per-city service status (not just fleet count).

```json
"robotaxiCities": {
  "cities": [
    {
      "name": "San Francisco",
      "status": "active",
      "serviceType": "unsupervised",
      "activeVehicles": 45,
      "launchDate": "2024-11-18",
      "serviceArea": "Selected neighborhoods",
      "notes": "Expanding to more areas"
    }
  ]
}
```

**Key Insight**: Fleet size alone is misleading. By tracking per-city status, we see:
- Where service actually runs
- Whether it's supervised or unsupervised
- Whether cities are expanding or contracting

### 9. Dual Validation (Python + Zod)

**Why two validators?**
- **Python** (`validate_data.py`): Runs pre-build; checks structure, dates, URLs, invariants
- **Zod** (`src/schema.ts`): Runs at build time (TypeScript) + runtime (Vite)

**Key Insight**: Double validation catches errors at different stages:
- Python catches data issues before you try to merge
- Zod catches schema mismatches before you ship

### 10. URL Cache (Canonical URLs Only)

**Purpose**: Avoid re-researching the same article.

**Implementation**:
```json
{
  "urls": {
    "https://electrek.co/2026/07/01/...": {
      "firstSeen": "2026-07-01",
      "lastSeen": "2026-07-08",
      "category": "Cybercab Production",
      "title": "Tesla Cybercab reaches 150 units"
    }
  }
}
```

**Normalization**:
- Lowercase domain
- Remove query params (except critical ones)
- Remove trailing slashes

**Key Insight**: Cache canonical URLs only (article URLs, not search/RSS). This avoids:
- Duplicate research (20–30% savings)
- Duplicate keyChanges (dedup happens at merge, not research time)
- Wasted tokens

---

## Data Flow: A Typical Update

### Week of 2026-07-08 (Tuesday update)

```
1. Spawn Config
   python3 scripts/spawn_researcher.py --all
   → research/configs/research-config-{category}.json (9 files)
   → research/configs/curator-config.json

2. Research (Parallel agents via /tesla-update-v2 skill)
   tesla-researcher (category 1) → research/raw/findings-cybercab.json
   tesla-researcher (category 2) → research/raw/findings-fsd.json
   ... (9 categories, with URL cache checks)
   
   Each researcher:
   - Loads hot context (~2KB: last week summary, latest metrics)
   - Checks URL cache before processing each URL
   - Outputs findings-{category}.json (~2KB)

3. Curation
   tesla-curator:
   - Loads 9 × findings-{category}.json
   - Deduplicates by (title, category)
   - Sentiment-corrects sugar-coated claims
   - Rejects weak Electrek-only claims
   - Outputs research/findings/2026-07-08.json (~10KB)

4. Merge
   python3 scripts/merge_findings.py research/findings/2026-07-08.json
   - Load findings + tesla-tracking-data.json
   - Merge keyChanges into weekly summary
   - Append metrics (deduplicated by date)
   - Update categories (cap at 15 keyPoints, 15 timeline)
   - Apply caps (if --apply-caps flag)
   - Validate result
   - Save tesla-tracking-data.json

5. Update URL Cache
   python3 scripts/update_url_cache.py research/findings/2026-07-08.json
   - Add all URLs from findings to cache
   - Update category counts

6. Archive Old Data
   python3 scripts/archive_old_data.py
   - If weeklySummaries > 52: move oldest years to data/archives/YYYY.json
   - Keep current + previous year in main file

7. Validate
   python3 scripts/validate_data.py
   npx tsx scripts/validate-zod-schema.ts

8. Build
   npm run build
   → dist/ (Zod validation at build time)

9. Commit & Push
   git add research/findings/2026-07-08.json \
            research/findings/url-cache.json \
            data/tesla-tracking-data.json
   git commit -m "Update: 2026-07-08 research (Cybercab +2, FSD +1, Optimus +0)"
   git push origin main

10. GitHub Actions Deploy
    - Checkout
    - pytest (merge regressions)
    - python3 validate_data.py
    - npm ci
    - npx tsx validate-zod-schema.ts
    - npm run build
    - Deploy dist/ to GitHub Pages
    → Live at https://gsolis31.github.io/Tesla_Research/
```

---

## Testing

### Unit Tests

```bash
npm test              # Full pytest suite
npm test:merge        # Merge logic only
```

**Tests** (`tests/test_merge_findings.py`):
- **Suite 1**: Merge determinism (same inputs → same output)
- **Suite 2**: Growth caps (15 keyPoints max, 15 timeline max)
- **Suite 3**: Deduplication (title + category)

**Test Data**:
- `tests/conftest.py` — Fixtures for sample data
- Mock findings files with various scenarios

**Key Insight**: Merge logic is deterministic and testable. You can replay any merge offline.

---

## Validation Strategy

### Pre-Build (Python)

```bash
python3 scripts/validate_data.py
```

Checks:
- ✅ JSON parseable
- ✅ Required fields exist (lastUpdated, weeklySummaries, metrics, categories)
- ✅ Date formats (YYYY-MM-DD)
- ✅ Status enums (positive/negative/neutral)
- ✅ URLs are valid URLs
- ✅ Invariants:
  - weeklySummaries in reverse chronological order
  - No duplicate weeks
  - metrics in chronological order
  - Category names match known categories
- ✅ UI coverage (warns if data exists but doesn't render)

Exit code: 0 (pass) or 1 (fail)

### Build-Time (Zod)

```bash
npm run build
```

Runs TypeScript type checking + Zod validation:
- Loads `src/schema.ts`
- Validates `data/tesla-tracking-data.json` against schema
- Fails fast if validation fails
- Produces `dist/` only if validation passes

### CI/CD (GitHub Actions)

On every push to `main`:
1. `python3 -m pytest` — Merge regression tests
2. `python3 scripts/validate_data.py` — Python validation
3. `npm ci` — Install (reproducible)
4. `npx tsx scripts/validate-zod-schema.ts` — Zod validation
5. `npm run build` — TypeScript + Vite
6. Deploy `dist/` to GitHub Pages

---

## Documentation

| Doc | Topic |
|-----|--------|
| `README.md` | Project overview, quick start, live dashboard link |
| `docs/SCHEMA_BOUND_ARCHITECTURE.md` | Grok #1: append-only design, cost analysis, migration |
| `docs/VALIDATION_UPGRADE.md` | Grok #2: Zod schema, validation layers, what was fixed |
| `docs/PARALLEL_RESEARCH.md` | Grok #3: parallel batched research (not active) |
| `docs/CURATION_SUMMARY.md` | Curation guidelines |
| `research/README.md` | Research pipeline layout |

---

## Common Tasks

### Add a New Weekly Summary Manually

```python
python3 -c "
import json
from datetime import datetime

data = json.load(open('data/tesla-tracking-data.json'))
data['weeklySummaries'].insert(0, {
    'weekOf': '2026-07-20',
    'keyChanges': [],
    'trends': []
})
data['lastUpdated'] = datetime.now().strftime('%Y-%m-%d')
json.dump(data, open('data/tesla-tracking-data.json', 'w'), indent=2)
"
```

### Apply Caps to Existing Data

```bash
python3 scripts/merge_findings.py research/findings/2026-07-08.json --apply-caps
```

### Archive Old Years

```bash
python3 scripts/archive_old_data.py
# Moves data > 2 years old to data/archives/YYYY.json
```

### Check URL Cache

```bash
python3 scripts/url_cache.py check "https://electrek.co/2026/07/..."
python3 scripts/url_cache.py stats
```

### Lint & Format

```bash
npm run lint
# ESLint rules in .eslintrc.cjs
```

### Debug Merge Issues

```bash
# Re-run merge with detailed output
python3 scripts/merge_findings.py research/findings/2026-07-08.json

# Check result
cat data/tesla-tracking-data.json | jq '.weeklySummaries[0]'
```

---

## Dependencies

### Runtime (Node)

- `react` — UI framework
- `react-dom` — React DOM rendering
- `chart.js` — Charting library
- `react-chartjs-2` — React wrapper for Chart.js
- `chartjs-plugin-datalabels` — Labels on chart data

### Dev (Node)

- `typescript` — Type checking
- `vite` — Build tool
- `@vitejs/plugin-react` — Vite React plugin
- `@types/react`, `@types/react-dom` — Type definitions
- `tailwindcss` — CSS framework
- `autoprefixer` — CSS prefixer
- `postcss` — CSS processor
- `eslint` — Linter
- `zod` — Schema validation
- `tsx` — TypeScript executor

### Runtime (Python)

- `anthropic` — Claude API (for agents)
- `requests` — HTTP client
- `beautifulsoup4` — HTML parsing

### Dev (Python)

- `pytest` — Test runner

---

## Environment & Deployment

### Environment Variables

None required for development (data is static JSON).

For research agents (via `/tesla-update-v2` skill):
- `ANTHROPIC_API_KEY` — Set by Claude Code

### Deployment

Every push to `main`:
1. GitHub Actions runs CI/CD workflow
2. Validation passes → build succeeds
3. `dist/` deployed to GitHub Pages
4. Live at https://gsolis31.github.io/Tesla_Research/

---

## Troubleshooting

### Build Fails: "Validation failed"

```
npm run build
→ ❌ Zod validation error
```

**Fix**: Run pre-build validation to see the issue:
```bash
python3 scripts/validate_data.py
npx tsx scripts/validate-zod-schema.ts
```

### Merge Fails: "Duplicate week"

```
python3 scripts/merge_findings.py research/findings/2026-07-08.json
→ ❌ Week 2026-07-08 already exists
```

**Fix**: Check if you're re-running the same findings. Merge is idempotent, so re-running same inputs is safe.

### Unit Tests Fail

```bash
npm test
→ ❌ test_merge_findings.py::test_caps_keypoints FAILED
```

**Fix**: Check if you changed the cap values. If you did:
1. Update `MAX_KEY_POINTS` in `scripts/merge_findings.py`
2. Update test expectations in `tests/test_merge_findings.py`

### GitHub Pages Deployment Blocked

Check GitHub Actions for errors:
- Go to https://github.com/gsolis31/Tesla_Research/actions
- Click the failed workflow
- Read the error logs (usually "Validation failed")

---

## References

- **Live Dashboard**: https://gsolis31.github.io/Tesla_Research/
- **GitHub Repo**: https://github.com/gsolis31/Tesla_Research/
- **GitHub Actions**: https://github.com/gsolis31/Tesla_Research/actions
- **Data Source**: `data/tesla-tracking-data.json` (170KB, hand-curated)
- **Schema**: `src/schema.ts` (Zod, single source of truth)

---

**Last Updated**: 2026-07-18  
**Project Type**: Personal research + public dashboard  
**License**: Educational and investment tracking (not financial advice)
