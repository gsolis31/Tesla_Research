# Tesla Curator Agent - Usage Guide

## Overview

Quality gate agent that validates and merges category findings from multiple researchers.

**What it does:**
- ✅ Deduplicates keyChanges (vs last week + URL cache)
- ✅ Validates sentiment matches reality (catches sugar-coating)
- ✅ Normalizes category names, dates, confidence levels
- ✅ Refuses weak single-source claims (e.g., Electrek-only)
- ✅ Merges metrics and category updates
- ✅ Outputs final validated `findings/YYYY-MM-DD.json`

**One curator brain sees the full picture** → better than 9 isolated researchers.

---

## Quick Start

### 1. Run Researchers First

Make sure you have category findings:

```bash
ls findings-*.json
# Should see: findings-cybercab.json, findings-fsd.json, etc.
```

If not, run researchers first:
```bash
python3 scripts/spawn_researcher.py --all
# Then spawn tesla-researcher agents
```

### 2. Generate Curator Config

```bash
python3 scripts/spawn_curator.py
# Or specify date:
python3 scripts/spawn_curator.py 2026-07-08
```

This creates `curator-config.json` with:
- List of all findings-*.json files
- Last week's keyChanges (for deduplication)
- URL cache path
- Date and weekOf

### 3. Spawn Curator

Use the `/tesla-curator` skill:

```
Curate research findings using curator-config.json
```

The agent will:
1. Load all category findings
2. Deduplicate vs last week + URL cache
3. Validate sentiment (fix sugar-coating)
4. Refuse weak claims
5. Normalize data
6. Extract trends
7. Merge metrics
8. Write `findings/YYYY-MM-DD.json`
9. Write `findings/curator-report-YYYY-MM-DD.md`

**Expected outputs:**
```
findings/2026-07-08.json          # Validated findings
findings/curator-report-2026-07-08.md  # What was fixed
```

---

## What the Curator Fixes

### 1. Deduplication

**Removes:**
- Duplicates vs last week (same title + category)
- Already-cached URLs
- Duplicates within this week (same title + category from different researchers)

**Example:**
```
Before: 12 keyChanges
After:  9 keyChanges (removed 3 duplicates)
```

### 2. Sentiment Validation

**Catches sugar-coating:**
- Status = "positive" but reality = "negative" → Auto-corrects to "negative"
- Status = "positive" but reality = "neutral" → Warns
- More negative signals than positive but status = "positive" → Warns

**Example fix:**
```
Before:
  title: "Robotaxi expands to Miami"
  status: "positive"
  sentiment.headline: "positive"
  sentiment.reality: "negative"

After:
  status: "negative"  ← Auto-corrected to match reality
```

### 3. Weak Claims Rejection

**Refuses:**
- Electrek-only with low confidence
- Insufficient evidence (<2 signals total)
- Too vague (lots of "possibly", "maybe", "could")

**Example:**
```
Rejected:
  title: "Optimus could possibly ship in 2027"
  source: electrek.co
  confidence: low
  reason: electrek_only_low_confidence
```

### 4. Normalization

**Ensures consistency:**
- Category names match standard list
- Dates in YYYY-MM-DD format
- Confidence in (high, medium, low)
- Status in (positive, negative, neutral)

---

## Curator Report

After curation, check the report:

```bash
cat findings/curator-report-2026-07-08.md
```

**Example report:**
```
======================================================================
Tesla Curator - Validation Report
======================================================================

Date: 2026-07-08
Week of: 2026-07-06

[1/4] Category Findings Loaded
✓ 9 categories researched
✓ 12 keyChanges collected

[2/4] Deduplication
✓ Removed 3 duplicates
  - 2 vs last week
  - 1 already cached
  - 0 within week

[3/4] Sentiment Validation
✓ 2 sentiment corrections applied
⚠ 1 warnings

[4/4] Quality Filter
✓ Rejected 1 weak claims
  - 1 Electrek-only
  - 0 insufficient evidence
  - 0 too vague

======================================================================
✓ CURATION COMPLETE: 8 validated keyChanges
======================================================================
```

---

## Validation Rules

### Sentiment Validation

**Rule 1: Status must match reality, not headline**

```python
if status != reality:
    if status == 'positive' and reality == 'negative':
        # ERROR: Auto-correct
        status = 'negative'
    elif status == 'positive' and reality == 'neutral':
        # WARN: Might be OK
        log_warning()
```

**Rule 2: Evidence must support status**

```python
if negative_signals > positive_signals and status == 'positive':
    # WARN: Consider downgrading
    log_warning("More negatives than positives but still positive")
```

### Weak Claims Rejection

**Rule 1: No Electrek-only low-confidence claims**
```python
if 'electrek.co' in source and confidence == 'low':
    reject("electrek_only_low_confidence")
```

**Rule 2: Minimum evidence threshold**
```python
if len(positive_signals) + len(negative_signals) < 2:
    reject("insufficient_evidence")
```

**Rule 3: Too vague**
```python
vague_words = ['possible', 'maybe', 'could', 'might', 'potentially']
if vague_count >= 3 and confidence == 'low':
    reject("too_vague")
```

---

## Testing

**Test curator with real data:**

1. Generate findings (if you haven't):
```bash
# Use existing findings from last run
ls findings-*.json
```

2. Generate curator config:
```bash
python3 scripts/spawn_curator.py
```

3. Manually invoke curator:
```
Curate research findings using curator-config.json
```

4. Check outputs:
```bash
# See what was curated
cat findings/2026-07-08.json | jq '.findings.keyChanges[] | {title, status, reality: .sentiment.reality}'

# Check curator report
cat findings/curator-report-2026-07-08.md

# Verify no sugar-coating
cat findings/2026-07-08.json | jq '.findings.keyChanges[] | select(.status != .sentiment.reality)'
# Should be empty or only neutral/positive mismatches (acceptable)
```

---

## Integration with Pipeline

**Full parallel pipeline:**

```bash
# Step 1: Generate all research configs
python3 scripts/spawn_researcher.py --all

# Step 2: Spawn 9 tesla-researcher agents in parallel
# (via Task tool or orchestrator)

# Step 3: Wait for all researchers to complete
# Result: 9 findings-*.json files

# Step 4: Generate curator config
python3 scripts/spawn_curator.py

# Step 5: Spawn tesla-curator agent
# (via Task tool)

# Step 6: Wait for curator to complete
# Result: findings/YYYY-MM-DD.json

# Step 7: Run merge + deploy scripts
python3 scripts/merge_findings.py findings/YYYY-MM-DD.json
python3 scripts/validate_data.py
npm run build
git add . && git commit && git push
```

---

## Cost & Performance

**Execution:**
- Time: 2-3 min (serial, quality over speed)
- Cost: ~$0.02 (Sonnet for quality)
- Model: Always use Sonnet (quality matters for validation)

**Trade-offs:**
- Could use Haiku to save $0.01, but quality might suffer
- Sentiment validation needs good reasoning
- Worth paying for Sonnet here

---

## Error Handling

**Missing category findings:**
- Warns but continues with available findings
- Notes in metadata which categories were skipped

**Empty findings:**
- Writes findings with skipReason
- Valid outcome, not an error

**URL cache missing:**
- Creates empty cache structure
- Proceeds without dedup (safer than failing)

**Sentiment validation fails:**
- Auto-corrects ERROR-level issues
- Logs WARN-level issues but doesn't block

---

## Next Steps After Curation

After curator completes:

1. **Review findings:**
```bash
cat findings/2026-07-08.json | jq
```

2. **Review curator report:**
```bash
cat findings/curator-report-2026-07-08.md
```

3. **If findings look good, run merge:**
```bash
python3 scripts/merge_findings.py findings/2026-07-08.json
```

4. **Validate merged data:**
```bash
python3 scripts/validate_data.py
```

5. **Build and deploy:**
```bash
npm run build
git add tesla-tracking-data.json findings/2026-07-08.json
git commit -m "Update: Parallel research for 2026-07-08"
git push origin main
```

---

## Comparison: Curator vs. Manual Review

| Task | Without Curator | With Curator |
|------|----------------|--------------|
| Deduplication | Manual (error-prone) | Automatic (reliable) |
| Sentiment validation | Miss sugar-coating | Catches + fixes |
| Weak claims | Might slip through | Filtered out |
| Normalization | Inconsistent | Consistent |
| Time | 10-15 min manual review | 2-3 min automated |
| Quality | Depends on reviewer | Deterministic rules |

**ROI**: Curator saves 10-15 min per run + improves quality.

---

## Troubleshooting

**No findings-*.json files:**
- Run tesla-researcher agents first
- Check they completed successfully

**Curator rejects all keyChanges:**
- Check if evidence is too weak
- Review curator report for reasons
- Adjust researcher quality if needed

**Sentiment corrections seem wrong:**
- Review the specific keyChange
- Check evidence.negative_signals vs positive_signals
- File issue if curator is wrong

**Missing metrics in output:**
- Check if researchers found metric updates
- Verify findings-{category}.json has metricUpdate
- Some categories don't have metrics (normal)

---

## Next: Build Orchestrator

Now that we have:
1. ✅ tesla-researcher (parallel category research)
2. ✅ tesla-curator (validate + merge)

We need:
3. ⏳ **Orchestrator** (spawns researchers → waits → spawns curator → runs scripts)

The orchestrator ties it all together into one command.
