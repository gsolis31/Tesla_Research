---
name: tesla-update
description: "RETIRED — use /tesla-update-v2 instead"
user-invocable: true
allowed-tools: Read
---

# ⚠️ This skill is retired

Use `/tesla-update-v2` for all updates — low-news weeks included.

**Why retired:**
- V1 edited `data/tesla-tracking-data.json` directly, bypassing `merge_findings.py`,
  the URL cache, growth caps, and deduplication.
- V2 handles low-news weeks just fine; it simply finds fewer findings to merge.
- Two update paths → inconsistent quality gates and non-auditable history.

**Migration:**
```
/tesla-update-v2
```
