# Tesla Researcher Agent - Usage Guide

## Overview

Generic category research agent that can be spawned in parallel to research Tesla categories independently.

**Benefits:**
- ✅ Parallel execution (research 6-9 categories simultaneously)
- ✅ Isolation (Cybercab research can't pollute Optimus findings)
- ✅ Reusable (one agent definition, spawn with different configs)
- ✅ Critical sentiment analysis (follows strict guidelines)

**Execution time:**
- Sequential (old): 15-20 min for 9 categories
- Parallel (new): 5-6 min for 9 categories (3x faster)

---

## Quick Start

### 1. Generate Research Configs

```bash
# Create configs for all 9 categories
python3 scripts/spawn_researcher.py --all

# Or create config for one category
python3 scripts/spawn_researcher.py cybercab
```

This creates `research-config-{category}.json` files with:
- Date range (last update → today)
- Hot context (latest metrics, recent keyChanges)
- Sources (tier 1, tier 2, specialized)
- Keywords for search
- Priority (determines model: sonnet vs haiku)

### 2. Spawn Researchers (Manual Test)

**Single category (for testing):**

Use the `/tesla-researcher` skill with a config file:

```
User: Research cybercab category using research-config-cybercab.json
```

The agent will:
1. Load config
2. Search tier 1 sources
3. Check URL cache
4. Extract keyChanges with critical sentiment
5. Find metric updates
6. Write `findings-cybercab.json`

**Expected output:**
```
findings-cybercab.json created with:
- 1-3 keyChanges (or 0 if no news)
- metricUpdate (if found)
- fleetUpdate (if found)
- categoryUpdate
- urlsSeen list
```

### 3. Spawn All Researchers in Parallel

This is what the **orchestrator** (parent skill) would do:

```python
# Pseudo-code for parallel spawning
categories = ["cybercab", "fsd", "optimus", "aiChip", ...]

# Spawn all in parallel
agent_ids = []
for category in categories:
    config = json.load(open(f'research-config-{category}.json'))
    model = "sonnet" if config["priority"] in ["critical", "high"] else "haiku"

    agent_id = Task({
        subagent_type: "tesla-researcher",
        description: f"Research {category}",
        model: model,
        prompt: f"""
Research the {config['categoryName']} category.

Config: {json.dumps(config)}

Output: findings-{category}.json
        """,
        run_in_background: True
    })

    agent_ids.append(agent_id)

# Wait for all to complete
for agent_id in agent_ids:
    wait_for_completion(agent_id)

# Result: 9 findings-*.json files
```

---

## Output Schema

Each researcher outputs `findings-{categoryKey}.json`:

```json
{
  "categoryKey": "cybercab",
  "keyChanges": [
    {
      "status": "negative",
      "sentiment": {
        "headline": "positive",
        "reality": "negative",
        "confidence": "high",
        "rationale": "City expansion doesn't fix failed scaling..."
      },
      "evidence": {
        "positive_signals": ["Miami launched", "Dallas launched"],
        "negative_signals": ["Fleet stuck at 50 vehicles", "Software bottleneck"],
        "key_metrics": {
          "actual": "50 vehicles after 1 year",
          "target": "Mass market service",
          "trajectory": "Stagnant"
        }
      },
      "category": "Cybercab Production",
      "title": "Robotaxi expands to Miami and Dallas",
      "description": "...",
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
    "criticalNews": "Miami and Dallas launched but fleet stuck at 50 vehicles",
    "newKeyPoint": "July 3: Miami and Dallas robotaxi service launched",
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
    "skipReason": "No significant news for job postings",
    "sourcesSearched": ["optimusk.blog", "linkedin.com"]
  }
}
```

---

## Next Steps After Research

After all researchers complete:

1. **Verify outputs:**
```bash
ls findings-*.json
# Should see 9 files (one per category)
```

2. **Review findings:**
```bash
# Check which categories have news
for f in findings-*.json; do
  echo -n "$f: "
  cat "$f" | python3 -c "import json,sys; d=json.load(sys.stdin); print(f\"{len(d.get('keyChanges',[]))} keyChanges\")"
done
```

3. **Spawn tesla-curator** (next agent):
```
The curator will:
- Load all findings-*.json
- Deduplicate vs last week + URL cache
- Validate sentiment vs reality
- Normalize category names
- Merge into findings/YYYY-MM-DD.json
```

4. **Run merge + deploy:**
```bash
python3 scripts/merge_findings.py findings/YYYY-MM-DD.json
python3 scripts/validate_data.py
npm run build
git add . && git commit && git push
```

---

## Testing Single Category

**Test cybercab research:**

1. Generate config:
```bash
python3 scripts/spawn_researcher.py cybercab
```

2. Manually invoke `/tesla-researcher` skill:
```
Research cybercab category using the config in research-config-cybercab.json
```

3. Check output:
```bash
cat findings-cybercab.json | jq '.keyChanges[] | {title, status}'
```

4. Verify sentiment is critical (not sugar-coated):
```bash
cat findings-cybercab.json | jq '.keyChanges[] | {title, status, reality: .sentiment.reality}'
```

---

## Category Priority & Model Selection

| Priority | Categories | Model | Why |
|----------|-----------|-------|-----|
| **CRITICAL** | Production & Delivery | Sonnet | Quarterly reports, precision matters |
| **HIGH** | Cybercab, FSD, Optimus, FSD v15 | Sonnet | Core business, quality over cost |
| **MEDIUM** | AI Chip, Battery 4680, Terafab | Haiku | Good enough, cost savings |
| **LOW** | Job Postings | Haiku | Simple tracking, low stakes |

**Cost per run:**
- 4 Sonnet agents × $0.02 = $0.08
- 5 Haiku agents × $0.005 = $0.025
- **Total: ~$0.10** (vs $0.02 for sequential)

**Trade-off:** Pay 5x more for 3x speed (worth it for urgent updates).

---

## Critical Sentiment Guidelines

**The agent applies strict rules:**

### Mark as NEGATIVE when:
- Fundamental constraints unsolved (e.g., fleet stuck after 1 year)
- Negative signals outweigh positives (e.g., expansion but ops failing)
- Progress stagnant (<10% growth over 6+ months)

### Mark as NEUTRAL when:
- Mixed signals (e.g., timeline confirmed but "slow ramp")
- Positive headline but concerning reality

### Mark as POSITIVE when:
- Clear progress on fundamentals (e.g., fleet doubles)
- Milestones achieved without caveats

### Reality Check:
"If I owned Tesla stock, would this make me more or less confident?"
- More confident = positive
- Unchanged = neutral
- Less confident = negative

---

## Troubleshooting

**No findings-*.json created:**
- Check agent logs for errors
- Verify config file exists and is valid JSON
- Check URL cache is accessible

**Empty keyChanges:**
- Expected if no news for that category
- Verify metadata.skipReason explains why

**Sentiment seems wrong:**
- Review evidence.negative_signals
- Check if status matches sentiment.reality (not headline)
- File issue if agent is sugar-coating

**Duplicate keyChanges:**
- URL cache might be stale
- Check metadata.urlsSeen vs findings/url-cache.json
- Curator should dedupe these

---

## Integration with Orchestrator

**From /tesla-update-v2 or new parallel skill:**

```python
# Step 1: Generate all configs
os.system("python3 scripts/spawn_researcher.py --all")

# Step 2: Spawn all researchers in parallel
# (see code example above)

# Step 3: Wait for completion
# (check for findings-*.json existence)

# Step 4: Spawn curator
# (next agent - not yet implemented)

# Step 5: Run scripts
os.system("python3 scripts/merge_findings.py findings/YYYY-MM-DD.json")
os.system("npm run build")
# etc.
```

---

## Next: Build tesla-curator Agent

After researchers complete, we need an agent that:
1. Loads all findings-*.json
2. Deduplicates vs last week + URL cache
3. Validates sentiment vs reality
4. Normalizes data
5. Outputs final findings/YYYY-MM-DD.json

See Grok's recommendation #2.
