# Research Findings Directory

This directory contains **intermediate artifacts** from `/tesla-update` research runs.

## Purpose

Instead of directly rewriting the 167KB `tesla-tracking-data.json` file, the skill now:

1. **Researches** across all categories
2. **Emits** a lightweight `findings/YYYY-MM-DD.json` file
3. **Merge script** deterministically combines findings → main data file

## Benefits

### ✅ Resumability
- Research failures don't corrupt main data
- Can re-run merge separately from research
- Can test merge logic without re-researching

### ✅ Auditability
- See exactly what was found before curation
- Track URLs seen (for deduplication)
- Review research before committing

### ✅ Parallelization
- Multiple agents can research different categories concurrently
- Each writes to separate findings files
- Merge script combines them deterministically

### ✅ Cost Control
- Agent only reads last week's data + current metrics (not full 167KB)
- Skip research if no news (findings file empty)
- Test merge logic without expensive LLM calls

## File Structure

```
findings/
├── schema.json                 # JSON Schema for findings format
├── README.md                   # This file
├── url-cache.json             # Deduplication cache (URLs already seen)
├── 2026-07-08.json            # Example findings file
└── YYYY-MM-DD.json            # Daily findings (one per research run)
```

## Findings Format

```json
{
  "date": "2026-07-08",
  "weekOf": "2026-07-07",
  "findings": {
    "keyChanges": [...],        // New developments
    "trends": [...],             // Trend observations
    "metrics": {                 // Metric updates
      "cybercab": [...],
      "robotaxiFleet": [...],
      "jobPostings": [...]
    },
    "quarterlyData": [...],      // New P&D reports
    "categoryUpdates": {         // Category metadata updates
      "cybercab": {
        "criticalNews": "...",
        "newKeyPoint": "...",
        "newTimelineEvent": { "date": "...", "event": "..." }
      }
    }
  },
  "metadata": {
    "sourcesSearched": [...],    // Which sources were checked
    "urlsSeen": [...],           // URLs discovered (for cache)
    "researchDuration": "12m"
  }
}
```

## Merge Process

```bash
# 1. Agent researches and emits findings
/tesla-update  # Creates findings/2026-07-08.json

# 2. Merge findings into main data file
python3 scripts/merge_findings.py findings/2026-07-08.json

# 3. Archive old data (optional, runs automatically in merge)
python3 scripts/archive_old_data.py

# 4. Build and deploy
npm run build
git add tesla-tracking-data.json findings/2026-07-08.json
git commit -m "Update: Research findings for 2026-07-08"
git push
```

## Caps on Growth

The merge script applies caps to prevent unbounded growth:

- **keyPoints**: Max 15 per category (FIFO, keeps most recent)
- **timeline**: Max 15 events per category (FIFO, keeps most recent)
- **weeklySummaries**: Max 52 weeks in main file (rest archived)

Old data is moved to `archives/YYYY.json` automatically.

## URL Deduplication

`url-cache.json` tracks all URLs seen across research runs:

```json
{
  "urls": {
    "https://electrek.co/2026/07/01/...": {
      "firstSeen": "2026-07-01",
      "lastSeen": "2026-07-08",
      "category": "Cybercab Production",
      "title": "..."
    }
  }
}
```

Agent checks cache before processing URLs to avoid:
- Re-analyzing same articles
- Duplicate keyChanges
- Wasted LLM tokens

## Migration from Old Workflow

**Old** (god-file agent loop):
```
Agent reads 167KB JSON + 670-line skill
  ↓
Rewrites entire JSON file
  ↓
Hopes nothing broke
  ↓
Build + deploy
```

**New** (schema-bound append-only):
```
Agent reads last week + current metrics (~10KB)
  ↓
Emits findings/YYYY-MM-DD.json (~5-10KB)
  ↓
Merge script updates main file (deterministic)
  ↓
Validate → Build → Deploy
```

## Schema Validation

All findings files are validated against `schema.json` before merge:

```bash
# Manual validation
python3 -c "
import json, jsonschema
schema = json.load(open('findings/schema.json'))
findings = json.load(open('findings/2026-07-08.json'))
jsonschema.validate(findings, schema)
print('✓ Valid')
"
```

The merge script auto-validates using `scripts/validate_data.py`.
