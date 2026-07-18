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

These tests use in-memory fixtures only (no network, no LLM, no writing production data).
