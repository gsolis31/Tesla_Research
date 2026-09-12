# Pipeline tests

Unit tests for Python merge / research pipeline logic.

## Run

```bash
# from repo root
python3 -m pytest
# or
npm test

# merge tests only
npm run test:merge
```

Requires `pytest` (`pip3 install -r requirements.txt`).

## What’s covered

`test_merge_findings.py` — regression tests for bugs we’ve hit in production:

- KeyChange dedupe (prefer richer evidence)
- Registration points re-routed off `robotaxiFleet` → `robotaxiRegistered`
- Quarter key normalization (`Q2 2026` ≡ `Q2-26`)
- P&D total recalculation
- Category updates (`latestStatus` → criticalNews, keyPoint caps, fsdv15)
- Weekly summary append vs new week

`test_lint_findings.py` — gold-set evals for `scripts/lint_findings.py` (fixtures in `tests/evals/`):

- Sep 6: Texas registration dumped as production/fleet (must error)
- Aug 22: Nevada permit `status=positive` / `reality=neutral` (must warn)
- Empty week with `searchLog` passes; empty without `searchLog` fails
- Electrek-only+low, stale date, noise source URL, ownership trespass
- Curated package still carrying `robotaxiFleet` registry counts fails
- `run.json` ledger merges researcher + curator stages

`test_coverage_scout.py` — recall diff for tesla-coverage-scout:

- Same-URL and similar-title stories are covered (not gaps)
- Researcher `considered` skips count as covered
- `seenUrls` / last-week titles are covered
- Unmatched NHTSA / AI5 stories are gaps
- Homepage noise is ignored, not a gap
- Missing `coverage.json` is `status=missing`, not a lint error

These tests use in-memory fixtures only (no network, no LLM, no writing production data).

```bash
npm run test:lint    # lint evals only
```
