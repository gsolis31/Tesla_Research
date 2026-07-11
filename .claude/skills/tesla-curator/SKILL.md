---
name: tesla-curator
description: Quality gate that validates and merges category findings into final findings file
user-invocable: false
allowed-tools: Read, Write, Bash
---

# Tesla Curator Agent

## Purpose

Quality gate agent that runs AFTER all researchers complete:
- Loads all `findings-{category}.json` files
- Deduplicates vs last week + URL cache
- Validates sentiment vs reality (catches sugar-coating)
- Normalizes category names, dates, confidence levels
- Refuses weak single-source claims
- Outputs final `findings/YYYY-MM-DD.json` (or skipReason if no news)

**One curator brain sees the full picture** → better than 9 isolated researchers.

---

## Input Contract

When spawned, expects these parameters:

```json
{
  "date": "2026-07-08",
  "weekOf": "2026-07-06",
  "findingsFiles": [
    "findings-cybercab.json",
    "findings-fsd.json",
    "findings-optimus.json",
    "findings-aiChip.json",
    "findings-battery4680.json",
    "findings-terafab.json",
    "findings-jobPostings.json",
    "findings-productionDelivery.json",
    "findings-fsdv15.json"
  ],
  "hotContext": {
    "lastWeekKeyChanges": [...],
    "urlCache": "findings/url-cache.json"
  }
}
```

Parent orchestrator provides this via prompt or JSON file.

---

## Output Contract

Writes `findings/YYYY-MM-DD.json`:

```json
{
  "date": "2026-07-08",
  "weekOf": "2026-07-06",
  "findings": {
    "keyChanges": [
      // Merged from all categories, deduplicated, validated
    ],
    "trends": [
      // Extracted from keyChanges
    ],
    "metrics": {
      "cybercab": [...],
      "robotaxiFleet": [...],
      "jobPostings": [...]
    },
    "quarterlyData": [
      // From productionDelivery
    ],
    "categoryUpdates": {
      "cybercab": {...},
      "fsd": {...},
      // etc.
    }
  },
  "metadata": {
    "sourcesSearched": [...],
    "urlsSeen": [...],
    "categoriesResearched": [...],
    "validationSummary": {
      "totalKeyChanges": 12,
      "duplicatesRemoved": 3,
      "sentimentCorrected": 2,
      "weakClaimsRejected": 1
    }
  }
}
```

**If no news found:**
```json
{
  "date": "2026-07-08",
  "weekOf": "2026-07-06",
  "findings": {
    "keyChanges": [],
    "trends": []
  },
  "metadata": {
    "skipReason": "No significant news found across all categories",
    "categoriesResearched": [...]
  }
}
```

---

## Execution Steps

### Step 1: Load All Category Findings

```python
import json
from pathlib import Path

# Parse input config
config = json.load(open('curator-config.json'))

date = config['date']
week_of = config['weekOf']
findings_files = config['findingsFiles']

# Load all category findings
category_findings = []
for file_path in findings_files:
    if Path(file_path).exists():
        with open(file_path) as f:
            category_findings.append(json.load(f))
    else:
        print(f"⚠️  Missing: {file_path}")

print(f"Loaded {len(category_findings)} category findings")
```

### Step 2: Load Hot Context

```python
# Load last week's keyChanges for deduplication
hot_context = config['hotContext']
last_week_key_changes = hot_context.get('lastWeekKeyChanges', [])

# Load URL cache
url_cache_path = hot_context.get('urlCache', 'findings/url-cache.json')
if Path(url_cache_path).exists():
    with open(url_cache_path) as f:
        url_cache = json.load(f)
else:
    url_cache = {"urls": {}}

print(f"Last week had {len(last_week_key_changes)} keyChanges")
print(f"URL cache has {len(url_cache['urls'])} entries")
```

### Step 3: Collect All KeyChanges

```python
all_key_changes = []

for category_data in category_findings:
    category_key = category_data.get('categoryKey')
    key_changes = category_data.get('keyChanges', [])

    print(f"  {category_key}: {len(key_changes)} keyChanges")

    for kc in key_changes:
        # Tag with source category
        kc['_sourceCategory'] = category_key
        all_key_changes.append(kc)

print(f"\nTotal keyChanges before dedup: {len(all_key_changes)}")
```

### Step 4: Deduplicate KeyChanges

**Dedup strategy:**
1. Check vs last week (same title + category = duplicate)
2. Check vs URL cache (URL already seen = duplicate)
3. Check within this week (same title + category = duplicate)

```python
def is_duplicate(kc, last_week_kcs, seen_titles):
    """Check if keyChange is a duplicate."""
    title = kc.get('title', '').strip()
    category = kc.get('category', '').strip()
    source_url = kc.get('source', '')

    # Check vs last week
    for last_kc in last_week_kcs:
        if (last_kc.get('title', '').strip() == title and
            last_kc.get('category', '').strip() == category):
            return True, "duplicate_vs_last_week"

    # Check URL cache
    if source_url and source_url in url_cache.get('urls', {}):
        return True, "url_already_cached"

    # Check within this week
    key = f"{category}|{title}"
    if key in seen_titles:
        return True, "duplicate_within_week"

    seen_titles.add(key)
    return False, None

# Deduplicate
deduplicated = []
duplicates_removed = []
seen_titles = set()

for kc in all_key_changes:
    is_dup, reason = is_duplicate(kc, last_week_key_changes, seen_titles)
    if is_dup:
        duplicates_removed.append({
            'title': kc.get('title'),
            'reason': reason
        })
    else:
        deduplicated.append(kc)

print(f"Removed {len(duplicates_removed)} duplicates")
print(f"Remaining: {len(deduplicated)} keyChanges")
```

### Step 5: Validate Sentiment

**Check for sugar-coating:**
- If status = "positive" but reality = "negative" → ERROR
- If status = "positive" but reality = "neutral" → WARN (might be OK)
- If negative_signals > positive_signals but status = "positive" → WARN

```python
def validate_sentiment(kc):
    """Validate sentiment matches reality, not headline."""
    issues = []

    sentiment = kc.get('sentiment', {})
    status = kc.get('status')
    headline = sentiment.get('headline')
    reality = sentiment.get('reality')
    evidence = kc.get('evidence', {})

    # Critical: status should match reality, not headline
    if status != reality:
        if status == 'positive' and reality == 'negative':
            issues.append({
                'severity': 'ERROR',
                'message': f'Status is positive but reality is negative (sugar-coating)',
                'suggestion': f'Change status to negative'
            })
        elif status == 'positive' and reality == 'neutral':
            issues.append({
                'severity': 'WARN',
                'message': f'Status is positive but reality is neutral',
                'suggestion': f'Consider changing status to neutral'
            })

    # Check if negative signals outweigh positives
    pos_count = len(evidence.get('positive_signals', []))
    neg_count = len(evidence.get('negative_signals', []))

    if neg_count > pos_count and status == 'positive':
        issues.append({
            'severity': 'WARN',
            'message': f'More negative signals ({neg_count}) than positive ({pos_count}) but status is positive',
            'suggestion': f'Consider neutral or negative status'
        })

    return issues

# Validate all keyChanges
sentiment_issues = []
corrected_count = 0

for kc in deduplicated:
    issues = validate_sentiment(kc)

    if issues:
        print(f"\n⚠️  Sentiment issue in: {kc['title']}")
        for issue in issues:
            print(f"   {issue['severity']}: {issue['message']}")
            print(f"   → {issue['suggestion']}")

            # Auto-fix ERROR-level issues
            if issue['severity'] == 'ERROR':
                sentiment = kc.get('sentiment', {})
                reality = sentiment.get('reality')
                kc['status'] = reality
                corrected_count += 1
                print(f"   ✓ Auto-corrected status to: {reality}")

        sentiment_issues.extend(issues)

print(f"\nSentiment validation: {corrected_count} corrections applied")
```

### Step 6: Refuse Weak Claims

**Criteria for rejection:**
- Only one source AND it's Electrek (tier 2, known bias)
- Confidence = "low" AND no corroboration
- Evidence is too vague (e.g., "possible", "maybe", "could")

```python
def is_weak_claim(kc):
    """Check if claim is too weak to include."""
    source = kc.get('source', '')
    sentiment = kc.get('sentiment', {})
    confidence = sentiment.get('confidence', 'medium')
    evidence = kc.get('evidence', {})

    # Electrek-only with low confidence
    if 'electrek.co' in source and confidence == 'low':
        return True, "electrek_only_low_confidence"

    # No substantial evidence
    pos_signals = evidence.get('positive_signals', [])
    neg_signals = evidence.get('negative_signals', [])

    if len(pos_signals) + len(neg_signals) < 2:
        return True, "insufficient_evidence"

    # Check for vague language
    description = kc.get('description', '').lower()
    vague_words = ['possible', 'maybe', 'could', 'might', 'potentially', 'reportedly']
    vague_count = sum(1 for word in vague_words if word in description)

    if vague_count >= 3 and confidence == 'low':
        return True, "too_vague"

    return False, None

# Filter weak claims
filtered = []
rejected = []

for kc in deduplicated:
    is_weak, reason = is_weak_claim(kc)
    if is_weak:
        rejected.append({
            'title': kc.get('title'),
            'reason': reason
        })
    else:
        filtered.append(kc)

print(f"Rejected {len(rejected)} weak claims")
print(f"Remaining: {len(filtered)} keyChanges")
```

### Step 7: Normalize Data

**Ensure consistency:**
- Category names match standard list
- Dates in YYYY-MM-DD format
- Confidence levels are valid (high/medium/low)
- Status values are valid (positive/negative/neutral)

```python
CATEGORY_NAMES = {
    'cybercab': 'Cybercab Production',
    'fsd': 'FSD Country Approvals',
    'optimus': 'Optimus Production',
    'productionDelivery': 'Vehicle Production & Delivery',
    'aiChip': 'AI Chip Production',
    'battery4680': '4680 Battery Cell Production',
    'terafab': 'Terafab Manufacturing',
    'jobPostings': 'Job Postings',
    'fsdv15': 'FSD v15 Software'
}

def normalize_key_change(kc):
    """Normalize keyChange data."""
    # Normalize category name
    category = kc.get('category', '')
    for key, standard_name in CATEGORY_NAMES.items():
        if category.lower().replace(' ', '').replace('&', '') == key.lower():
            kc['category'] = standard_name
            break

    # Validate status
    status = kc.get('status', 'neutral')
    if status not in ['positive', 'negative', 'neutral']:
        kc['status'] = 'neutral'

    # Validate confidence
    sentiment = kc.get('sentiment', {})
    confidence = sentiment.get('confidence', 'medium')
    if confidence not in ['high', 'medium', 'low']:
        sentiment['confidence'] = 'medium'

    return kc

# Normalize all keyChanges
normalized = [normalize_key_change(kc) for kc in filtered]

print(f"Normalized {len(normalized)} keyChanges")
```

### Step 8: Extract Trends

**Auto-generate trends from keyChanges:**

```python
def extract_trends(key_changes):
    """Extract high-level trends from keyChanges."""
    trends = []

    # Group by category
    by_category = {}
    for kc in key_changes:
        category = kc.get('category', 'Unknown')
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(kc)

    # Generate trend for each category with news
    for category, kcs in by_category.items():
        if len(kcs) == 1:
            # Single update: use title
            trends.append(f"{category}: {kcs[0]['title']}")
        else:
            # Multiple updates: summarize
            pos_count = sum(1 for kc in kcs if kc['status'] == 'positive')
            neg_count = sum(1 for kc in kcs if kc['status'] == 'negative')

            if neg_count > pos_count:
                trends.append(f"{category}: Mixed signals with concerning developments")
            elif pos_count > neg_count:
                trends.append(f"{category}: Progress across multiple fronts")
            else:
                trends.append(f"{category}: Balanced developments")

    return trends[:4]  # Max 4 trends

trends = extract_trends(normalized)
print(f"Generated {len(trends)} trends")
```

### Step 9: Merge Metrics

```python
metrics = {
    'cybercab': [],
    'robotaxiFleet': [],
    'jobPostings': []
}

quarterly_data = []

for category_data in category_findings:
    # Metric updates
    if 'metricUpdate' in category_data and category_data['metricUpdate']:
        category_key = category_data['categoryKey']
        if category_key == 'cybercab':
            metrics['cybercab'].append(category_data['metricUpdate'])
        elif category_key == 'jobPostings':
            metrics['jobPostings'].append(category_data['metricUpdate'])

    # Fleet updates
    if 'fleetUpdate' in category_data and category_data['fleetUpdate']:
        metrics['robotaxiFleet'].append(category_data['fleetUpdate'])

    # Quarterly data
    if category_data.get('categoryKey') == 'productionDelivery':
        if 'quarterlyData' in category_data and category_data['quarterlyData']:
            quarterly_data.extend(category_data['quarterlyData'])

print(f"Merged metrics: {sum(len(v) for v in metrics.values())} data points")
print(f"Quarterly data: {len(quarterly_data)} entries")
```

### Step 10: Merge Category Updates

```python
category_updates = {}

for category_data in category_findings:
    if 'categoryUpdate' in category_data and category_data['categoryUpdate']:
        category_key = category_data['categoryKey']
        category_updates[category_key] = category_data['categoryUpdate']

print(f"Category updates: {len(category_updates)} categories")
```

### Step 11: Collect Metadata

```python
# Collect all URLs seen
all_urls = []
all_sources = []

for category_data in category_findings:
    all_urls.extend(category_data.get('urlsSeen', []))
    sources = category_data.get('metadata', {}).get('sourcesSearched', [])
    all_sources.extend(sources)

# Deduplicate
all_urls = list(set(all_urls))
all_sources = list(set(all_sources))

# Categories researched
categories_researched = [cf['categoryKey'] for cf in category_findings if cf.get('categoryKey')]

metadata = {
    'sourcesSearched': all_sources,
    'urlsSeen': all_urls,
    'categoriesResearched': categories_researched,
    'validationSummary': {
        'totalKeyChanges': len(all_key_changes),
        'duplicatesRemoved': len(duplicates_removed),
        'sentimentCorrected': corrected_count,
        'weakClaimsRejected': len(rejected)
    }
}
```

### Step 12: Write Final Findings

```python
import json
from pathlib import Path

final_findings = {
    'date': date,
    'weekOf': week_of,
    'findings': {
        'keyChanges': normalized,
        'trends': trends,
        'metrics': metrics,
        'quarterlyData': quarterly_data,
        'categoryUpdates': category_updates
    },
    'metadata': metadata
}

# Check if we have any news
has_news = (
    len(normalized) > 0 or
    any(len(v) > 0 for v in metrics.values()) or
    len(quarterly_data) > 0
)

if not has_news:
    # No news found
    final_findings = {
        'date': date,
        'weekOf': week_of,
        'findings': {
            'keyChanges': [],
            'trends': []
        },
        'metadata': {
            'skipReason': 'No significant news found across all categories',
            'categoriesResearched': categories_researched,
            'sourcesSearched': all_sources
        }
    }

# Write to findings directory
output_path = Path('findings') / f'{date}.json'
output_path.parent.mkdir(exist_ok=True)

with open(output_path, 'w') as f:
    json.dump(final_findings, f, indent=2)

print(f"\n✅ Written {output_path}")
print(f"   - {len(normalized)} keyChanges")
print(f"   - {len(trends)} trends")
print(f"   - {metadata['validationSummary']['duplicatesRemoved']} duplicates removed")
print(f"   - {metadata['validationSummary']['sentimentCorrected']} sentiment corrections")
print(f"   - {metadata['validationSummary']['weakClaimsRejected']} weak claims rejected")
```

---

## Validation Summary Report

After writing findings, generate a summary report:

```python
report = f"""
======================================================================
Tesla Curator - Validation Report
======================================================================

Date: {date}
Week of: {week_of}

[1/4] Category Findings Loaded
✓ {len(category_findings)} categories researched
✓ {len(all_key_changes)} keyChanges collected

[2/4] Deduplication
✓ Removed {len(duplicates_removed)} duplicates
  - {sum(1 for d in duplicates_removed if d['reason'] == 'duplicate_vs_last_week')} vs last week
  - {sum(1 for d in duplicates_removed if d['reason'] == 'url_already_cached')} already cached
  - {sum(1 for d in duplicates_removed if d['reason'] == 'duplicate_within_week')} within week

[3/4] Sentiment Validation
✓ {corrected_count} sentiment corrections applied
⚠ {len([i for i in sentiment_issues if i['severity'] == 'WARN'])} warnings

[4/4] Quality Filter
✓ Rejected {len(rejected)} weak claims
  - {sum(1 for r in rejected if r['reason'] == 'electrek_only_low_confidence')} Electrek-only
  - {sum(1 for r in rejected if r['reason'] == 'insufficient_evidence')} insufficient evidence
  - {sum(1 for r in rejected if r['reason'] == 'too_vague')} too vague

======================================================================
✓ CURATION COMPLETE: {len(normalized)} validated keyChanges
======================================================================
"""

print(report)

# Write report to file
with open(f'findings/curator-report-{date}.md', 'w') as f:
    f.write(report)
```

---

## Error Handling

**If category findings missing:**
- Warn but continue with available findings
- Note in metadata which categories were skipped

**If all categories empty:**
- Write findings with skipReason
- Don't fail - this is valid outcome

**If sentiment validation fails:**
- Auto-correct ERROR-level issues
- Log WARN-level issues but don't block

**If URL cache missing:**
- Create empty cache structure
- Proceed without dedup (safer than failing)

---

## Usage Example

**Orchestrator spawns curator:**

```python
# After all researchers complete

config = {
    "date": "2026-07-08",
    "weekOf": "2026-07-06",
    "findingsFiles": [
        "findings-cybercab.json",
        "findings-fsd.json",
        # ... all 9 categories
    ],
    "hotContext": {
        "lastWeekKeyChanges": data['weeklySummaries'][0]['keyChanges'],
        "urlCache": "findings/url-cache.json"
    }
}

# Write config
with open('curator-config.json', 'w') as f:
    json.dump(config, f)

# Spawn curator
agent_id = Task({
    subagent_type: "tesla-curator",
    description: "Validate and merge findings",
    model: "sonnet",  # Quality matters here
    prompt: f"Curate research findings using config in curator-config.json"
})

# Result: findings/2026-07-08.json
```

---

## Success Metrics

**Execution:**
- Time: 2-3 min (serial processing, quality over speed)
- Cost: ~$0.02 (Sonnet for quality)

**Quality:**
- Zero duplicates in output
- Sentiment matches reality (not headlines)
- No weak single-source claims
- Consistent data formatting

**Output:**
- Valid findings/YYYY-MM-DD.json ready for merge script
- Curator report showing what was fixed
- Clear skipReason if no news found

---

## Next Steps After Curation

After curator completes:

1. **Review curator report:**
```bash
cat findings/curator-report-2026-07-08.md
```

2. **Verify findings:**
```bash
cat findings/2026-07-08.json | jq '.findings.keyChanges[] | {title, status, reality: .sentiment.reality}'
```

3. **Run merge + deploy:**
```bash
python3 scripts/merge_findings.py findings/2026-07-08.json
python3 scripts/validate_data.py
npm run build
git add . && git commit && git push
```

---

## Integration with Researchers

**Full parallel pipeline:**

```
1. Spawn 9 tesla-researcher agents (parallel)
   → findings-{category}.json × 9

2. Spawn 1 tesla-curator agent (serial)
   → findings/YYYY-MM-DD.json (validated)

3. Run scripts (merge, validate, build, deploy)
   → Updated dashboard
```

**Benefits:**
- Researchers work independently (no interference)
- Curator sees full picture (better deduplication)
- Quality gate before data goes live
- Clear separation of concerns
