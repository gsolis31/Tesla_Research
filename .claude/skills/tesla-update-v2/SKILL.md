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
2. Spawns 1 `tesla-coverage-scout` with batch 3 (independent recall check)
3. Spawns 1 `tesla-curator` agent to validate/merge findings and address coverage gaps
4. Runs merge/validate/build/deploy scripts
5. Commits and pushes to GitHub

**Time:** 12-15 minutes (2x faster than V1)

**This skill does NOT do research itself** - it coordinates the agents.

**Why batched?** Prevents WebSearch rate limit exhaustion (9 agents × 10 searches = 90 calls).

### Context rules (do not skip)

Agents already have SOPs in `.claude/agents/tesla-researcher.md`, `tesla-coverage-scout.md`, and `tesla-curator.md`. Configs from the spawn scripts already carry last week's titles, seen URLs, sources, and ownership.

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

This creates 9 researcher configs plus `research/configs/coverage-scout-config.json`.

Researcher configs:
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
On Grok, call web_search not search_tool.
Follow your system instructions for search, sentiment, ownership, searchLog, and output schema.
```

**Batch 1 (Critical + High Priority):** `productionDelivery`, `cybercab`, `fsd` (sonnet)

**Batch 2 (High Priority):** `optimus`, `fsdv15` (sonnet); `aiChip` (haiku)

**Batch 3 (Medium + Low Priority):** `battery4680`, `terafab`, `jobPostings` (haiku)

**With batch 3, spawn the coverage scout (sonnet).** Do not wait for batch 3 researchers to finish first — it must not read `research/raw/`.

```
Read research/configs/coverage-scout-config.json and write to its outputPath only.
Do not read data/tesla-tracking-data.json, research/findings/, or any research/raw/findings-*.json.
On Grok, call web_search not search_tool.
Follow your system instructions. Independent sweep — do not copy category researchers.
```

```python
Task({
    subagent_type: "tesla-coverage-scout",
    description: "Coverage scout",
    prompt: "<template above>",
    run_in_background: true
})
```

Example (repeat per category, `run_in_background: true`):
```python
Task({
    subagent_type: "tesla-researcher",
    description: "Research productionDelivery",
    prompt: "<template above with CATEGORY=productionDelivery>",
    run_in_background: true
})
```

Wait after each batch before starting the next (3 files after batch 1, 6 after batch 2, 9 after batch 3). Scout runs during batch 3.

**Expected outputs:** 9 `findings-{category}.json` files + `research/logs/$today/coverage.json`

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

today=$(date +%Y-%m-%d)
# Scout started with batch 3; wait up to ~2 min, then continue without it
for i in 1 2 3 4 5 6 7 8; do
    [ -f "research/logs/$today/coverage.json" ] && break
    echo "Waiting for coverage scout... ($i/8)"
    sleep 15
done
if [ ! -f "research/logs/$today/coverage.json" ]; then
    echo "⚠ coverage.json missing — lint will record coverage.status=missing"
fi
```

### Step 3b: Lint raw findings + write run ledger (required)

```bash
today=$(date +%Y-%m-%d)
python3 scripts/lint_findings.py --raw --date "$today" --write-logs
```

Writes `research/logs/$today/`:
- `lint-raw.json` — mechanical errors/warnings per category
- `{category}.json` — extracted `searchLog`
- `run.json` — per-agent status (ok / empty / lint_error / missing)

**Do not spawn the curator while `MISSING_RAW_FILE` or `INVALID_JSON` errors remain.** Re-run the failed category first.

Other raw lint errors (`REGISTRATION_AS_FLEET`, `OWNERSHIP_TRESPASS`, `STALE_DATE`, `ELECTREK_ONLY_LOW`, `MISSING_SEARCH_LOG`, …) go to the curator as must-drops via `lintReport`. Warnings (`STATUS_AHEAD_OF_REALITY`, `TITLE_TOO_LONG`) are curator judgment.

If a category is `empty` with `skipReason` and `queries >= 1` in `run.json`, that is a valid quiet week — do not re-research it just because it filed nothing.

### Step 4: Generate Curator Config

```bash
python3 scripts/spawn_curator.py
```

This creates `curator-config.json` with:
- List of all research/raw/findings-*.json files
- Slim last-week keyChanges (title/date/category/source/status)
- `seenUrls` (URL strings only — do not open url-cache.json)
- `lintReport` / `logsDir` (raw lint from Step 3b)
- `coverageGaps` (unmatched scout stories; empty if scout did not run)
- Date and weekOf

### Step 5: Spawn Curator Agent

```python
Task({
    subagent_type: "tesla-curator",
    description: "Validate and merge findings",
    prompt: """
Curate using research/configs/curator-config.json.
Read that config, the findingsFiles it lists, and lintReport if the file exists.
Write research/findings/YYYY-MM-DD.json and research/findings/curator-report-YYYY-MM-DD.md.
Do not read data/tesla-tracking-data.json, research/findings/url-cache.json, or a prior findings/YYYY-MM-DD.json.
Dedup using hotContext.lastWeekKeyChanges and hotContext.seenUrls.
Honor lint-raw errors as must-drops. Address every coverageGap (file after web_fetch, or reject with reason).
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

Lint the curated package and update the run ledger:

```bash
today=$(date +%Y-%m-%d)
python3 scripts/lint_findings.py --curated research/findings/$today.json --date "$today" --write-logs
```

Curated **errors** block finalize (registration still in `robotaxiFleet`, title still >120, stale dates). Fix the findings file or re-run the curator before Step 8.

### Step 7: Review Curator Report

```bash
cat research/findings/curator-report-$(date +%Y-%m-%d).md
```

Check:
- How many duplicates removed?
- Any sentiment corrections?
- Any weak claims rejected?
- `research/logs/$today/run.json` — which categories are `ok` / `empty` / `lint_error`
- Raw lint errors the curator dropped (especially `REGISTRATION_AS_FLEET`)
- Coverage gaps in `run.json` / curator report (filed vs rejected)

### Step 8: Finalize (merge → cache → archive → validate → build)

Run the finalization script — this replaces the old manual steps 9–13:

```bash
today=$(date +%Y-%m-%d)
python3 scripts/finalize_update.py research/findings/$today.json
```

This chains: `lint_findings.py --curated` → `merge_findings.py` → `update_url_cache.py` → `archive_old_data.py` → `validate_data.py` → `validate-zod-schema.ts` → `npm run build`

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

git add data/tesla-tracking-data.json \
        research/findings/$today.json \
        research/findings/url-cache.json \
        research/logs/$today

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

**If the coverage scout fails:**
- Continue. Lint records `coverage.status=missing`
- Curator `coverageGaps` will be empty — note it in the user summary
- Optional re-run: `python3 scripts/spawn_researcher.py --scout` then re-lint --raw

**If curator fails:**
- Findings files are preserved
- Check curator-report for errors
- Fix issues in research/raw/findings-*.json if needed
- Re-run curator: `python3 scripts/spawn_curator.py`

**If raw lint fails (`MISSING_RAW_FILE` / `INVALID_JSON`):**
- Do not spawn curator
- Re-run the missing category, then `lint_findings.py --raw --write-logs`

**If curated lint fails (finalize Step 8):**
- Findings preserved; main data unchanged
- Check `research/logs/$today/lint-curated.json`
- Fix the curated file or re-run curator, then finalize again

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
- Time: 12-15 min (3 batches × 3-4 min each, scout overlaps batch 3, + curator 2-3 min)
- Cost: ~$0.12 (5 Sonnet researchers + 1 scout + curator + 4 Haiku)
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
today=$(date +%Y-%m-%d)

# Per-category status (ok / empty / lint_error / missing)
python3 -c "
import json, sys
d = json.load(open(sys.argv[1]))
for k, v in (d.get('agents') or {}).items():
    print(f\"{k:20} {v['status']:11} filed={v['filed']} queries={v['queries']} err={v['lintErrors']}\")
print('curator', d.get('curator'))
print('coverage', d.get('coverage'))
" research/logs/$today/run.json

cat research/findings/curator-report-$today.md
```

---

## Success Criteria

**Research phase:**
- ✅ 9 research/raw/findings-*.json files created
- ✅ Each has keyChanges OR skipReason
- ✅ Each has `searchLog.queries` (quiet weeks too)
- ✅ Coverage scout wrote `research/logs/YYYY-MM-DD/coverage.json` (or ledger says missing)
- ✅ `research/logs/YYYY-MM-DD/run.json` written
- ✅ No `MISSING_RAW_FILE` / `INVALID_JSON`

**Curation phase:**
- ✅ Duplicates removed
- ✅ Sentiment validated (sugar-coating caught)
- ✅ Lint-raw errors dropped (especially registration-as-fleet)
- ✅ Every coverageGap filed or rejected with reason
- ✅ Curated lint has 0 errors
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
4. Spawn batch 3 (3 researchers) + coverage scout - Wait 3-4 min
5. Lint raw (includes coverage diff) + write `research/logs/YYYY-MM-DD/run.json`
6. Generate curator config
7. Spawn curator - Wait 2-3 minutes
8. Lint curated (blocks finalize on errors)
9. Run merge/validate/build/deploy
10. Commit + push (includes `research/logs/YYYY-MM-DD/`)
11. Report summary to user

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
         + tesla-coverage-scout (parallel, does not read raw/)
  ↓ 3-4 min
research/raw/findings-*.json × 9 total
research/logs/YYYY-MM-DD/coverage.json
  ↓
lint_findings.py --raw --write-logs
  (diffs scout vs researchers → coverage-gaps.json)
  ↓
Generate curator config (spawn_curator.py)
  ↓
Spawn 1 tesla-curator agent
  ↓ 2-3 min
research/findings/YYYY-MM-DD.json (validated)
  ↓
lint_findings.py --curated --write-logs
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
- `scripts/lint_findings.py` - Mechanical quality gate + coverage diff + run ledger
- `tests/evals/` - Frozen gold cases (Sep 6 registration-as-fleet, Aug 22 Nevada, coverage gaps)
