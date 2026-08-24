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

### Context rules (do not skip)

Agents already have SOPs in `.claude/agents/tesla-researcher.md` and `tesla-curator.md`. Configs from the spawn scripts already carry last week's titles, seen URLs, sources, and ownership.

- Spawn with the short prompts below. Do **not** paste search queries, JSON schemas, ownership lists, or last week's stories into the prompt.
- Do **not** read `data/tesla-tracking-data.json`, `research/findings/url-cache.json`, or a prior `research/findings/YYYY-MM-DD.json` (not even as a writing sample). `spawn_researcher.py --all` prints the date range.
- Do **not** tell researchers or the curator to open those files. Dedup data is in each config as `hotContext.recentKeyChanges` / `lastWeekKeyChanges` and `hotContext.seenUrls`.

---

## Execution Steps

### Step 1: Generate Research Configs

```bash
cd /Users/gonzalosolis/Research
python3 scripts/spawn_researcher.py --all
```

This creates 9 config files:
- `research/configs/research-config-cybercab.json`
- `research/configs/research-config-fsd.json`
- `research/configs/research-config-optimus.json`
- `research/configs/research-config-aiChip.json`
- `research/configs/research-config-battery4680.json`
- `research/configs/research-config-terafab.json`
- `research/configs/research-config-jobPostings.json`
- `research/configs/research-config-productionDelivery.json`
- `research/configs/research-config-fsdv15.json`

### Step 2: Spawn Researcher Agents (Batched)

**IMPORTANT:** Spawn agents in 3 batches of 3 to avoid hitting WebSearch rate limits.

Use this prompt for every category (swap `CATEGORY` only). Do not expand it.

```
Research ONLY CATEGORY.

Read research/configs/research-config-CATEGORY.json and write to its outputPath.
Do not read data/tesla-tracking-data.json, research/findings/url-cache.json, or any research/findings/YYYY-MM-DD.json.
Dedup using hotContext.recentKeyChanges and hotContext.seenUrls in the config.
Follow your system instructions for search, sentiment, ownership, and output schema.
```

**Batch 1 (Critical + High Priority):** `productionDelivery`, `cybercab`, `fsd` (sonnet)

**Batch 2 (High Priority):** `optimus`, `fsdv15` (sonnet); `aiChip` (haiku)

**Batch 3 (Medium + Low Priority):** `battery4680`, `terafab`, `jobPostings` (haiku)

Example (repeat per category, `run_in_background: true`):
```python
Task({
    subagent_type: "tesla-researcher",
    description: "Research productionDelivery",
    prompt: "<template above with CATEGORY=productionDelivery>",
    run_in_background: true
})
```

Wait after each batch before starting the next (3 files after batch 1, 6 after batch 2, 9 after batch 3).

**Expected outputs:** 9 `findings-{category}.json` files

**Estimated time:** 8-12 minutes (batched execution with rate limit protection)

### Step 3: Wait Between Batches

**After each batch, wait for completion:**

```bash
# Wait for batch to complete
expected_count=3  # or 6 for batch 2, or 9 for batch 3
while true; do
    count=$(ls research/raw/findings-*.json 2>/dev/null | wc -l | tr -d ' ')
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
ls research/raw/findings-*.json
# Should see 9 files
```

### Step 4: Generate Curator Config

```bash
python3 scripts/spawn_curator.py
```

This creates `curator-config.json` with:
- List of all research/raw/findings-*.json files
- Slim last-week keyChanges (title/date/category/source/status)
- `seenUrls` (URL strings only — do not open url-cache.json)
- Date and weekOf

### Step 5: Spawn Curator Agent

```python
Task({
    subagent_type: "tesla-curator",
    description: "Validate and merge findings",
    prompt: """
Curate using research/configs/curator-config.json.
Read only that config plus the findingsFiles it lists.
Write research/findings/YYYY-MM-DD.json and research/findings/curator-report-YYYY-MM-DD.md.
Do not read data/tesla-tracking-data.json, research/findings/url-cache.json, or a prior findings/YYYY-MM-DD.json.
Dedup using hotContext.lastWeekKeyChanges and hotContext.seenUrls.
Be critical. Auto-fix status when status=positive but reality=negative.
    """
})
```

**Expected outputs:**
- `research/findings/YYYY-MM-DD.json` (validated findings)
- `research/findings/curator-report-YYYY-MM-DD.md` (validation report)

**Estimated time:** 2-3 minutes

### Step 6: Wait for Curator to Complete

Check that findings file exists:

```bash
# Determine date
today=$(date +%Y-%m-%d)

# Wait for curator
while [ ! -f "research/findings/$today.json" ]; do
    echo "Waiting for curator..."
    sleep 5
done

echo "✓ Curator completed"
```

### Step 7: Review Curator Report

```bash
cat research/findings/curator-report-$(date +%Y-%m-%d).md
```

Check:
- How many duplicates removed?
- Any sentiment corrections?
- Any weak claims rejected?

### Step 8: Finalize (merge → cache → archive → validate → build)

Run the finalization script — this replaces the old manual steps 9–13:

```bash
today=$(date +%Y-%m-%d)
python3 scripts/finalize_update.py research/findings/$today.json
```

This chains: `merge_findings.py` → `update_url_cache.py` → `archive_old_data.py` → `validate_data.py` → `validate-zod-schema.ts` → `npm run build`

If you need to iterate on data before building, use `--skip-build` and run `npm run build` separately.

Optional url-cache cleanup if noise leaked in:
```bash
python3 scripts/update_url_cache.py --prune
```

### Step 9: Commit and Push

```bash
today=$(date +%Y-%m-%d)

# Get summary from findings
summary=$(cat research/findings/$today.json | python3 -c "
import json, sys
findings = json.load(sys.stdin)
kc_count = len(findings['findings']['keyChanges'])
trend_count = len(findings['findings'].get('trends', []))
print(f'{kc_count} key changes, {trend_count} trends')
")

git add data/tesla-tracking-data.json research/findings/$today.json research/findings/url-cache.json

git commit -m "$(cat <<EOF
Update: Batched research for $today

$summary

Research pipeline:
- 9 researchers (3 batches): 9-12 min
- 1 curator (validation): 2-3 min
- Total: ~12-15 min

Validation summary:
$(cat research/findings/curator-report-$today.md | grep -A 10 "validationSummary" | head -5)

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"

git push origin main
```

---

## Error Handling

**If a researcher fails:**
- Other researchers continue (isolation)
- Check which research/raw/findings-*.json are missing
- Re-run failed category: `python3 scripts/spawn_researcher.py <category>`
- Then continue with curator

**If curator fails:**
- Findings files are preserved
- Check curator-report for errors
- Fix issues in research/raw/findings-*.json if needed
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
ls research/raw/findings-*.json 2>/dev/null | wc -l

# Check specific category output
cat research/raw/findings-cybercab.json | python3 -c "import json,sys; print(len(json.load(sys.stdin)['keyChanges']), 'keyChanges')"
```

**After completion:**
```bash
# Review curator report
cat research/findings/curator-report-$(date +%Y-%m-%d).md

# Check final findings
cat research/findings/$(date +%Y-%m-%d).json | python3 -c "
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
- ✅ 9 research/raw/findings-*.json files created
- ✅ Each has keyChanges OR skipReason
- ✅ URLs cached

**Curation phase:**
- ✅ Duplicates removed
- ✅ Sentiment validated (sugar-coating caught)
- ✅ Weak claims rejected
- ✅ research/findings/YYYY-MM-DD.json created

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
research/raw/findings-*.json × 3
  ↓
Batch 2: Spawn 3 tesla-researcher agents
  ↓ 3-4 min
research/raw/findings-*.json × 6 total
  ↓
Batch 3: Spawn 3 tesla-researcher agents
  ↓ 3-4 min
research/raw/findings-*.json × 9 total
  ↓
Generate curator config (spawn_curator.py)
  ↓
Spawn 1 tesla-curator agent
  ↓ 2-3 min
research/findings/YYYY-MM-DD.json (validated)
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
