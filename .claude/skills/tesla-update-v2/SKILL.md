---
name: tesla-update-v2
description: Schema-bound append-only Tesla research skill (Grok #1 architecture)
user-invocable: true
allowed-tools: WebSearch, Read, Write, Bash
---

# Tesla Tracker Update Skill V2 (Schema-Bound)

## What Changed from V1

**Old workflow** (god-file agent loop):
- Agent reads 167KB JSON + 670-line skill
- Agent rewrites entire 3,008-line JSON file
- Build + commit manually

**New workflow** (schema-bound append-only):
- Agent reads last week's summary + current metrics (~10KB)
- Agent emits lightweight `findings/YYYY-MM-DD.json` (~5-10KB)
- Merge script updates main file deterministically
- Auto-validate → build → commit

**Benefits**:
- ✅ **80% less context** (10KB vs 167KB)
- ✅ **Resumable** (research failures don't corrupt data)
- ✅ **Auditable** (see what was found before merge)
- ✅ **Testable** (merge logic separate from research)
- ✅ **Caps enforced** (keyPoints/timeline limited to 15 items)

---

## Execution Steps

### Step 1: Determine Research Period

```python
from datetime import datetime
import json

# Load current data to get last update date
data = json.load(open('/Users/gonzalosolis/Research/tesla-tracking-data.json'))
last_updated = data['lastUpdated']  # e.g., "2026-07-03"
today = datetime.now().strftime('%Y-%m-%d')

# Calculate Monday of current week
from datetime import timedelta
now = datetime.now()
monday = now - timedelta(days=now.weekday())
week_of = monday.strftime('%Y-%m-%d')

print(f"Research period: {last_updated} → {today}")
print(f"Week of: {week_of}")
```

### Step 2: Read Hot Context Only

**DO NOT** read the entire JSON file. Only read:

1. **Last week's summary** (to avoid duplicate keyChanges)
```python
last_week = data['weeklySummaries'][0] if data['weeklySummaries'] else None
```

2. **Current metrics** (latest counts)
```python
cybercab_latest = data['metrics']['cybercab']['data'][-1] if data['metrics']['cybercab']['data'] else None
robotaxi_latest = data['metrics']['robotaxiFleet']['data'][-1]
job_postings_latest = data['metrics']['jobPostings']['data'][-1]
```

3. **Category criticalNews** (current state)
```python
category_news = {
    cat: data['categories'][cat]['criticalNews']
    for cat in data['categories']
    if cat != 'productionDelivery'
}
```

**Total context**: ~10KB vs 167KB in V1

### Step 3: Research (Multi-Source Search)

Follow the same multi-source search protocol from V1:

**Tier 1 Sources** (primary - use these first):
- Teslarati (teslarati.com)
- TeslaNorth (teslanorth.com)
- Tesla Oracle (teslaoracle.com)
- Basenor (basenor.com)
- Optimusk Blog (optimusk.blog)
- Official Tesla (tesla.com, ir.tesla.com)

**Tier 2 Sources** (supplementary - reference only):
- Electrek (electrek.co) - known anti-Tesla bias, use ONLY for confirmation

**Specialized Sources**:
- Robotaxi Tracker (robotaxitracker.com) - fleet deployment
- Official IR (ir.tesla.com/press) - quarterly reports

**For EACH of the 9 categories**:
1. Search 2-3 Tier 1 sources with targeted queries
2. Cross-reference findings
3. Check Electrek for additional context (don't rely on it alone)
4. For robotaxi: ALWAYS check robotaxitracker.com
5. For P&D: ALWAYS check ir.tesla.com/press

**Important**: Use the URL cache to avoid re-analyzing seen articles:
```bash
python3 scripts/url_cache.py check "<url>"
# Exit code 0 = seen before, 1 = new URL
```

### Step 4: Emit Findings File

**DO NOT** edit `tesla-tracking-data.json` directly.

Instead, create `findings/YYYY-MM-DD.json`:

```json
{
  "date": "2026-07-08",
  "weekOf": "2026-07-07",
  "findings": {
    "keyChanges": [
      {
        "status": "positive|negative|neutral",
        "sentiment": {
          "headline": "...",
          "reality": "...",
          "confidence": "high|medium|low",
          "rationale": "..."
        },
        "evidence": {
          "positive_signals": ["..."],
          "negative_signals": ["..."],
          "key_metrics": {
            "actual": "...",
            "target": "...",
            "trajectory": "..."
          }
        },
        "category": "Cybercab Production",
        "title": "...",
        "description": "...",
        "source": "https://..."
      }
    ],
    "trends": [
      "Trend 1",
      "Trend 2"
    ],
    "metrics": {
      "cybercab": [
        { "date": "2026-07-08", "count": 160, "note": "..." }
      ],
      "robotaxiFleet": [
        { "date": "2026-07-08", "count": 40, "note": "..." }
      ],
      "jobPostings": [
        { "date": "2026-07-08", "count": 120, "note": "..." }
      ]
    },
    "quarterlyData": [
      { "quarter": "Q2-26", "production": 451758, "delivery": 480126 }
    ],
    "categoryUpdates": {
      "cybercab": {
        "criticalNews": "Latest development",
        "newKeyPoint": "New key point to add",
        "newTimelineEvent": {
          "date": "2026-07-01",
          "event": "Production milestone"
        }
      }
    }
  },
  "metadata": {
    "sourcesSearched": ["teslarati.com", "teslanorth.com", "robotaxitracker.com"],
    "urlsSeen": ["https://...", "https://..."],
    "researchDuration": "12m"
  }
}
```

**Validation**: Findings must match `findings/schema.json`

---

## CRITICAL: Sentiment Analysis Guidelines

**BE VERY CRITICAL. DO NOT SUGAR COAT.**

When assigning `status` (positive/negative/neutral), prioritize **structural/fundamental issues** over **headline wins**:

### Mark as NEGATIVE when:
✅ **Fundamental constraints remain unsolved**
- Example: Robotaxi expands cities but fleet stuck at 50 vehicles after a year
- Example: Production timeline announced but "impossible to predict" and "quite slow"
- Example: Regulatory approval but no path to actual deployment

✅ **Negative signals outweigh or undermine positive signals**
- Example: New facility announced but existing facility underperforming
- Example: Timeline confirmed but with major caveats/delays
- Example: Growth metrics declining despite new initiatives

✅ **Progress metrics show stagnation or regression**
- Example: Fleet growth <10% over 6+ months
- Example: Timeline pushed right by >3 months
- Example: Cost targets missed significantly

### Mark as NEUTRAL when:
✅ **Mixed signals with no clear winner**
- Example: Timeline firmed up but with "slow ramp" warning
- Example: Approval granted but deployment timeline uncertain

✅ **Positive headline but concerning reality**
- Example: Expansion announced but existing ops struggling
- Example: Production starts but volume unclear

### Mark as POSITIVE when:
✅ **Clear progress on fundamentals**
- Example: Fleet doubles in size with strong metrics
- Example: Regulatory win with clear deployment path
- Example: Production ramp on track with volume targets

✅ **Milestones achieved without major caveats**
- Example: First commercial delivery with customer confirmed
- Example: Facility operational at target capacity

### Reality Check:
**Ask yourself**: "If I owned Tesla stock, would this news make me more or less confident in the timeline?"

- More confident = positive
- Unchanged/uncertain = neutral
- Less confident = negative

**Examples from 2026-07-08:**
- ❌ Robotaxi expansion to Miami/Dallas - marked POSITIVE originally
  - Reality: Fleet stuck at 50 vehicles after a year = **FAILED SCALING**
  - Correct rating: **NEGATIVE** (fundamental constraint unsolved)

- ✅ Denmark FSD approval - marked POSITIVE
  - Reality: Regulatory progress, no major caveats
  - Correct rating: **POSITIVE**

- ✅ Optimus production timeline - marked NEUTRAL
  - Reality: Timeline set but "quite slow" + "impossible to predict"
  - Correct rating: **NEUTRAL** (mixed signals)

---

### Step 5: Skip if No News

If no keyChanges, trends, metrics, or category updates found:

```json
{
  "date": "2026-07-08",
  "weekOf": "2026-07-07",
  "findings": {
    "keyChanges": [],
    "trends": []
  },
  "metadata": {
    "skipReason": "No significant news found for 2026-07-08",
    "sourcesSearched": ["..."]
  }
}
```

**DO NOT** run merge script if findings are empty. Just commit the findings file for audit trail.

### Step 6: Merge Findings

```bash
cd /Users/gonzalosolis/Research
python3 scripts/merge_findings.py findings/YYYY-MM-DD.json
```

This script will:
- ✅ Load findings + current data
- ✅ Merge keyChanges into weekly summaries
- ✅ Append metric data points (deduplicated)
- ✅ Add quarterly data (deduplicated)
- ✅ Update category metadata
- ✅ Apply caps (keyPoints: 15, timeline: 15)
- ✅ Validate merged result
- ✅ Save to tesla-tracking-data.json

### Step 7: Update URL Cache

```bash
# Add all URLs from findings to cache
for url in $(cat findings/YYYY-MM-DD.json | python3 -c "
import json, sys
findings = json.load(sys.stdin)
for url in findings['metadata']['urlsSeen']:
    print(url)
"); do
  # Get category and title from keyChanges
  python3 scripts/url_cache.py add "$url" "Category" "Title"
done
```

### Step 8: Archive Old Data

```bash
python3 scripts/archive_old_data.py
```

Keeps current + previous year in main file, archives the rest.

### Step 9: Build

```bash
npm run build
```

Build will fail if validation errors exist (Zod runtime validation).

### Step 10: Commit and Push

```bash
git add tesla-tracking-data.json findings/YYYY-MM-DD.json findings/url-cache.json
git commit -m "Update: Research findings for YYYY-MM-DD

$(python3 -c "
import json
findings = json.load(open('findings/YYYY-MM-DD.json'))
print(f'{len(findings[\"findings\"][\"keyChanges\"])} key changes')
print(f'{len(findings[\"findings\"].get(\"trends\", []))} trends')
")

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

git push origin main
```

---

## Policy: Avoiding Repetitive Headlines

**CRITICAL RULE**: Only create keyChanges for actual news, not for "no change" situations.

### When TO Create a keyChange:
✅ New developments (approvals, deployments, announcements)
✅ Significant changes (fleet growth >20%, timeline shifts >1 month)
✅ Major milestones (production starts, facility openings)

### When NOT TO Create a keyChange:
❌ Metrics that haven't changed since last update
❌ "Still waiting" or "remains unchanged" situations
❌ Repeating information from previous weeks

**For stagnant metrics**:
- Update the metric data point in findings.metrics.*
- Do NOT create a keyChange unless there's new context

---

## Caps on Category Arrays

The merge script enforces caps to prevent unbounded growth:

- **keyPoints**: Max 15 per category (FIFO, keeps most recent)
- **timeline**: Max 15 events per category (FIFO, keeps most recent)
- **weeklySummaries**: Max 52 weeks in main file (rest archived)

When adding `categoryUpdates.*.newKeyPoint` or `categoryUpdates.*.newTimelineEvent`, the merge script will automatically cap the arrays.

---

## Example Invocation

```
User: /tesla-update-v2
```

Expected behavior:
1. Read hot context only (~10KB)
2. Research across all 9 categories
3. Emit findings/YYYY-MM-DD.json
4. Run merge script
5. Update URL cache
6. Archive old data
7. Build
8. Commit + push
9. Report summary to user

---

## Error Handling

If merge fails:
- Findings file is preserved
- Main data file unchanged
- Can debug merge separately
- Can re-run merge after fixing

If research fails:
- No findings file created
- Main data unchanged
- Can resume research without re-doing completed categories

---

## Cost Savings

**V1 (old)**:
- Context: 167KB JSON + 670-line skill = ~200KB
- Per run: ~$0.15 (rough estimate)

**V2 (new)**:
- Context: 10KB hot slice + schema = ~15KB
- Per run: ~$0.02 (rough estimate)

**Savings**: ~87% reduction in context cost

---

## Migration Note

This is **V2** of the skill. The old `/tesla-update` skill still exists but should be deprecated.

Use `/tesla-update-v2` for new runs. The old skill will be removed after V2 is proven stable.
