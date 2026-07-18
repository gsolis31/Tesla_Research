# Schema-Bound Append-Only Architecture (Grok #1)

## The Problem We Solved

### Old Architecture ("God-File Agent Loop")

```
Agent Loop (every /tesla-update run):
├─ Load 670-line skill file
├─ Load 167KB tesla-tracking-data.json (3,008 lines)
├─ Research all 9 categories
├─ Rewrite entire JSON file (free-form)
├─ Hope it didn't break
└─ Manual build + commit
```

**Problems**:
- 🔴 **Context cost grows with file**, not with delta ($0.15/run)
- 🔴 **Write errors only show up after deploy**
- 🔴 **New categories land in JSON but never surface** (schema drift)
- 🔴 **Can't parallelize** (merge is "overwrite monolith carefully")
- 🔴 **No resumability** (research failure corrupts data)
- 🔴 **Unbounded growth** (Cybercab: 30 keyPoints, 25 timeline events)

### New Architecture ("Schema-Bound Append-Only")

```
Research → findings/YYYY-MM-DD.json → Merge Script → tesla-tracking-data.json → Validate → Build → Deploy
   ↓
URL Cache (deduplication)
   ↓
Caps Applied (keyPoints: 15, timeline: 15)
```

**Benefits**:
- ✅ **87% less context** (10KB vs 167KB, $0.02/run)
- ✅ **Resumable** (research failures don't corrupt data)
- ✅ **Auditable** (see findings before merge)
- ✅ **Parallelizable** (multiple agents can write findings concurrently)
- ✅ **Testable** (merge logic separate from research)
- ✅ **Capped growth** (enforced limits on array sizes)
- ✅ **URL deduplication** (avoid re-analyzing same articles)

---

## Architecture Components

### 1. Findings Files (`findings/YYYY-MM-DD.json`)

**Lightweight intermediate artifacts** from research runs.

```json
{
  "date": "2026-07-08",
  "weekOf": "2026-07-07",
  "findings": {
    "keyChanges": [...],        // New developments
    "trends": [...],             // Trend observations
    "metrics": {                 // Metric updates (append-only)
      "cybercab": [...],
      "robotaxiFleet": [...],
      "jobPostings": [...]
    },
    "quarterlyData": [...],      // New P&D reports
    "categoryUpdates": {         // Category metadata
      "cybercab": {
        "criticalNews": "...",
        "newKeyPoint": "...",    // Single new point (merge applies cap)
        "newTimelineEvent": {...}
      }
    }
  },
  "metadata": {
    "sourcesSearched": [...],
    "urlsSeen": [...],           // For cache
    "researchDuration": "12m"
  }
}
```

**Schema**: `findings/schema.json` (JSON Schema for validation)

**Size**: ~5-10KB (vs 167KB main file)

### 2. Merge Script (`scripts/merge_findings.py`)

**Deterministic** script that takes findings → main data file.

```bash
python3 scripts/merge_findings.py findings/2026-07-08.json
```

**Operations**:
1. Load findings + current data
2. Merge keyChanges into weekly summaries
   - If same week → append
   - If new week → create at beginning
3. Append metric data points (deduplicated by date)
4. Add quarterly data (deduplicated by quarter)
5. Update category metadata
   - criticalNews (replace)
   - newKeyPoint (append + cap at 15)
   - newTimelineEvent (append + cap at 15)
6. Apply caps retrospectively (if `--apply-caps` flag)
7. Update lastUpdated
8. Validate result
9. Save

**Idempotent**: Can re-run safely (same inputs → same output)

**Caps**:
- `keyPoints`: Max 15 per category (FIFO)
- `timeline`: Max 15 events per category (FIFO)
- `weeklySummaries`: Max 52 weeks (rest archived)

### 3. URL Cache (`findings/url-cache.json`)

**Deduplication cache** to avoid re-analyzing seen URLs.

```json
{
  "urls": {
    "https://electrek.co/2026/07/01/...": {
      "firstSeen": "2026-07-01",
      "lastSeen": "2026-07-08",
      "category": "Cybercab Production",
      "title": "..."
    }
  },
  "stats": {
    "totalUrls": 247,
    "categoryCounts": {...}
  }
}
```

**Usage**:
```bash
# Check if URL seen
python3 scripts/url_cache.py check "<url>"

# Add URL
python3 scripts/url_cache.py add "<url>" "Category" "Title"

# Stats
python3 scripts/url_cache.py stats
```

**Normalization**:
- Lowercases domain
- Removes query params (except for specific domains)
- Removes trailing slashes

**Benefits**:
- Avoid duplicate keyChanges
- Save LLM tokens (don't re-analyze)
- Track research coverage

### 4. Updated Skill (`/tesla-update-v2`)

**Streamlined research skill** that uses new architecture.

**Changes from V1**:
- ✅ Only reads hot context (~10KB)
  - Last week's summary
  - Current metrics (latest counts)
  - Category criticalNews
- ✅ Emits findings file instead of rewriting JSON
- ✅ Checks URL cache before processing articles
- ✅ Runs merge script automatically
- ✅ Updates URL cache
- ✅ Archives old data
- ✅ Builds + commits automatically

**Hot Context Example**:
```python
# Instead of reading all 167KB:
data = json.load(open('tesla-tracking-data.json'))
last_week = data['weeklySummaries'][0]
cybercab_latest = data['metrics']['cybercab']['data'][-1]
robotaxi_latest = data['metrics']['robotaxiFleet']['data'][-1]
# Total: ~10KB
```

### 5. Schema Validation (Zod + Python)

**Already implemented in Grok #2**, now integrated:

- `src/schema.ts` - Zod schema (single source of truth)
- `scripts/validate_data.py` - Pre-build Python validation
- `findings/schema.json` - Findings format validation

**Validation flows**:
1. **Findings**: Validated against `findings/schema.json` before merge
2. **Merged data**: Validated by merge script (calls `validate_data.py`)
3. **Build**: Zod validation in `App.tsx` (runtime)
4. **CI**: GitHub Actions runs validation before deploy

---

## Data Flow

### New Update Cycle

```
1. Agent reads hot context (~10KB)
   ↓
2. Agent researches 9 categories
   - Checks URL cache for each URL
   - Skips seen URLs
   - Multi-source verification
   ↓
3. Agent emits findings/YYYY-MM-DD.json
   - Validate against findings/schema.json
   - If empty → skip merge
   ↓
4. Merge script runs
   - Load findings + current data
   - Merge deterministically
   - Apply caps
   - Validate result
   ↓
5. Update URL cache
   - Add all new URLs from findings
   ↓
6. Archive script runs
   - Move old data to archives/YYYY.json
   ↓
7. Build
   - npm run build (Zod validation)
   - Fail fast on errors
   ↓
8. Commit + push
   - findings/YYYY-MM-DD.json
   - tesla-tracking-data.json
   - findings/url-cache.json
   ↓
9. GitHub Actions deploy
   - Validate (Python)
   - Build (Zod)
   - Deploy to Pages
```

### Error Handling

**Research fails**:
- No findings file created
- Main data unchanged
- Can resume from where it failed

**Merge fails**:
- Findings file preserved
- Main data unchanged
- Fix merge logic + re-run

**Validation fails**:
- Build stops
- Deploy blocked
- Clear error messages

---

## Growth Caps (Enforced by Merge Script)

### Before Caps

```
Cybercab:
  keyPoints: 30 items (unbounded)
  timeline: 25 events (unbounded)

FSD:
  keyPoints: 23 items
  timeline: 20 events

Optimus:
  keyPoints: 25 items
  timeline: 21 events
```

**Growth rate**: ~2-3 items/month per category = exponential file growth

### After Caps

```
All categories:
  keyPoints: Max 15 (FIFO, keeps most recent)
  timeline: Max 15 (FIFO, keeps most recent)

Weekly summaries:
  Max 52 weeks in main file (rest archived)
```

**Growth rate**: Bounded at cap size (file size stable)

### Retrospective Caps

Run once to apply caps to existing data:

```bash
python3 scripts/merge_findings.py findings/YYYY-MM-DD.json --apply-caps
```

**Result**:
```
✓ Capped aiChip.keyPoints: 16 → 15
✓ Capped cybercab.keyPoints: 30 → 15
✓ Capped cybercab.timeline: 25 → 15
✓ Capped fsd.keyPoints: 23 → 15
✓ Capped fsd.timeline: 20 → 15
✓ Capped optimus.keyPoints: 25 → 15
✓ Capped optimus.timeline: 21 → 15
```

Old data moved to `archives/` automatically.

---

## Cost Analysis

### V1 (God-File Loop)

**Per /tesla-update run**:
- Input: 167KB JSON + 670-line skill = ~200KB context
- Research: 9 categories × 3 sources = 27 web searches
- Output: Rewrite 3,008-line JSON = ~167KB
- **Estimated cost**: ~$0.15/run

**Annual** (52 runs):
- $7.80/year in context costs alone
- Plus research tokens (variable)

### V2 (Schema-Bound)

**Per /tesla-update-v2 run**:
- Input: 10KB hot context + schema = ~15KB context
- Research: Same 27 searches, but cache reduces duplicates
- Output: Emit 5-10KB findings = ~8KB
- **Estimated cost**: ~$0.02/run

**Annual** (52 runs):
- $1.04/year in context costs
- **Savings**: 87% reduction

### Additional Savings

- **URL cache**: Reduces duplicate research (est. 20-30% savings)
- **Skip-early logic**: No merge if no news (saves build time)
- **Parallelization**: Can research categories concurrently (future)

---

## Migration Path

### Phase 1: Test V2 Alongside V1 ✅

- [x] Create findings schema
- [x] Create merge script
- [x] Create URL cache
- [x] Create `/tesla-update-v2` skill
- [x] Test merge with example findings
- [x] Apply caps to existing data

### Phase 2: Parallel Operation

- [ ] Run V2 for 2-3 weeks alongside V1
- [ ] Verify data quality
- [ ] Compare costs
- [ ] Monitor for edge cases

### Phase 3: Deprecate V1

- [ ] Mark `/tesla-update` as deprecated
- [ ] Update README to use V2
- [ ] Remove old skill file
- [ ] Archive V1 documentation

---

## File Structure

```
Research/
├── findings/                           # NEW: Intermediate artifacts
│   ├── schema.json                     # Findings format schema
│   ├── url-cache.json                  # Deduplication cache
│   ├── README.md                       # Findings documentation
│   └── YYYY-MM-DD.json                 # Daily findings files
├── scripts/
│   ├── merge_findings.py               # NEW: Deterministic merge
│   ├── url_cache.py                    # NEW: Cache management
│   ├── validate_data.py                # From Grok #2
│   └── archive_old_data.py             # Existing
├── .claude/skills/
│   ├── tesla-update/                   # V1 (deprecated)
│   └── tesla-update-v2/                # NEW: V2 skill
│       └── SKILL.md
├── src/
│   ├── schema.ts                       # From Grok #2
│   └── ...
├── tesla-tracking-data.json            # Main data file (managed by merge script)
└── archives/                           # Archived data by year
    └── YYYY.json
```

---

## Key Principles

### 1. Append-Only Writes

**Never overwrite**, only append:
- keyChanges → append to weekly summary
- Metrics → append data points (deduplicated)
- Quarterly data → append quarters (deduplicated)
- Category updates → append with caps

**Benefits**:
- No data loss
- Safer merges
- Easier to parallelize

### 2. Deterministic Merges

**Same inputs → same outputs**:
- No random ordering
- No timestamp-based logic (except for deduplication)
- Repeatable for testing

**Benefits**:
- Testable merge logic
- Can replay merges
- Easier debugging

### 3. Single Source of Truth

**Schema is the contract**:
- Zod schema defines structure
- TypeScript types generated from schema
- Findings validated against schema
- Merge enforces schema invariants

**Benefits**:
- No schema drift
- Type safety
- Clear contracts

### 4. Caps Prevent Unbounded Growth

**All arrays have limits**:
- keyPoints: 15
- timeline: 15
- weeklySummaries: 52

**Benefits**:
- Predictable file size
- Fast React renders
- Controlled bundle size

---

## Success Metrics

### Quantitative

- ✅ Context reduction: 167KB → 10KB (94%)
- ✅ Cost reduction: $0.15 → $0.02 (87%)
- ✅ Array caps applied: Cybercab 30→15, FSD 23→15, Optimus 25→15
- ✅ Schema validation: 3 layers (Python, Zod, TypeScript)

### Qualitative

- ✅ Research failures don't corrupt data
- ✅ Can test merge logic independently
- ✅ Can review findings before committing
- ✅ Can parallelize research (future)
- ✅ URL deduplication prevents waste

---

## Next Steps

### Immediate
1. Run `/tesla-update-v2` for next weekly update
2. Monitor for issues
3. Compare with V1 output quality

### Short-term
1. Build URL cache from historical keyChanges
2. Optimize research prompts for V2
3. Add parallel category research

### Long-term
1. Deprecate V1 skill
2. Add findings dashboard (view all research runs)
3. Implement multi-agent parallel research (Grok #3)

---

## Related Docs

- `VALIDATION_UPGRADE.md` - Grok #2 implementation
- `findings/README.md` - Findings directory documentation
- `.claude/skills/tesla-update-v2/SKILL.md` - V2 skill specification
- `findings/schema.json` - Findings format specification
