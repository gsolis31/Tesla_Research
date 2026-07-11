---
name: tesla-researcher
description: Research a single Tesla category and output validated findings fragment
user-invocable: false
allowed-tools: WebSearch, Read, Write, Bash
---

# Tesla Category Researcher Agent

## Purpose

Generic research agent that:
- Researches **ONE category** for a date range
- Outputs `findings-{categoryKey}.json` (category fragment)
- Uses URL cache to avoid duplicates
- Does NOT edit tesla-tracking-data.json
- Can be spawned in parallel (6-9 instances)

---

## Input Contract

When spawned, expects these parameters:

```json
{
  "categoryKey": "cybercab",
  "dateFrom": "2026-07-03",
  "dateTo": "2026-07-08",
  "weekOf": "2026-07-06",
  "hotContext": {
    "latestMetric": {"date": "2026-06-28", "count": 150, "note": "..."},
    "latestFleet": {"date": "2026-06-28", "count": 50, "note": "..."},
    "criticalNews": "Latest development...",
    "recentKeyChanges": [...]
  },
  "sources": {
    "tier1": ["teslarati.com", "robotaxitracker.com", "teslanorth.com"],
    "tier2": ["electrek.co"],
    "specialized": ["robotaxitracker.com"]
  },
  "keywords": ["Cybercab", "robotaxi", "fleet", "autonomous", "FSD"],
  "priority": "high"
}
```

Parent skill provides this via prompt or JSON file.

---

## Output Contract

Writes `findings-{categoryKey}.json`:

```json
{
  "categoryKey": "cybercab",
  "keyChanges": [
    {
      "status": "positive|negative|neutral",
      "sentiment": {
        "headline": "positive|negative|neutral",
        "reality": "positive|negative|neutral",
        "confidence": "high|medium|low",
        "rationale": "Detailed explanation..."
      },
      "evidence": {
        "positive_signals": ["Signal 1", "Signal 2"],
        "negative_signals": ["Signal 1", "Signal 2"],
        "key_metrics": {
          "actual": "...",
          "target": "...",
          "trajectory": "..."
        }
      },
      "category": "Cybercab Production",
      "title": "Short headline",
      "description": "Detailed 3-5 sentence description",
      "source": "https://..."
    }
  ],
  "metricUpdate": {
    "date": "2026-07-08",
    "count": 160,
    "note": "Staged at Giga Texas"
  },
  "fleetUpdate": {
    "date": "2026-07-08",
    "count": 50,
    "note": "Active across 4 cities"
  },
  "categoryUpdate": {
    "criticalNews": "Latest development summary",
    "newKeyPoint": "New key point to add to category",
    "newTimelineEvent": {
      "date": "2026-07-03",
      "event": "Miami robotaxi service launched"
    }
  },
  "urlsSeen": ["https://...", "https://..."],
  "metadata": {
    "researchDuration": "~4 min",
    "sourcesSearched": ["teslarati.com", "robotaxitracker.com"]
  }
}
```

**If no news found:**
```json
{
  "categoryKey": "jobPostings",
  "keyChanges": [],
  "urlsSeen": [],
  "metadata": {
    "skipReason": "No significant news found for job postings",
    "sourcesSearched": [...]
  }
}
```

---

## Execution Steps

### Step 1: Parse Input Config

Load category configuration from prompt or JSON file:

```python
import json

# If config provided as JSON file path
config = json.load(open('research-config-cybercab.json'))

# Or parse from prompt parameters
category_key = config['categoryKey']
date_from = config['dateFrom']
date_to = config['dateTo']
sources = config['sources']
keywords = config['keywords']
```

### Step 2: Load Hot Context

```python
hot_context = config['hotContext']

print(f"Category: {category_key}")
print(f"Research period: {date_from} → {date_to}")
print(f"Latest metric: {hot_context.get('latestMetric')}")
print(f"Critical news: {hot_context['criticalNews']}")
print(f"Recent keyChanges: {len(hot_context['recentKeyChanges'])} items")
```

**Do NOT read the full tesla-tracking-data.json** - use only provided hot context.

### Step 3: Search Tier 1 Sources

For each Tier 1 source, search with targeted queries:

```python
for source in sources['tier1']:
    for keyword in keywords[:3]:  # Top 3 keywords
        query = f"site:{source} {keyword} after:{date_from}"
        # Use WebSearch tool
        results = search(query)
        # Process results...
```

**Search strategy:**
- Tier 1 sources: Deep search, trust results
- Tier 2 sources (Electrek): Only for confirmation, don't rely on alone
- Specialized sources: MUST check (e.g., robotaxitracker.com for fleet counts)

### Step 4: Check URL Cache

For each URL found:

```bash
python3 scripts/url_cache.py check "https://example.com/article"
# Exit code 0 = already seen, skip
# Exit code 1 = new URL, analyze
```

**Only analyze new URLs** to avoid duplicate keyChanges.

### Step 5: Extract KeyChanges (CRITICAL SENTIMENT)

For each new article with significant news:

**BE VERY CRITICAL. DO NOT SUGAR COAT.**

Apply these rules:

#### Mark as NEGATIVE when:
- ✅ Fundamental constraints remain unsolved
  - Example: Fleet stuck at 50 vehicles after a year
  - Example: Production "impossible to predict" and "quite slow"
  - Example: Timeline pushed right by >3 months

- ✅ Negative signals outweigh or undermine positives
  - Example: Expansion announced but existing ops failing
  - Example: Milestone reached but with major caveats

- ✅ Progress metrics show stagnation or regression
  - Example: Fleet growth <10% over 6+ months
  - Example: Timeline delays of 3+ months

#### Mark as NEUTRAL when:
- ✅ Mixed signals with no clear winner
  - Example: Timeline confirmed but "slow ramp" warning
  - Example: Approval granted but deployment unclear

- ✅ Positive headline but concerning reality
  - Example: City expansion but fleet not scaling

#### Mark as POSITIVE when:
- ✅ Clear progress on fundamentals
  - Example: Fleet doubles with strong metrics
  - Example: Regulatory win with deployment path
  - Example: Production ramp on track

- ✅ Milestones achieved without major caveats
  - Example: First commercial delivery confirmed
  - Example: Facility operational at target

#### Reality Check Question:
**"If I owned Tesla stock, would this news make me more or less confident in the timeline?"**
- More confident = positive
- Unchanged/uncertain = neutral
- Less confident = negative

### Step 6: Find Metric Updates

**Category-specific metrics:**

- **Cybercab**: Production count (staged vehicles)
- **Robotaxi Fleet**: Active vehicles in service
- **Job Postings**: Optimus-related openings
- **FSD Approvals**: Country count
- **Production & Delivery**: Quarterly data (Q1, Q2, Q3, Q4)

**Specialized sources for metrics:**
- Robotaxi fleet: robotaxitracker.com (MUST CHECK)
- Job postings: LinkedIn, optimusk.blog
- P&D: ir.tesla.com/press (official only)

```python
# Example for robotaxi
if category_key == "cybercab":
    # Search robotaxitracker.com for latest fleet count
    # Update metricUpdate and fleetUpdate
```

### Step 7: Update Category Metadata

```python
category_update = {
    "criticalNews": "1-sentence latest development",
    "newKeyPoint": "New key point if significant milestone",
    "newTimelineEvent": {
        "date": "2026-07-03",
        "event": "Miami service launched"
    } if has_timeline_event else None
}
```

**Guidelines:**
- criticalNews: Always update if keyChanges found
- newKeyPoint: Only if truly significant (new milestone, major shift)
- newTimelineEvent: Only if specific date + concrete event

### Step 8: Write Findings File

```python
import json

findings = {
    "categoryKey": category_key,
    "keyChanges": key_changes,  # list of keyChange objects
    "metricUpdate": metric_update if found else None,
    "fleetUpdate": fleet_update if found else None,
    "categoryUpdate": category_update if has_updates else None,
    "urlsSeen": urls_seen,
    "metadata": {
        "researchDuration": "~4 min",
        "sourcesSearched": sources_searched
    }
}

with open(f'findings-{category_key}.json', 'w') as f:
    json.dump(findings, f, indent=2)

print(f"✅ Written findings-{category_key}.json")
print(f"   - {len(key_changes)} keyChanges")
print(f"   - {len(urls_seen)} URLs processed")
```

---

## Category Configurations

Built-in configs for all 9 categories:

### HIGH PRIORITY

**Cybercab Production**
```json
{
  "categoryKey": "cybercab",
  "categoryName": "Cybercab Production",
  "priority": "high",
  "sources": {
    "tier1": ["teslarati.com", "teslanorth.com", "teslaoracle.com"],
    "specialized": ["robotaxitracker.com"]
  },
  "keywords": ["Cybercab", "robotaxi", "fleet", "autonomous", "unsupervised"],
  "metrics": ["cybercab", "robotaxiFleet"],
  "estimatedTime": "4-5 min"
}
```

**FSD Country Approvals**
```json
{
  "categoryKey": "fsd",
  "categoryName": "FSD Country Approvals",
  "priority": "high",
  "sources": {
    "tier1": ["teslarati.com", "teslanorth.com", "teslaoracle.com"]
  },
  "keywords": ["FSD", "approval", "country", "Europe", "regulatory"],
  "metrics": ["fsdApprovals"],
  "estimatedTime": "3-4 min"
}
```

**Optimus Production**
```json
{
  "categoryKey": "optimus",
  "categoryName": "Optimus Production",
  "priority": "high",
  "sources": {
    "tier1": ["optimusk.blog", "teslarati.com", "teslanorth.com"]
  },
  "keywords": ["Optimus", "humanoid", "robot", "Fremont", "Giga Texas"],
  "metrics": [],
  "estimatedTime": "3-4 min"
}
```

**FSD v15 Software**
```json
{
  "categoryKey": "fsdv15",
  "categoryName": "FSD v15 Software",
  "priority": "high",
  "sources": {
    "tier1": ["teslarati.com", "teslanorth.com", "notateslaapp.com"]
  },
  "keywords": ["FSD v15", "FSD 15", "supervised", "end-to-end"],
  "metrics": [],
  "estimatedTime": "3-4 min"
}
```

### CRITICAL PRIORITY

**Vehicle Production & Delivery**
```json
{
  "categoryKey": "productionDelivery",
  "categoryName": "Vehicle Production & Delivery",
  "priority": "critical",
  "sources": {
    "tier1": ["ir.tesla.com"],
    "tier2": ["teslarati.com", "teslanorth.com"]
  },
  "keywords": ["quarterly", "production", "delivery", "Q1", "Q2", "Q3", "Q4"],
  "metrics": ["quarterlyData"],
  "estimatedTime": "2-3 min",
  "note": "Only search ir.tesla.com/press for official reports. Tier 2 for context only."
}
```

### MEDIUM PRIORITY

**AI Chip Production**
```json
{
  "categoryKey": "aiChip",
  "categoryName": "AI Chip Production",
  "priority": "medium",
  "sources": {
    "tier1": ["teslarati.com", "teslanorth.com", "teslaoracle.com"]
  },
  "keywords": ["AI5", "AI6", "Samsung", "TSMC", "2nm", "Dojo"],
  "metrics": [],
  "estimatedTime": "3-4 min"
}
```

**4680 Battery Cell Production**
```json
{
  "categoryKey": "battery4680",
  "categoryName": "4680 Battery Cell Production",
  "priority": "medium",
  "sources": {
    "tier1": ["teslarati.com", "teslanorth.com", "basenor.com"]
  },
  "keywords": ["4680", "battery cell", "GWh", "yield", "dry electrode"],
  "metrics": [],
  "estimatedTime": "3-4 min"
}
```

**Terafab Manufacturing**
```json
{
  "categoryKey": "terafab",
  "categoryName": "Terafab Manufacturing",
  "priority": "medium",
  "sources": {
    "tier1": ["teslarati.com", "teslanorth.com"]
  },
  "keywords": ["Terafab", "North Campus", "chip fab", "Taylor Texas"],
  "metrics": [],
  "estimatedTime": "3-4 min"
}
```

### LOW PRIORITY

**Job Postings**
```json
{
  "categoryKey": "jobPostings",
  "categoryName": "Job Postings",
  "priority": "low",
  "sources": {
    "tier1": ["optimusk.blog", "linkedin.com"]
  },
  "keywords": ["Optimus", "hiring", "job posting", "Tesla careers"],
  "metrics": ["jobPostings"],
  "estimatedTime": "2-3 min"
}
```

---

## Model Selection

Based on priority:
- **CRITICAL/HIGH priority**: Use Sonnet (better quality)
- **MEDIUM/LOW priority**: Use Haiku (cost savings)

Parent orchestrator can specify model when spawning:
```python
Task({
  subagent_type: "tesla-researcher",
  model: "sonnet" if priority in ["critical", "high"] else "haiku",
  prompt: ...
})
```

---

## Error Handling

**If category has no news:**
- Still write findings file with empty keyChanges
- Include skipReason in metadata
- Don't fail - let curator decide

**If sources unreachable:**
- Note in metadata which sources failed
- Continue with available sources
- Don't fail unless 0 sources work

**If URL cache errors:**
- Default to analyzing URL (safer than skipping)
- Log warning in metadata

---

## Quality Standards

**Evidence requirements:**
- Minimum 2 positive signals OR 2 negative signals
- If single-source claim: mark as low confidence
- If Electrek-only: don't use unless confirmed by Tier 1

**Metric requirements:**
- Only update if concrete number found
- Must have source (can't be estimated/guessed)
- Include note with context

**Timeline events:**
- Must have specific date (YYYY-MM-DD)
- Must have concrete event (not "expected" or "planned")

---

## Usage Example

**Orchestrator spawns researcher:**

```python
# In /tesla-update-v2 skill or parallel coordinator

config = {
  "categoryKey": "cybercab",
  "dateFrom": "2026-07-03",
  "dateTo": "2026-07-08",
  "weekOf": "2026-07-06",
  "hotContext": {
    "latestMetric": {"date": "2026-06-28", "count": 150},
    "criticalNews": "Austin fleet at 50 vehicles...",
    "recentKeyChanges": [...]
  },
  "sources": {
    "tier1": ["teslarati.com", "robotaxitracker.com"],
    "specialized": ["robotaxitracker.com"]
  },
  "keywords": ["Cybercab", "robotaxi", "fleet", "autonomous"]
}

# Spawn agent
agent_id = Task({
  subagent_type: "tesla-researcher",
  model: "sonnet",
  prompt: f"Research {config['categoryKey']} category with config: {json.dumps(config)}",
  run_in_background: true
})

# Result: findings-cybercab.json
```

---

## Success Metrics

**Per-category execution:**
- Time: 2-5 min (varies by category)
- Cost: ~$0.003-0.01 (Haiku) or ~$0.01-0.03 (Sonnet)
- Output: Valid findings-{categoryKey}.json

**Quality:**
- Sentiment matches reality (not sugar-coated)
- Evidence is substantial (not vague)
- No duplicate keyChanges vs last week
- URLs cached for future runs

---

## Next Steps After Research

Agent writes findings file and exits. Parent orchestrator:

1. Waits for all category researchers to complete
2. Spawns tesla-curator to validate + merge all findings
3. Curator outputs final findings/YYYY-MM-DD.json
4. Parent runs merge scripts + deploy
