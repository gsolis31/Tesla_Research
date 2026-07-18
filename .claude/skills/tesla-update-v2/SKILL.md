---
name: tesla-update-v2
description: Fast batched Tesla research with agents - 2x faster than V1 (12-15 min vs 20-30 min)
user-invocable: true
allowed-tools: Read, Write, Bash, Task
---

# Tesla Tracker Update Skill V2 (Batched Agent Orchestrator)

## ⚠️ When to Use This vs V1

**Use this (V2) when:**
- ✅ Urgent update needed (2x faster than V1)
- ✅ Catching up after 2+ weeks
- ✅ Major news events (earnings, product launch)
- ✅ Multiple categories likely have news

**Use /tesla-update (V1) when:**
- ✅ Low-news week (only 1-2 categories need updates)
- ✅ Small update (catching up 1-3 days)
- ✅ You prefer simplicity over speed

---

## What This Does

**Orchestrates batched research pipeline:**
1. Spawns 9 `tesla-researcher` agents in 3 batches of 3 (one per category)
2. Spawns 1 `tesla-curator` agent to validate/merge findings
3. Runs merge/validate/build/deploy scripts
4. Commits and pushes to GitHub

**Time:** 12-15 minutes (2x faster than V1)

**This skill does NOT do research itself** - it coordinates the agents.

**Why batched?** Prevents WebSearch rate limit exhaustion (9 agents × 10 searches = 90 calls).

---

## Execution Steps

### Step 1: Determine Research Period

```python
from datetime import datetime, timedelta
import json

# Load current data
data = json.load(open('/Users/gonzalosolis/Research/tesla-tracking-data.json'))
last_updated = data['lastUpdated']
today = datetime.now().strftime('%Y-%m-%d')

# Calculate Monday of current week
now = datetime.now()
monday = now - timedelta(days=now.weekday())
week_of = monday.strftime('%Y-%m-%d')

print(f"Research period: {last_updated} → {today}")
print(f"Week of: {week_of}")
```

### Step 2: Generate Research Configs

```bash
cd /Users/gonzalosolis/Research
python3 scripts/spawn_researcher.py --all
```

This creates 9 config files:
- `research-config-cybercab.json`
- `research-config-fsd.json`
- `research-config-optimus.json`
- `research-config-aiChip.json`
- `research-config-battery4680.json`
- `research-config-terafab.json`
- `research-config-jobPostings.json`
- `research-config-productionDelivery.json`
- `research-config-fsdv15.json`

### Step 3: Spawn Researcher Agents (Batched)

**IMPORTANT:** Spawn agents in 3 batches of 3 to avoid hitting WebSearch rate limits.

**Batch 1 (Critical + High Priority):**
```python
# Spawn 3 high-priority agents in parallel
Task({
    subagent_type: "tesla-researcher",
    description: "Research productionDelivery",
    model: "sonnet",
    prompt: "...",
    run_in_background: true
})
Task({
    subagent_type: "tesla-researcher",
    description: "Research cybercab",
    model: "sonnet",
    prompt: "...",
    run_in_background: true
})
Task({
    subagent_type: "tesla-researcher",
    description: "Research fsd",
    model: "sonnet",
    prompt: "...",
    run_in_background: true
})
```

Wait for batch 1 to complete (check for 3 findings-*.json files).

**Batch 2 (High Priority):**
```python
# Spawn next 3 high-priority agents
Task({
    subagent_type: "tesla-researcher",
    description: "Research optimus",
    model: "sonnet",
    prompt: "...",
    run_in_background: true
})
Task({
    subagent_type: "tesla-researcher",
    description: "Research fsdv15",
    model: "sonnet",
    prompt: "...",
    run_in_background: true
})
Task({
    subagent_type: "tesla-researcher",
    description: "Research aiChip",
    model: "haiku",
    prompt: "...",
    run_in_background: true
})
```

Wait for batch 2 to complete (check for 6 findings-*.json files total).

**Batch 3 (Medium + Low Priority):**
```python
# Spawn final 3 agents
Task({
    subagent_type: "tesla-researcher",
    description: "Research battery4680",
    model: "haiku",
    prompt: "...",
    run_in_background: true
})
Task({
    subagent_type: "tesla-researcher",
    description: "Research terafab",
    model: "haiku",
    prompt: "...",
    run_in_background: true
})
Task({
    subagent_type: "tesla-researcher",
    description: "Research jobPostings",
    model: "haiku",
    prompt: "...",
    run_in_background: true
})
```

Wait for batch 3 to complete (check for 9 findings-*.json files total).

**Expected outputs:** 9 `findings-{category}.json` files

**Estimated time:** 8-12 minutes (batched execution with rate limit protection)

### Step 4: Wait Between Batches

**After each batch, wait for completion:**

```bash
# Wait for batch to complete
expected_count=3  # or 6 for batch 2, or 9 for batch 3
while true; do
    count=$(ls findings-*.json 2>/dev/null | wc -l | tr -d ' ')
    if [ "$count" -ge $expected_count ]; then
        echo "✓ Batch completed ($count/$expected_count files)"
        break
    fi
    echo "Waiting for batch... ($count/$expected_count complete)"
    sleep 15
done
```

**Check final completion:**
```bash
ls findings-*.json
# Should see 9 files
```

### Step 5: Generate Curator Config

```bash
python3 scripts/spawn_curator.py
```

This creates `curator-config.json` with:
- List of all findings-*.json files
- Last week's keyChanges (for deduplication)
- URL cache path
- Date and weekOf

### Step 6: Spawn Curator Agent

Use the Task tool to spawn curator:

```python
Task({
    subagent_type: "tesla-curator",
    description: "Validate and merge findings",
    model: "sonnet",  # Always use Sonnet for quality
    prompt: """
Curate the research findings from all categories.

Use the configuration file: curator-config.json

This file contains:
- All findings-{category}.json files to merge
- Last week's keyChanges for deduplication
- URL cache for checking seen URLs

Your tasks:
1. Load all category findings
2. Deduplicate vs last week + URL cache
3. Validate sentiment (catch sugar-coating, auto-correct)
4. Refuse weak claims (Electrek-only + low confidence)
5. Normalize data (category names, dates, confidence)
6. Extract trends
7. Merge metrics and category updates
8. Write findings/YYYY-MM-DD.json
9. Generate validation report

Be critical. Auto-fix sentiment when status=positive but reality=negative.
    """
})
```

**Expected outputs:**
- `findings/YYYY-MM-DD.json` (validated findings)
- `findings/curator-report-YYYY-MM-DD.md` (validation report)

**Estimated time:** 2-3 minutes

### Step 7: Wait for Curator to Complete

Check that findings file exists:

```bash
# Determine date
today=$(date +%Y-%m-%d)

# Wait for curator
while [ ! -f "findings/$today.json" ]; do
    echo "Waiting for curator..."
    sleep 5
done

echo "✓ Curator completed"
```

### Step 8: Review Curator Report

```bash
cat findings/curator-report-$(date +%Y-%m-%d).md
```

Check:
- How many duplicates removed?
- Any sentiment corrections?
- Any weak claims rejected?

### Step 9: Run Merge Script

```bash
today=$(date +%Y-%m-%d)
python3 scripts/merge_findings.py findings/$today.json
```

This merges the validated findings into `tesla-tracking-data.json`.

### Step 10: Update URL Cache

Cache **canonical article source URLs only** (from accepted keyChanges). Do not dump search/feed/homepage URLs.

```bash
today=$(date +%Y-%m-%d)
python3 scripts/update_url_cache.py findings/$today.json
```

Optional cleanup if noise leaked into the cache:
```bash
python3 scripts/update_url_cache.py --prune
```

### Step 11: Archive Old Data

```bash
python3 scripts/archive_old_data.py
```

Keeps current + previous year in main file, archives the rest.

### Step 12: Validate Merged Data

```bash
python3 scripts/validate_data.py
```

This runs comprehensive validation. Must pass before proceeding.

### Step 13: Build

```bash
npm run build
```

Build will fail if validation errors exist.

### Step 14: Commit and Push

```bash
today=$(date +%Y-%m-%d)

# Get summary from findings
summary=$(cat findings/$today.json | python3 -c "
import json, sys
findings = json.load(sys.stdin)
kc_count = len(findings['findings']['keyChanges'])
trend_count = len(findings['findings'].get('trends', []))
print(f'{kc_count} key changes, {trend_count} trends')
")

git add tesla-tracking-data.json findings/$today.json findings/url-cache.json dist/

git commit -m "$(cat <<EOF
Update: Batched research for $today

$summary

Research pipeline:
- 9 researchers (3 batches): 9-12 min
- 1 curator (validation): 2-3 min
- Total: ~12-15 min

Validation summary:
$(cat findings/curator-report-$today.md | grep -A 10 "validationSummary" | head -5)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"

git push origin main
```

---

## Error Handling

**If a researcher fails:**
- Other researchers continue (isolation)
- Check which findings-*.json are missing
- Re-run failed category: `python3 scripts/spawn_researcher.py <category>`
- Then continue with curator

**If curator fails:**
- Findings files are preserved
- Check curator-report for errors
- Fix issues in findings-*.json if needed
- Re-run curator: `python3 scripts/spawn_curator.py`

**If merge fails:**
- Findings preserved
- Main data unchanged
- Debug merge separately
- Re-run after fixing

---

## Cost & Performance

**V1 (old god-file):**
- Time: 20-30 min
- Cost: ~$0.15
- Context: 167KB

**V2 (batched agents):**
- Time: 12-15 min (3 batches × 3-4 min each + curator 2-3 min)
- Cost: ~$0.10 (5 Sonnet × $0.02 + 4 Haiku × $0.005 + curator $0.02)
- Context: 10KB per agent
- Rate limits: Safe (spreads WebSearch calls across batches)

**Trade-off:** Pay ~67% of V1 cost for 2x speed improvement + rate limit safety.

---

## When to Use

**Use V2 (batched) when:**
- ✅ Urgent update needed
- ✅ Catching up after 2+ weeks
- ✅ Major news events (earnings, product launch)
- ✅ Multiple categories likely have news

**Don't use V2 when:**
- ❌ Low-news week (many categories will be empty)
- ❌ Only 1-2 categories need update (use researcher directly)

**Why batched execution?**
- Prevents hitting WebSearch rate limits
- 9 agents × 10 searches = 90 WebSearch calls
- Batching spreads calls over time (30 searches per batch)

---

## Monitoring Progress

**During execution:**
```bash
# Check running agents
/tasks

# Count completed researchers
ls findings-*.json 2>/dev/null | wc -l

# Check specific category output
cat findings-cybercab.json | python3 -c "import json,sys; print(len(json.load(sys.stdin)['keyChanges']), 'keyChanges')"
```

**After completion:**
```bash
# Review curator report
cat findings/curator-report-$(date +%Y-%m-%d).md

# Check final findings
cat findings/$(date +%Y-%m-%d).json | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(f\"keyChanges: {len(d['findings']['keyChanges'])}\")
print(f\"trends: {len(d['findings']['trends'])}\")
print(f\"duplicates removed: {d['metadata']['validationSummary']['duplicatesRemoved']}\")
print(f\"sentiment corrected: {d['metadata']['validationSummary']['sentimentCorrected']}\")
"
```

---

## Success Criteria

**Research phase:**
- ✅ 9 findings-*.json files created
- ✅ Each has keyChanges OR skipReason
- ✅ URLs cached

**Curation phase:**
- ✅ Duplicates removed
- ✅ Sentiment validated (sugar-coating caught)
- ✅ Weak claims rejected
- ✅ findings/YYYY-MM-DD.json created

**Deployment phase:**
- ✅ Validation passes
- ✅ Build succeeds
- ✅ Committed and pushed
- ✅ Live site updated

---

## Example Invocation

```
User: /tesla-update-v2
```

Expected behavior:
1. Generate research configs (9 files)
2. Spawn batch 1 (3 researchers) - Wait 3-4 min
3. Spawn batch 2 (3 researchers) - Wait 3-4 min
4. Spawn batch 3 (3 researchers) - Wait 3-4 min
5. Generate curator config
6. Spawn curator - Wait 2-3 minutes
7. Run merge/validate/build/deploy
8. Commit + push
9. Report summary to user

Total time: ~12-15 minutes (vs 20-30 min in V1, avoids rate limits)

---

## Architecture

```
/tesla-update-v2 (orchestrator skill)
  ↓
Generate configs (spawn_researcher.py --all)
  ↓
Batch 1: Spawn 3 tesla-researcher agents
  ↓ 3-4 min
findings-*.json × 3
  ↓
Batch 2: Spawn 3 tesla-researcher agents
  ↓ 3-4 min
findings-*.json × 6 total
  ↓
Batch 3: Spawn 3 tesla-researcher agents
  ↓ 3-4 min
findings-*.json × 9 total
  ↓
Generate curator config (spawn_curator.py)
  ↓
Spawn 1 tesla-curator agent
  ↓ 2-3 min
findings/YYYY-MM-DD.json (validated)
  ↓
Run scripts (merge, validate, archive, build)
  ↓
Commit + push
  ↓
✅ Done
```

---

## Related Documentation

- `SCHEMA_BOUND_ARCHITECTURE.md` - Grok #1 (schema-bound findings)
- `VALIDATION_UPGRADE.md` - Grok #2 (validation system)
- `PARALLEL_RESEARCH.md` - Grok #3 (parallel pipeline)
- `.claude/skills/tesla-researcher/` - Category research agent
- `.claude/skills/tesla-curator/` - Quality gate agent
- `scripts/spawn_researcher.py` - Config generator
- `scripts/spawn_curator.py` - Curator config generator
