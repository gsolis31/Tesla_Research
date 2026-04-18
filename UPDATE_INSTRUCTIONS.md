# Tesla Tracking Update Instructions

## Overview
This tracker monitors Tesla developments across 5 key categories. Updates should be performed weekly or bi-weekly.

## Update Process

### 1. Research Latest News
Research updates in these categories from the last update date to today:

**Categories to Track:**
1. **AI Chip Production (AI5/AI6 at Samsung/TSMC)**
   - Production timeline updates
   - Samsung/TSMC 2nm yield improvements or delays
   - Wafer capacity expansion news
   - Terafab developments

2. **Cybercab Production**
   - Production unit counts and locations
   - Testing deployment updates
   - Mass production timeline progress
   - Crash testing and validation status

3. **FSD Country Approvals**
   - New country approvals (especially EU via mutual recognition)
   - Regulatory timeline updates
   - Japan deployment progress
   - Early Access program expansion

4. **Job Postings**
   - Current Optimus-related job posting count
   - Significant hiring changes
   - New role types or locations

5. **Optimus Production**
   - Production timeline updates
   - Facility setup progress (Fremont, Giga Texas)
   - Commercial customer announcements
   - Pricing updates

**Preferred News Sources:**
- Electrek
- Teslarati
- TeslaNorth
- Tesla Oracle
- Basenor
- Official Tesla announcements

### 2. Update Data Files

**Files to Update:**
- `tesla-tracking-data.json` - Primary data file
- `tesla-dashboard.html` - Contains embedded copy of JSON data (lines 388-579)

**Update Structure:**

#### A. Update lastUpdated date
```json
"lastUpdated": "YYYY-MM-DD"
```

#### B. Add new weekly summary (at START of weeklySummaries array)
```json
{
  "weekOf": "YYYY-MM-DD",
  "keyChanges": [
    {
      "category": "Category Name",
      "status": "positive|negative|neutral",
      "title": "Brief title",
      "description": "Detailed description with key data points",
      "source": "https://source-url.com"
    }
  ],
  "trends": [
    "Trend to watch 1",
    "Trend to watch 2"
  ]
}
```

#### C. Update metrics with new data points
- Add new Cybercab production counts
- Add new job posting counts
- Update FSD approval status/countries

#### D. Update categories
For each relevant category, update:
- `latestUpdate`: Current date
- `criticalNews`: Most important recent development
- `keyPoints`: Add/update bullet points with new information
- `timeline`: Add new timeline events with dates

### 3. Update HTML Dashboard
The HTML file contains an embedded copy of the JSON data (starting around line 388).
Replace the embedded `const data = {...}` object with the updated JSON from `tesla-tracking-data.json`.

### 4. Launch Dashboard
```bash
open tesla-dashboard.html
```

## Quick Command for Updates

When asked to "run the latest Tesla update":
1. Research all 5 categories for updates since last update date
2. Update `tesla-tracking-data.json` with new findings
3. Update embedded data in `tesla-dashboard.html`
4. Open the dashboard in browser

## Data Structure Notes

- **Always AUGMENT, never overwrite** - Add new weekly summaries at the beginning, keep historical data
- Weekly summaries are in reverse chronological order (newest first)
- Metrics data arrays grow over time (append new data points)
- Timeline arrays in categories should be in chronological order
- Status values: "positive" (green), "negative" (red), "neutral" (yellow)

## Automation Idea

Consider creating a script in the future that:
1. Fetches the latest data from `tesla-tracking-data.json`
2. Launches a research agent for the 5 categories
3. Updates both JSON and HTML files
4. Opens the dashboard

For now, this manual process ensures quality control of the research and data.
