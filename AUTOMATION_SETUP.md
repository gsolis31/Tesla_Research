# Tesla Tracker - Automation Setup

## ⚠️ Note: Automation Currently Disabled

**Issue**: Claude API doesn't have built-in web search, so automated updates can't fetch Tesla news.

**Solution**: Use manual `/tesla-update` via Claude Code CLI (works perfectly with web search).

The GitHub Actions workflow has been disabled to avoid wasting API credits.

---

## Original Documentation (For Reference)

## How It Works

1. **GitHub Actions workflow** runs every Monday at 12 PM UTC (7 AM EST / 4 AM PST)
2. **Python script** uses Claude API to research Tesla news and updates
3. **Multi-layered sentiment analysis** is automatically applied
4. **Changes are committed** and pushed to GitHub
5. **GitHub Pages** auto-deploys the updated dashboard

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

### Step 4: Enable GitHub Actions

1. In your repository, click **Actions** tab
2. If prompted, click **I understand my workflows, go ahead and enable them**
3. You should see "Tesla Tracker Auto-Update" workflow

### Step 5: Test It

#### Manual Test:
1. Go to **Actions** tab
2. Click **Tesla Tracker Auto-Update** workflow
3. Click **Run workflow** dropdown (right side)
4. Click green **Run workflow** button
5. Watch it run (takes ~2-3 minutes)
6. Check if `tesla-tracking-data.json` was updated

#### Check the Schedule:
- Workflow runs automatically every **Monday at 12 PM UTC**
- To change schedule, edit `.github/workflows/tesla-update.yml`
- Cron format: `'0 12 * * 1'` (minute hour day month weekday)

## How Updates Work

The automation script:

1. **Reads current data** from `tesla-tracking-data.json`
2. **Checks last update date** to determine research period
3. **Uses Claude API** to:
   - Search for Tesla news in all 5 categories
   - Apply multi-layered sentiment analysis
   - Extract objective metrics and evidence
   - Detect headline-reality gaps
4. **Updates JSON** with new weekly summary and metrics
5. **Syncs HTML dashboard** with updated data
6. **Commits changes** to GitHub
7. **GitHub Pages** auto-deploys within ~1 minute

## Cost Estimate

**Claude API Usage** (pay-as-you-go):
- ~10,000-20,000 tokens per weekly update
- Cost: $0.03-$0.06 per update
- **Monthly cost: ~$0.25** (4 updates/month)

Very affordable for automated updates!

## Customization

### Change Update Frequency

Edit `.github/workflows/tesla-update.yml`:

```yaml
# Daily at noon UTC
- cron: '0 12 * * *'

# Twice weekly (Monday & Thursday)
- cron: '0 12 * * 1,4'

# Every 3 days
- cron: '0 12 */3 * *'
```

### Change Update Time

Format: `'minute hour * * *'`
- `'0 16 * * 1'` = Monday 4 PM UTC (11 AM EST)
- `'30 9 * * 1'` = Monday 9:30 AM UTC (4:30 AM EST)

## Monitoring

### View Workflow Runs:
1. Go to **Actions** tab in GitHub
2. See history of all runs (success/failure)
3. Click any run to see detailed logs

### Check for Updates:
- Dashboard URL: https://gsolis31.github.io/Tesla_Research/
- Check "Last Updated" date in top-right corner
- Review recent commits for update history

## Troubleshooting

### Workflow Fails
1. Check **Actions** tab for error logs
2. Common issues:
   - API key not set correctly
   - API rate limits exceeded
   - No significant news (not actually an error)

### No Updates Showing
1. Check if workflow ran successfully in Actions tab
2. Verify API key is valid
3. Check commit history - was anything committed?
4. Clear browser cache and refresh dashboard

### API Costs Too High
1. Reduce update frequency (weekly → bi-weekly)
2. Check token usage in Anthropic Console
3. Optimize the prompt in `scripts/auto_update.py`

## Manual Updates

You can still run manual updates locally:
```bash
# Using Claude Code CLI (current method)
/tesla-update

# OR using the automation script
ANTHROPIC_API_KEY=your-key python scripts/auto_update.py
```

## Disabling Automation

To stop automatic updates:
1. Go to `.github/workflows/tesla-update.yml`
2. Comment out or delete the `schedule:` section
3. Keep `workflow_dispatch:` for manual triggers only

---

## Summary

Once set up:
- ✅ Updates run automatically every Monday
- ✅ No laptop needed
- ✅ Dashboard always up-to-date
- ✅ Costs ~$0.25/month
- ✅ Can trigger manual updates anytime
- ✅ Full transparency via GitHub commits

Questions? Check the workflow logs in the Actions tab!
