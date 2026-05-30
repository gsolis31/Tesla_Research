# Tesla Tracker - Automation Setup

## ⚠️ Automation Currently Disabled

**Issue**: Claude API doesn't have built-in web search capability, so the `auto_update.py` script cannot fetch real Tesla news.

**Current Solution**: Use manual `/tesla-update` via Claude Code CLI, which has full web search access.

**Status**:
- ✅ `/tesla-update` skill - **Primary update method** (recommended)
- ⚠️ `scripts/auto_update.py` - Partial implementation, web search not wired
- ❌ GitHub Actions workflow - Scheduled runs disabled (workflow_dispatch still available for testing)

---

## Current Update Workflow

Use the Claude Code skill for weekly updates:

```bash
/tesla-update
```

This will:
1. Research latest news across all 5 categories with web search
2. Apply multi-layered sentiment analysis
3. Update tesla-tracking-data.json
4. Sync index.html dashboard
5. Validate changes
6. Open dashboard in browser

---

## GitHub Actions Status

The workflow at `.github/workflows/tesla-update.yml` is configured but **not actively used**:
- Scheduled cron runs: **Disabled** (commented out)
- Manual trigger: **Available** (workflow_dispatch) for testing only
- Limitation: Cannot perform real web searches, only uses Claude API without search tools

If you want to test the workflow manually, it will run `scripts/auto_update.py` but **will not fetch real news** due to lack of web search capability.

## Setup Instructions

### Step 1: Get Claude API Access

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up for API access (separate from Claude Pro)
3. New accounts get $5 free credits
4. After free credits: ~$3 per million tokens (very cheap for this use case)

### Step 2: Create API Key

1. In Anthropic Console, go to **API Keys**
2. Click **Create Key**
3. Name it "Tesla Tracker GitHub Actions"
4. Copy the key (starts with `sk-ant-...`)
5. **Save it securely** - you won't see it again!

### Step 3: Add Secret to GitHub

1. Go to your GitHub repository: https://github.com/gsolis31/Tesla_Research
2. Click **Settings** tab
3. In left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Name: `ANTHROPIC_API_KEY`
6. Value: Paste your API key from Step 2
7. Click **Add secret**

---

## Archived Documentation (For Reference Only)

<details>
<summary>Original GitHub Actions Setup Instructions (Not Currently Used)</summary>

The following documentation describes the original plan for automated GitHub Actions updates. This approach is **not currently active** because the Claude API lacks web search capabilities needed for real news research.

### Historical Setup Steps

#### Step 1: Get Claude API Access
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up for API access (separate from Claude Pro)
3. New accounts get $5 free credits
4. After free credits: ~$3 per million tokens

#### Step 2: Create API Key
1. In Anthropic Console, go to **API Keys**
2. Click **Create Key**
3. Name it "Tesla Tracker GitHub Actions"
4. Copy the key (starts with `sk-ant-...`)

#### Step 3: Add Secret to GitHub
1. Go to repository Settings → Secrets and variables → Actions
2. Create secret: `ANTHROPIC_API_KEY`
3. Paste API key value

#### Step 4: Enable Schedule (If Web Search Becomes Available)
Edit `.github/workflows/tesla-update.yml` and uncomment the schedule:
```yaml
schedule:
  - cron: '0 12 * * 1'  # Monday at 12 PM UTC
```

### Cost Estimate (If Re-enabled)
- ~10,000-20,000 tokens per weekly update
- Cost: $0.03-$0.06 per update
- **Monthly cost: ~$0.25** (4 updates/month)

</details>

---

## Manual Updates (Current Method)

You can run updates locally using either method:

### Method 1: Claude Code Skill (Recommended)
```bash
/tesla-update
```
Full web search, sentiment analysis, and complete data updates.

### Method 2: Automation Script (Limited)
```bash
ANTHROPIC_API_KEY=your-key python3 scripts/auto_update.py
```
⚠️ **Note**: This script does not have web search and cannot fetch real news. It's a partial implementation kept for reference.

---

## Summary

**Current Status**:
- ✅ Manual `/tesla-update` skill - Full functionality with web search
- ✅ Validation and sync scripts - Working
- ⚠️ GitHub Actions - Disabled (no web search capability)
- ⚠️ `auto_update.py` - Partial implementation only

**Recommended Workflow**: Use `/tesla-update` via Claude Code CLI for all updates.
