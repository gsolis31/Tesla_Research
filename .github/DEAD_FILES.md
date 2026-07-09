# Dead Files & Obsolete Documentation

These files are no longer used and should be deleted or updated:

## ❌ Dead Workflows

### `.github/workflows/tesla-update.yml`
- **Status**: Dead (references non-existent `scripts/auto_update.py`)
- **Problem**: Tries to run automated updates via GitHub Actions
- **Reality**: The `/tesla-update` skill in Claude Code is the only working update method
- **Action**: Delete this file or update to trigger Claude Code remotely

## ⚠️ Obsolete Documentation

### `AUTOMATION_SETUP.md`
- **Status**: Partially obsolete
- **Problem**: References old HTML embed workflow, outdated automation setup
- **Action**: Update to reflect React/Vite architecture and new validation system

### `README.md` (Sections to Update)
- Lines mentioning "Sync index.html" - no longer exists
- Automation claims that don't match reality (says skill commits/pushes, but it doesn't)

## 🔧 Legacy Scripts

### `scripts/validate_legacy.py` (renamed from `validate.py`)
- **Status**: Obsolete (checks for `index.html` DATA_OBJECT markers)
- **Replacement**: `scripts/validate_data.py` (works with React/Vite)
- **Action**: Keep for reference, but don't use

### Missing Script Referenced in Workflow
- **File**: `scripts/auto_update.py`
- **Status**: Never existed or was deleted
- **References**: `.github/workflows/tesla-update.yml:34`
- **Action**: Either create it or delete the workflow

## 📝 Documentation Debt

### `.claude/skills/tesla-update/SKILL.md`
- Line 24-28: Mentions "Sync the embedded data in index.html" (no longer exists)
- Line 435-441: Says "Open dashboard in browser" but doesn't commit/push
- Line 397-416: References archive script but skill never calls it
- **Action**: Update to match new validation workflow and automation reality

## Cleanup Commands

```bash
# Delete dead workflow
rm .github/workflows/tesla-update.yml

# Delete legacy validation
rm scripts/validate_legacy.py

# Or keep as reference with clear naming
mv scripts/validate_legacy.py scripts/OLD_validate_for_html.py
```

## New Reality (Post Grok #2 Fix)

✅ **Validation**: `scripts/validate_data.py` (Python) + `src/schema.ts` (Zod)
✅ **Build**: GitHub Actions runs validation before build
✅ **Types**: Generated from Zod schema (single source of truth)
✅ **Quality Gate**: Build fails on bad data

❌ **Automation**: Still manual (skill doesn't commit/push)
❌ **Archive**: Still manual (skill doesn't call archive script)
