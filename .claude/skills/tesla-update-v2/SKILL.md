---
name: tesla-update-v2
description: Weekly Tesla research. Nine category agents and a coverage scout run together, a script assembles the draft, and one curator judges the close calls.
---

# Tesla Tracker Update

Orchestrate the weekly research pipeline. Do not research stories yourself.

Agents already have their instructions in `.claude/agents/`. Configs from the spawn scripts carry last week's titles, seen URLs, and ownership.

- Spawn with the short prompts below. Do not paste search queries, schemas, ownership lists, or last week's stories.
- Do not read `data/tesla-tracking-data.json`, `research/findings/url-cache.json`, or a prior `research/findings/YYYY-MM-DD.json`. `spawn_researcher.py --all` prints the date range.
- Do not tell researchers or the curator to open those files.

## Models

`.grok/config.toml` pins `tesla-researcher`, `tesla-coverage-scout`, and `tesla-curator` to `grok-4.7`.

Agent files set reasoning effort: `high` for researchers and the scout, `medium` for the curator. Do not request Haiku, Sonnet, or `grok-4.7-build-fast`. Do not pass a model argument unless the spawn tool lists one.

## Step 1: Configs

```bash
cd /Users/gonzalosolis/Research
python3 scripts/spawn_researcher.py --all
```

This archives any `research/raw/findings-*.json` from the previous run, then writes nine researcher configs and `research/configs/coverage-scout-config.json`.

Use the printed `dateTo` as `$today` for the rest of the run.

## Step 2: Research together

Spawn all nine researchers and the coverage scout in one wave. Do not wait between categories.

Researcher prompt (swap `CATEGORY` only):

```
Research ONLY CATEGORY.

Read research/configs/research-config-CATEGORY.json and write to its outputPath.
Do not read data/tesla-tracking-data.json, research/findings/url-cache.json, or any research/findings/YYYY-MM-DD.json.
Dedup using hotContext.recentKeyChanges and hotContext.seenUrls in the config.
Use web_search, at most 6 searches. Fetch every article URL from a search in the same step.
Do not scrape. Do not call search_tool. Do not run lint_findings.py.
Follow your system instructions for sentiment, ownership, searchLog, and output schema.
```

Categories: `productionDelivery`, `cybercab`, `fsd`, `optimus`, `fsdv15`, `aiChip`, `battery4680`, `terafab`, `jobPostings`.

Scout prompt, spawned with the researchers:

```
Read research/configs/coverage-scout-config.json and write to its outputPath only.
Do not read data/tesla-tracking-data.json, research/findings/, or any research/raw/findings-*.json.
Use web_search, at most 6 searches. Fetch the candidate URLs from each search in the same step. Independent sweep — do not copy category researchers.
```

If this wave hits HTTP 429 often enough that agents stall, the next run uses two waves of five. Do not go back to three waves of three by default.

Wait until nine `research/raw/findings-*.json` files exist. The scout writes `research/logs/$today/coverage.json`. Wait up to about two minutes for it, then continue. A missing scout is recorded as `coverage.status=missing`.

## Step 3: Lint raw, assemble, curate

```bash
python3 scripts/lint_findings.py --raw --date "$today" --write-logs
```

Do not spawn the curator while `MISSING_RAW_FILE` or `INVALID_JSON` remains. Re-run that category first.

`QUERY_CAP` and `SEARCH_TOOL` are warnings. A category that is `empty` with `skipReason` and at least one query is a quiet week. Do not re-research it.

```bash
python3 scripts/spawn_curator.py "$today"
```

That command assembles `research/findings/$today.json` and writes a curator config whose `review` list replaces the full URL cache. Do not lint the draft before the curator. Finalize lints it once.

Curator prompt:

```
Edit the draft described in research/configs/curator-config.json.
Read that config and outputPath. Write reportPath.
Do not rebuild the file from raw findings.
Do not read data/tesla-tracking-data.json, research/findings/url-cache.json, or a prior findings/YYYY-MM-DD.json.
Clear every review.mustFix. Decide every cacheHit and every coverageGap.
web_fetch only coverage-gap URLs, all of them in one step.
Do not grep the repository, the linter, the schema, or memory files.
```

Wait until `research/findings/$today.json` and the curator report exist. Read the report. Check duplicate removals, sentiment flips, gap decisions, and metric drops.

## Step 4: Finalize

```bash
python3 scripts/finalize_update.py research/findings/$today.json
```

This is the one local validation pass: curated lint, merge (no second data validation), URL cache, archive, `validate_data.py`, Zod, and the production build.

Curated lint errors block the merge. Fix the findings file or re-run the curator, then finalize again.

The pre-commit hook runs pytest only. GitHub Actions runs tests, data validation, Zod, and the build again on push.

## Step 5: Commit and push

```bash
git add data/tesla-tracking-data.json \
        research/findings/$today.json \
        research/findings/curator-report-$today.md \
        research/findings/url-cache.json \
        research/logs/$today

git commit -m "Update: Research for $today"
git push origin main
```

Put the key-change count and the curator's validation line in the commit body.

## When something fails

- One researcher fails: the others keep their files. Re-run `python3 scripts/spawn_researcher.py <category>` for the missing one, then lint and curate. Do not re-run `--all`. That archives the files the other agents just wrote.
- Scout fails: continue. Lint records `coverage.status=missing`.
- Curator fails: the draft is still there. Fix the review items and re-run the curator. `spawn_curator.py` rebuilds the draft, so prefer editing the findings file when the draft was already judged.
- Merge fails: the main data file is unchanged. Fix the findings file and finalize again.

## Done

- Nine raw findings files, each with keyChanges or a skipReason, and a searchLog
- Coverage file present, or the ledger says the scout was missing
- No `MISSING_RAW_FILE` or `INVALID_JSON`
- Curator report decides every coverage gap
- Curated lint has zero errors
- Finalize passes and the commit is on `main`
