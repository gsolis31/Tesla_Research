---
name: tesla-update
description: Automatically research and update the Tesla investor tracking dashboard with the latest news across all categories plus quarterly production & delivery data
user-invocable: true
allowed-tools: WebSearch, Read, Edit, Write, Bash
---

# Tesla Tracker Update Skill

## What This Skill Does

When invoked, this skill will:
1. Read the current `tesla-tracking-data.json` to get the last update date
2. Research latest news for all 5 news categories from the last update date until today
3. Check for new quarterly production & delivery reports from ir.tesla.com/press
4. Update `tesla-tracking-data.json` with new weekly summary, metrics, and P&D data
5. Sync the embedded data in `index.html`
6. Open the dashboard in the browser
7. Provide a summary of key updates

---

## File Locations

- **JSON Data**: `/Users/gonzalosolis/Research/tesla-tracking-data.json`
- **HTML Dashboard**: `/Users/gonzalosolis/Research/index.html`
- **Working Directory**: `/Users/gonzalosolis/Research`

---

## One-Time Setup (Required for HTML Sync)

**IMPORTANT**: The HTML file must have marker comments for reliable data syncing.

If not already present, add these markers to `index.html`:

**Around line 450** (before `const data = {`):
```html
    <script>
        // Embedded data - updated automatically from tesla-tracking-data.json
        <!-- DATA_OBJECT_START -->
        const data = {
```

**Around line 1352** (after the closing `}`):
```html
        };
        <!-- DATA_OBJECT_END -->

        function renderProductionDelivery() {
```

These markers ensure the update script can reliably find and replace the data object without syntax errors.

---

## Categories to Track

### News Categories (1-8)

### 1. AI Chip Production (AI5/AI6 at Samsung/TSMC)
**Search for**:
- Production timeline updates
- Samsung/TSMC 2nm yield improvements or delays
- Wafer capacity expansion news
- Terafab developments
- Risk production vs mass production milestones

### 2. Cybercab Production
**Search for**:
- Production unit counts and locations
- Testing deployment updates
- Mass production timeline progress
- Crash testing and validation status
- Public road testing locations

### 3. FSD Country Approvals
**Search for**:
- New country approvals (especially EU via mutual recognition)
- Regulatory timeline updates
- Subscription pricing launches
- Japan deployment progress
- Early Access program expansion

### 4. Job Postings (Optimus-related)
**Search for**:
- Current Optimus-related job posting count
- Significant hiring changes
- New role types or locations
- Strategic hires from competitors

### 5. Optimus Production
**Search for**:
- Production timeline updates
- Facility setup progress (Fremont, Giga Texas)
- Commercial customer announcements
- Pricing updates
- Gen 3/Gen 4 developments
- Cortex AI infrastructure updates
- Digital Optimus developments

### 6. Vehicle Production & Delivery (Quarterly Reports)
**CRITICAL - Official Source Only**:
- **Official URL**: https://ir.tesla.com/press
- Search for quarterly production and delivery press releases
- Look for releases titled "Tesla [Quarter] [Year] Production, Deliveries & Deployments"
- Extract exact production and delivery numbers (not rounded "over X" figures)
- Update for any new quarters since last update
- Calculate annual totals and YoY growth for completed years

**What to extract**:
- Exact production number for the quarter
- Exact delivery number for the quarter
- Quarter designation (e.g., Q1-26, Q2-26)

### 7. Terafab In-House Chip Manufacturing
**Search for**:
- Construction progress at Giga Texas North Campus
- Partnership updates (Intel collaboration)
- AI5 chip production milestones (small-batch 2026, volume 2027)
- Facility buildout timeline and investment updates
- Strategic implications for vertical integration

### 8. 4680 Battery Cell Production
**Search for**:
- Production capacity updates (GWh/year)
- Yield rate improvements
- Cost per kWh milestones
- Dry coating technology progress
- Facility expansion (Giga Texas, Giga Nevada)
- Integration into vehicle models (Model Y, Cybertruck)

### 9. FSD v15 Software Rewrite (Critical Milestone)
**Search for**:
- Release timeline updates (target Q4 2026/Q1 2027)
- Development progress and testing updates
- Parameter count and architecture details
- Hardware compatibility confirmations
- Impact on robotaxi scaling timeline
- Beta testing program expansion

---

## Policy: Avoiding Repetitive Headlines

**CRITICAL RULE**: Only create keyChanges for actual news, not for "no change" situations.

### When TO Create a keyChange:
✅ New developments (approvals, deployments, announcements)
✅ Significant changes (fleet growth >20%, timeline shifts >1 month)
✅ Major milestones (production starts, facility openings, partnerships)
✅ Strategic pivots (cancellations, new directions, major partnerships)
✅ First-time revelations (investigations, leaked data, official statements)

### When NOT TO Create a keyChange:
❌ Metrics that haven't changed since last update
❌ "Still waiting" or "remains unchanged" situations
❌ Minor continuations of previous trends
❌ Repeating information from previous weeks

### Examples:

**Good:**
- Week 1: "Bloomberg reveals robotaxi fleet at 59 vehicles, H1 target abandoned" ✅ (major revelation)
- Week 2: (No keyChange about fleet) ✅ (no new news, just update metric silently)
- Week 3: "Fleet expands to 120 vehicles with FSD v14.5 deployment" ✅ (significant change)

**Bad:**
- Week 1: "Robotaxi fleet at 59 vehicles" ✅
- Week 2: "Robotaxi fleet frozen at 59 vehicles for 7 days" ❌ (repetitive)
- Week 3: "Robotaxi fleet still at 59 vehicles for 14 days" ❌ (repetitive)

### How to Handle Ongoing Situations:

**For stagnant metrics:**
- Update the metric data point in `metrics.robotaxiFleet.data[]`
- Mention briefly in trends if contextually relevant
- Do NOT create a keyChange unless there's new context (statement from Musk, regulatory issue, etc.)

**For slow-moving progress:**
- Only report when there's a meaningful increment (>20% change, major milestone)
- Consolidate minor updates into quarterly summaries

**For "waiting on X" situations:**
- Report once when the dependency is identified
- Don't repeat weekly until the situation resolves

---

## Preferred News Sources

Search using these source domains for best results:
- Electrek (electrek.co)
- Teslarati (teslarati.com)
- TeslaNorth (teslanorth.com)
- Tesla Oracle (teslaoracle.com)
- Basenor (basenor.com)
- Optimusk Blog (optimusk.blog)
- Official Tesla announcements

---

## Execution Steps

### Step 1: Read Current State
```
1. Read tesla-tracking-data.json
2. Extract lastUpdated date
3. Calculate date range: lastUpdated → today
```

### Step 2: Research Updates
For each of the 9 categories, use WebSearch to find news from the date range:
```
- Search query format: "Tesla [category] [keywords] 2026 [months]"
- Review top 5-10 results per category
- Identify key changes, status (positive/negative/neutral), sources
```

**IMPORTANT - Production & Delivery Data**:
After researching the 5 news categories, ALWAYS check for new quarterly production & delivery reports:
```
1. Search: "Tesla Q[N] [YEAR] production delivery report site:ir.tesla.com"
   - Check for all quarters since last update in data file
   - Example: If last quarter is Q4 2024, search for Q1 2025, Q2 2025, etc.

2. For each new quarter found:
   - Use WebSearch to get the report URL
   - Extract exact production and delivery numbers
   - Note: Reports say "over XXX,XXX" but search results usually have exact figures

3. Calculate annual totals for completed years:
   - Sum all 4 quarters for deliveries
   - Calculate YoY growth: ((current year - previous year) / previous year) × 100
   - Update totalProduction and totalDeliveries (sum ALL quarters from all years)
```

**IMPORTANT - Robotaxi Fleet Data**:
ALWAYS check for updated robotaxi fleet deployment numbers:
```
1. Search: "Tesla robotaxi fleet size active vehicles April [YEAR]"
2. Search: "Tesla robotaxi deployment Dallas Houston Phoenix Austin site:robotaxitracker.com"
3. Look for:
   - Total active vehicles across all cities
   - City-specific deployment numbers
   - New city launches
   - Fleet growth metrics
4. Sources to check:
   - robotaxitracker.com (primary source for real-time data)
   - Basenor, Teslarati, Electrek for deployment announcements
```

### Step 3: Update JSON Data
Update `tesla-tracking-data.json`:

**A. Update lastUpdated**:
```json
"lastUpdated": "YYYY-MM-DD"  // Today's date
```

**B. Add new weekly summary** (at START of weeklySummaries array):
```json
{
  "weekOf": "YYYY-MM-DD",
  "keyChanges": [
    {
      "category": "Category Name",
      "status": "positive|negative|neutral",
      "title": "Brief title (under 80 chars)",
      "description": "Detailed description with key data points",
      "source": "https://source-url.com"
    }
  ],
  "trends": [
    "Trend observation 1",
    "Trend observation 2",
    "Trend observation 3",
    "Trend observation 4"
  ]
}
```

**C. Update metrics** (if applicable):
- Add new Cybercab production counts to `metrics.cybercab.data[]`
- Add new job posting counts to `metrics.jobPostings.data[]`
- **ALWAYS add new robotaxi fleet counts to `metrics.robotaxiFleet.data[]`** with format:
  ```json
  { "date": "YYYY-MM-DD", "count": XXX, "note": "Description with city breakdown" }
  ```
- Update FSD approval countries in `metrics.fsdApprovals.countries[]`

**D. Update categories** (for each relevant category):
- Update `latestUpdate` to today's date
- Update `criticalNews` with most important recent development
- Add/update `keyPoints` array with new information
- Add new timeline events to `timeline[]` array

**E. Update Production & Delivery Data** (if new quarters available):
Update `categories.productionDelivery`:
- Update `latestUpdate` to today's date
- Update `criticalNews` with latest quarter results
- **Append** new quarters to `quarterlyData[]` array:
  ```json
  { "quarter": "Q1-26", "production": 408386, "delivery": 358023 }
  ```
- Update `annualSummary[]` when a full year is complete:
  ```json
  { "year": "2025", "deliveries": 1636129, "yoyGrowth": -8.56 }
  ```
- Recalculate `totalProduction` (sum of ALL production values)
- Recalculate `totalDeliveries` (sum of ALL delivery values)

### Step 4: Sync HTML Dashboard
Update `index.html`:

**Process**:
Use the shared sync script to reliably sync JSON to HTML:

```bash
python scripts/sync_dashboard.py
```

Or in Python:
```python
from scripts.sync_dashboard import sync_dashboard

if not sync_dashboard():
    print("ERROR: Failed to sync dashboard")
    exit(1)
```

**Note**: This shared script (scripts/sync_dashboard.py) uses marker comments to reliably locate and replace the data object, preventing syntax errors. It's also used by auto_update.py for consistency.

### Step 5: Open Dashboard
```bash
open index.html
```

### Step 6: Provide Summary
Output a concise summary to user:
- Week range updated (last date → today)
- Number of key changes found per category
- Major highlights (🟢 positive, 🔴 negative, 🟡 neutral)
- Links to top 3-5 sources

**Troubleshooting Note**:
If the dashboard appears blank in the browser, tell the user:
"If you see a blank dashboard, press `Cmd+Option+I` to open the browser console and check for JavaScript errors. This usually indicates a syntax issue in the data object."

---

## Data Structure Notes

**CRITICAL RULES**:
- ✅ **ALWAYS AUGMENT, NEVER OVERWRITE** existing data
- ✅ Add new weekly summaries at the **BEGINNING** of weeklySummaries array
- ✅ Keep all historical data intact
- ✅ Weekly summaries in reverse chronological order (newest first)
- ✅ Metrics data arrays grow over time (append new data points)
- ✅ Timeline arrays in categories should be in chronological order
- ✅ Status values: "positive" (🟢), "negative" (🔴), "neutral" (🟡)

**Status Guidelines**:
- **Positive**: Approvals, production milestones hit, yield improvements, new customers
- **Negative**: Delays, production misses, regulatory setbacks, cancellations
- **Neutral**: Stable metrics, ongoing progress, minor updates

### Multi-Layered Sentiment Analysis

**CRITICAL**: Use rigorous, evidence-based sentiment analysis to distinguish between headline framing and objective reality.

**Analysis Framework**:

Each keyChange entry should include dual-layer sentiment assessment:

```json
{
  "status": "negative",  // Reality assessment (what metrics show)
  "sentiment": {
    "headline": "neutral",     // What the article/announcement says
    "reality": "negative",      // What the data actually shows
    "confidence": "high|medium|low",
    "rationale": "Explain why reality differs from headline"
  },
  "evidence": {
    "positive_signals": [
      "List 2-5 genuinely positive data points"
    ],
    "negative_signals": [
      "List 2-5 concerning data points"
    ],
    "key_metrics": {
      "actual": "Current performance",
      "target": "Goal or expectation",
      "trajectory": "Percentage of target or timeline status"
    }
  },
  "category": "...",
  "title": "...",
  "description": "...",
  "source": "..."
}
```

**Required Analysis Steps**:

1. **Extract Objective Metrics**
   - Production counts, dates, percentages, timelines
   - Do NOT rely on headline framing ("milestone reached", "successful launch")
   - Focus on actual numbers vs targets

2. **Gather Evidence**
   - List 2-5 positive_signals (real achievements)
   - List 2-5 negative_signals (real concerns)
   - Be objective - a "launch" with 25 units is both a launch (positive) AND far below scale (negative)

3. **Calculate Reality Assessment**
   - Compare actual performance to stated targets
   - Evaluate trajectory toward goals
   - Consider timeline delays or accelerations

4. **Assign Dual Sentiment**
   - `headline`: What the media/announcement emphasizes
   - `reality`: What the metrics objectively show
   - `confidence`: How certain you are (high/medium/low)
   - `rationale`: Explain any headline-reality gap

5. **Set Status Field**
   - `status` should ALWAYS reflect the `reality` assessment, NOT the headline
   - This is what appears in sentiment trend charts

**Category-Specific Thresholds**:

**Cybercab/Robotaxi**:
- POSITIVE: ≥80% of target trajectory, ahead of schedule
- NEUTRAL: 40-79% of target, minor delays <1 month
- NEGATIVE: <40% of target, major delays >1 month
- Example: "25 vehicles, target 1000+ by H1 2026" = 25/1000 = 2.5% = NEGATIVE

**AI Chip Production**:
- POSITIVE: On schedule, yields >80% of target
- NEUTRAL: Delay 3-6 months, yields 60-80%
- NEGATIVE: Delay >6 months, yields <60%, technology fallback

**FSD Country Approvals**:
- POSITIVE: New country approval, early expansion
- NEUTRAL: Expected timeline, minor delays <1 month
- NEGATIVE: Rejection, delays >1 month, regulatory setbacks

**Optimus Production**:
- POSITIVE: Timeline advancing, facility expansions, customer deals
- NEUTRAL: Stable progress, on schedule
- NEGATIVE: Timeline delays >1 quarter, facility setbacks, order cancellations

**Job Postings**:
- POSITIVE: +20% increase in relevant roles
- NEUTRAL: ±20% range (stable)
- NEGATIVE: -20% decrease in relevant roles

**Example - Robotaxi Fleet Analysis**:

```json
{
  "status": "negative",
  "sentiment": {
    "headline": "neutral",
    "reality": "negative",
    "confidence": "high",
    "rationale": "25 vehicles represents only 6% of the pace needed to reach 1000+ vehicles across 7 cities by H1 2026"
  },
  "evidence": {
    "positive_signals": [
      "Android app launched for rider access",
      "3 cities now operational (Dallas, Houston, Phoenix)",
      "Public testing phase initiated"
    ],
    "negative_signals": [
      "Only 25 vehicles deployed after 4 months of operation",
      "94% below required trajectory for H1 2026 target",
      "Expansion to remaining 5 cities not yet announced",
      "No mass production timeline confirmed"
    ],
    "key_metrics": {
      "actual": 25,
      "target": "1000+ across 7 cities by H1 2026",
      "trajectory": "6% of target pace (25 vehicles / ~400 needed now)"
    }
  },
  "category": "Cybercab Production",
  "title": "Robotaxi fleet grows to 25 vehicles across 3 cities",
  "description": "Tesla's robotaxi fleet now includes 25 operational vehicles across Dallas, Houston, and Phoenix. Android app launched for public testing. However, this represents significant delay toward stated H1 2026 target of 1000+ vehicles across 7 cities.",
  "source": "https://..."
}
```

**Detecting Headline-Reality Gaps**:

Watch for these patterns:
- "Milestone reached" but numbers are <50% of target
- "Launched" but deployment is <100 units
- "On track" but timeline has slipped >1 quarter
- "Successful" but metrics show decline YoY
- "Expansion" but new locations are <20% of plan

When you detect a gap:
- Set `headline` to the media framing
- Set `reality` to the metrics-based assessment
- Set `status` to match `reality`
- Provide clear `rationale` explaining the discrepancy

**Backward Compatibility**:
- All new fields (sentiment, evidence) are OPTIONAL
- Existing entries without these fields will continue to work
- Dashboard will fall back to `status` field when sentiment.* is missing

---

## Error Handling

If any step fails:
1. Report the specific error to user
2. Ask if they want to continue with partial update
3. Do NOT overwrite existing data if update is incomplete
4. Suggest manual intervention if needed

---

## Example Invocation

```
User: /tesla-update
```

Expected behavior:
1. Skill automatically executes all steps
2. No questions asked (unless errors occur)
3. Dashboard opens with updated data
4. User receives summary of changes

---

## Tips for Best Results

- **Be comprehensive**: Don't skip categories even if no major news
- **Verify dates**: Ensure timeline events are in correct chronological order
- **Source quality**: Prefer official announcements and reliable Tesla news sites
- **Data consistency**: Match existing tone and detail level in descriptions
- **Metric tracking**: If a new metric appears regularly, consider adding it to the tracking structure
- **Production & Delivery**: ALWAYS check ir.tesla.com/press for new quarterly reports - this is the single source of truth for official numbers. Tesla releases quarterly reports typically within the first week of each quarter (early Jan, Apr, Jul, Oct)

---

## Skill Maintenance

Update this skill file if:
- File paths change
- Data structure evolves
- New categories are added
- News sources change
- User preferences change
