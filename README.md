# Tesla Investor Research Dashboard

An automated tracking system for monitoring Tesla's key development milestones across AI chips, autonomous vehicles, robotics, and regulatory approvals. Built with a custom Claude AI skill that automatically researches and updates the dashboard weekly.

![Dashboard Preview](https://img.shields.io/badge/Status-Active-success)
![Last Updated](https://img.shields.io/badge/Updated-2026--05--24-blue)

## 🎯 What This Tracks

**5 Key Categories:**
1. **AI Chip Production** - AI5/AI6 development at Samsung/TSMC
2. **Cybercab Production** - Autonomous robotaxi manufacturing and testing
3. **FSD Country Approvals** - Full Self-Driving regulatory progress
4. **Job Postings** - Optimus robotics hiring trends
5. **Optimus Production** - Humanoid robot manufacturing timeline

**Plus:**
- Quarterly vehicle production & delivery data from Tesla IR
- Historical trends and year-over-year growth analysis
- Interactive charts and metrics visualization

## 🚀 Quick Start

### View the Dashboard

Simply open `index.html` in your browser:
```bash
open index.html
```

The dashboard is a standalone HTML file with embedded data - no server required!

### Automated Updates (Claude Code Required)

If you have [Claude Code](https://claude.ai/code) installed:

```bash
/tesla-update
```

This skill will:
- Research latest news across all 5 categories
- Check for new quarterly P&D reports
- Update the JSON data file
- Sync the HTML dashboard
- Open the updated dashboard automatically

## 📁 Project Structure

```
Research/
├── index.html                    # Interactive dashboard (open in browser)
├── tesla-tracking-data.json      # All tracking data (source of truth)
├── .claude/
│   └── skills/
│       └── tesla-update/
│           └── SKILL.md          # Automated update skill
├── tesla-investor-tracking.md    # Archived tracking document (pre-dashboard)
└── README.md                     # This file
```

## 🔄 How Updates Work

The `/tesla-update` skill automates the entire research and update process:

1. **Research** - Searches preferred news sources (Electrek, Teslarati, etc.)
2. **Extract** - Pulls key developments with dates and sources
3. **Update JSON** - Adds new weekly summary and metrics
4. **Sync HTML** - Embeds updated data in dashboard
5. **Validate** - Ensures no syntax errors
6. **Open** - Launches dashboard in browser

## 📊 Data Format

All data is stored in `tesla-tracking-data.json` with this structure:

```json
{
  "lastUpdated": "2026-04-18",
  "weeklySummaries": [
    {
      "weekOf": "2026-04-18",
      "keyChanges": [...],
      "trends": [...]
    }
  ],
  "metrics": {
    "cybercab": { "data": [...] },
    "jobPostings": { "data": [...] },
    "robotaxiFleet": { "data": [...] },
    "fsdApprovals": { "countries": [...] }
  },
  "categories": {
    "aiChip": {...},
    "cybercab": {...},
    "fsd": {...},
    "jobPostings": {...},
    "optimus": {...},
    "productionDelivery": {...}
  }
}
```

## 🎨 Dashboard Features

- **Weekly Summaries** - Latest developments with trend analysis
- **Category Deep Dives** - Detailed timelines and key points for each area
- **Interactive Charts** - Cybercab production, robotaxi fleet deployment, quarterly deliveries
- **Status Indicators** - 🟢 Positive, 🔴 Negative, 🟡 Neutral
- **Source Links** - Every update links to original source
- **Historical Data** - Complete tracking history since March 2026

## 🛠️ Technical Details

**Dashboard Technology:**
- Single HTML file with embedded CSS/JavaScript/data
- Chart.js for visualizations (loaded from CDN)
- TradingView widget for Tesla stock (loaded from CDN)
- Requires internet for CDN libraries, otherwise fully standalone
- Responsive design for mobile/desktop

**Data Management:**
- JSON as single source of truth
- Embedded data in HTML for standalone deployment
- Marker comments for reliable sync
- Validation to prevent syntax errors

**Automation:**
- Claude AI skill with web search
- Automatic news aggregation
- Official Tesla IR data extraction
- Smart formatting and categorization

## 📈 Data Sources

**Preferred News Sources:**
- [Electrek](https://electrek.co)
- [Teslarati](https://teslarati.com)
- [TeslaNorth](https://teslanorth.com)
- [Tesla Oracle](https://teslaoracle.com)
- [Basenor](https://basenor.com)
- [Optimusk Blog](https://optimusk.blog)

**Official Data:**
- [Tesla Investor Relations](https://ir.tesla.com/press) - Quarterly reports

## 🤝 Contributing

This is a personal research project, but suggestions are welcome! Feel free to:
- Open issues for data corrections
- Suggest additional tracking categories
- Report bugs in the dashboard

## 📝 License

Personal research project for educational and investment tracking purposes.

## 🙏 Credits

- **Research & Updates**: Automated via Claude Sonnet 4.5
- **Dashboard Design**: Custom HTML/CSS/JavaScript
- **Data Curation**: Ongoing weekly updates

---

**Note**: This project tracks publicly available information for research purposes. Not financial advice. Always verify information with official sources before making investment decisions.

**Last Updated**: May 24, 2026 | [View Dashboard](index.html)
