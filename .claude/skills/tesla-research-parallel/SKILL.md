---
name: tesla-research-parallel
description: "[DEPRECATED] Use tesla-update-v2 instead - this hits rate limits"
user-invocable: false
allowed-tools: WebSearch, Read, Write, Bash, Task
---

# ⚠️ DEPRECATED: Tesla Parallel Research Skill

**Status:** DEPRECATED as of July 12, 2026
**Reason:** Hits WebSearch rate limits due to unbatched parallel execution
**Replacement:** Use `/tesla-update-v2` instead (batched execution prevents rate limits)

---

## What This Did

Researched multiple Tesla categories **in parallel** using subagents, then merged findings.

**Before** (sequential):
```
Research Category 1 (5min)
  ↓
Research Category 2 (5min)
  ↓
Research Category 3 (5min)
  ↓
Total: 15 minutes
```

**After** (parallel):
```
Research Category 1 ─┐
Research Category 2 ─┼─→ Merge
Research Category 3 ─┘
Total: 5-6 minutes (3x faster)
```

---

## Execution Steps

### Step 1: Determine Research Scope

```python
from datetime import datetime
import json

# Load current state
data = json.load(open('/Users/gonzalosolis/Research/tesla-tracking-data.json'))
last_updated = data['lastUpdated']
today = datetime.now().strftime('%Y-%m-%d')

print(f"Research period: {last_updated} → {today}")
```

**Categories to research**:
1. AI Chip Production (priority: medium)
2. 4680 Battery Cell Production (priority: medium)
3. Cybercab Production (priority: HIGH)
4. FSD Country Approvals (priority: HIGH)
5. Job Postings (priority: low)
6. Optimus Production (priority: HIGH)
7. Vehicle Production & Delivery (priority: CRITICAL)
8. Terafab Manufacturing (priority: medium)
9. FSD v15 Software (priority: HIGH)

**Parallel strategy**:
- Launch HIGH/CRITICAL categories first (6 agents)
- Launch MEDIUM categories second (3 agents)
- LOW categories run last or skip if time-constrained

### Step 2: Launch Parallel Research Agents

For each **HIGH/CRITICAL** category, launch a subagent using the Task tool:

```typescript
// Example: Launch Cybercab research agent
Task({
  subagent_type: "general-purpose",
  description: "Research Cybercab Production",
  prompt: `
Research Task: Cybercab Production

Period: ${last_updated} → ${today}

Hot Context:
- Last update: ${data.categories.cybercab.latestUpdate}
- Critical news: ${data.categories.cybercab.criticalNews}
- Latest fleet count: ${data.metrics.robotaxiFleet.data.slice(-1)[0]}

Sources (Tier 1):
- teslarati.com
- robotaxitracker.com
- teslanorth.com

Keywords: Cybercab, robotaxi, fleet, autonomous, FSD

Your Task:
1. Search each Tier 1 source for news since ${last_updated}
2. For each URL found:
   - Check cache: python3 scripts/url_cache.py check "<url>"
   - Skip if exit code = 0 (already seen)
3. Extract keyChanges with full sentiment + evidence
4. Find latest fleet count from robotaxitracker.com
5. Write output to: findings-cybercab.json

Output Format:
{
  "categoryKey": "cybercab",
  "keyChanges": [...],
  "metricUpdate": { "date": "${today}", "count": X, "note": "..." },
  "fleetUpdate": { "date": "${today}", "count": X, "note": "..." },
  "categoryUpdate": {
    "criticalNews": "...",
    "newKeyPoint": "..."
  },
  "urlsSeen": [...]
}
  `,
  run_in_background: true  // Run in parallel
})
```

**Launch 6-9 agents in parallel** (one per category), all with `run_in_background: true`.

### Step 3: Monitor Agent Progress

```bash
# Check on running agents
/tasks

# Read agent output
tail -f /tmp/task-{agent-id}.log
```

**Estimated time per agent**: 3-5 minutes

### Step 4: Wait for Completion

Poll for agent completion or wait for notifications.

Once all agents finish, proceed to merge.

### Step 5: Merge Category Findings

```bash
python3 scripts/parallel_research.py --date ${today} --merge-only
```

This will:
- Load all `findings-{category}.json` files
- Merge into single `findings/YYYY-MM-DD.json`
- Deduplicate URLs
- Combine metrics

**Output**: `findings/2026-07-08.json`

### Step 6: Run Standard Merge Pipeline

```bash
# Merge findings into main data
python3 scripts/merge_findings.py findings/2026-07-08.json

# Update URL cache
for url in $(cat findings/2026-07-08.json | python3 -c "
import json, sys
for url in json.load(sys.stdin)['metadata']['urlsSeen']:
    print(url)
"); do
  python3 scripts/url_cache.py add "$url" "Category" "Title"
done

# Archive
python3 scripts/archive_old_data.py

# Build
npm run build

# Commit + push
git add tesla-tracking-data.json findings/2026-07-08.json
git commit -m "Update: Parallel research for 2026-07-08 (9 categories)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
git push origin main
```

---

## Category Research Templates

### High-Priority Categories

**Cybercab Production**:
- Sources: robotaxitracker.com, teslarati.com, teslanorth.com
- Focus: Fleet counts, city deployments, production numbers
- Metrics: robotaxiFleet, cybercab

**FSD Country Approvals**:
- Sources: teslarati.com, teslanorth.com, teslaoracle.com
- Focus: New country approvals, regulatory updates
- Metrics: fsdApprovals.countries

**Optimus Production**:
- Sources: optimusk.blog, teslarati.com, teslanorth.com
- Focus: Production milestones, facility updates
- Metrics: None (category updates only)

**Vehicle Production & Delivery** (CRITICAL):
- Sources: ir.tesla.com/press (ONLY official source)
- Focus: Quarterly reports (Q1, Q2, Q3, Q4)
- Metrics: quarterlyData

### Medium-Priority Categories

**AI Chip Production**:
- Sources: teslarati.com, teslanorth.com
- Keywords: AI5, AI6, Samsung, TSMC, Dojo

**Terafab Manufacturing**:
- Sources: teslarati.com, teslanorth.com
- Keywords: Terafab, North Campus, chip fab

**4680 Battery**:
- Sources: teslarati.com, teslanorth.com
- Keywords: 4680, battery cell, GWh, yield

### Low-Priority Categories

**Job Postings**:
- Sources: optimusk.blog, LinkedIn, Tesla careers
- Focus: Optimus-related hiring trends
- Metrics: jobPostings

**FSD v15 Software**:
- Sources: teslarati.com, teslanorth.com
- Focus: Development timeline, testing updates

---

## Parallel Execution Best Practices

### 1. Agent Independence

Each agent should:
- ✅ Read only its hot context (not full JSON)
- ✅ Write to its own findings file
- ✅ Use URL cache independently
- ❌ NOT depend on other agents' results

### 2. Error Handling

If an agent fails:
- Other agents continue
- Missing category = empty findings for that category
- Can re-run failed category separately

### 3. Resource Limits

**Recommended**:
- Max 6-9 parallel agents (one per category)
- Use Haiku model for LOW priority categories (cost savings)
- Use Sonnet for HIGH/CRITICAL categories (quality)

**Model selection**:
```typescript
Task({
  model: "haiku",  // For Job Postings, 4680 Battery
  // or
  model: "sonnet", // For Cybercab, FSD, P&D
})
```

### 4. Cost Optimization

**Sequential V2** (~$0.02/run):
- 9 categories × sequential = ~$0.02

**Parallel V3** (~$0.05/run):
- 9 categories × parallel × overhead = ~$0.05
- **BUT** 3x faster (5min vs 15min)

**Trade-off**: Pay 2.5x more for 3x speed

---

## Fallback to Sequential

If parallel execution fails or is too expensive:

```bash
# Run V2 (sequential but optimized)
/tesla-update-v2
```

V2 is still 87% cheaper than V1, just slower than V3.

---

## Example Invocation

```
User: /tesla-research-parallel
```

**Expected behavior**:
1. Determine research scope (9 categories)
2. Launch 9 parallel agents (6 HIGH, 3 MEDIUM)
3. Wait for completion (5-6 minutes)
4. Merge category findings
5. Run standard merge pipeline
6. Build + commit + push
7. Report summary

---

## Success Metrics

**V1** (sequential god-file):
- Time: ~20-30 min
- Cost: ~$0.15
- Context: 167KB

**V2** (sequential findings):
- Time: ~15-20 min
- Cost: ~$0.02
- Context: 10KB

**V3** (parallel findings):
- Time: ~5-6 min (3x faster than V2)
- Cost: ~$0.05 (2.5x more than V2)
- Context: 10KB per agent

**Best for**:
- V2: Regular weekly updates (cost-optimized)
- V3: Urgent updates, catching up after delays (speed-optimized)

---

## Limitations

### Current
- Task tool coordination is manual
- No automatic retry on agent failure
- No progress streaming from agents

### Future Improvements
- Auto-retry failed categories
- Real-time progress dashboard
- Smart agent allocation (prioritize categories with recent activity)
- Adaptive parallelism (scale up/down based on news volume)
