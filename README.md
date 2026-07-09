# Tesla Investor Tracking Dashboard

An automated tracking system for monitoring Tesla's key development milestones across AI chips, autonomous vehicles, robotics, and regulatory approvals. Built with React + TypeScript and powered by a custom Claude AI skill that automatically researches and updates the dashboard weekly.

![Dashboard Preview](https://img.shields.io/badge/Status-Active-success)
![Last Updated](https://img.shields.io/badge/Updated-2026--07--03-blue)
[![Deployed](https://img.shields.io/badge/Live-GitHub%20Pages-brightgreen)](https://gsolis31.github.io/Tesla_Research/)

## 🎯 What This Tracks

**9 Key Categories:**
1. **AI Chip Production** - AI5/AI6 development at Samsung/TSMC, Terafab progress
2. **Cybercab Production** - Autonomous robotaxi manufacturing and testing
3. **FSD Country Approvals** - Full Self-Driving regulatory progress worldwide
4. **FSD v15 Software** - Major software rewrite timeline and development
5. **Job Postings** - Optimus robotics hiring trends
6. **Optimus Production** - Humanoid robot manufacturing timeline
7. **Terafab In-House Chip Manufacturing** - Tesla's chip fabrication facility
8. **4680 Battery Cell Production** - Battery cell manufacturing progress
9. **Vehicle Production & Delivery** - Quarterly production and delivery data

**Plus:**
- Robotaxi fleet deployment by city
- Historical trends and year-over-year growth analysis
- Interactive charts and metrics visualization
- Real-time Tesla stock chart (TradingView)

## 🚀 Quick Start

### View Live Dashboard

Visit the live dashboard at: **https://gsolis31.github.io/Tesla_Research/**

### Local Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev
# Opens at http://localhost:5173

# Build for production
npm run build
# Creates dist/ folder with optimized build
```

### Automated Updates (Claude Code Required)

If you have [Claude Code](https://claude.ai/code) installed:

```bash
/tesla-update
```

This skill will:
- Research latest news across all 9 categories
- Check for new quarterly production & delivery reports
- Update robotaxi fleet deployment data
- Update the JSON data file
- Rebuild the React app
- **Note**: Currently does not auto-commit (manual git push required)

## 📁 Project Structure

```
Research/
├── src/                                # React source code
│   ├── components/                     # React components
│   │   ├── WeeklySummary.tsx          # Latest updates display
│   │   ├── MetricsCharts.tsx          # Charts + city table + P&D
│   │   ├── Categories.tsx             # Category information tabs
│   │   ├── ProductionDelivery.tsx     # P&D with advanced filtering
│   │   └── TradingViewWidget.tsx      # Tesla stock chart
│   ├── types/                          # TypeScript type definitions
│   │   └── index.ts
│   ├── App.tsx                         # Main app component
│   ├── App.css                         # App-specific styles
│   ├── index.css                       # Global styles + Tailwind
│   └── main.tsx                        # React entry point
├── dist/                               # Production build output (auto-deployed)
├── tesla-tracking-data.json            # All tracking data (source of truth)
├── archives/                           # Archived data by year
├── .claude/
│   └── skills/
│       └── tesla-update/
│           └── SKILL.md                # Automated update skill
├── .github/
│   └── workflows/
│       └── deploy.yml                  # Auto-deploy to GitHub Pages
├── scripts/
│   ├── archive_old_data.py             # Annual data archiving
│   ├── validate_data.py                # Data validation (React/Vite)
│   └── validate_legacy.py              # Old validation (HTML-based, obsolete)
├── package.json                        # Node dependencies & scripts
├── vite.config.ts                      # Vite build configuration
├── tailwind.config.js                  # Tailwind CSS config
├── tsconfig.json                       # TypeScript config
└── README.md                           # This file
```

## 🔄 How Updates Work

The `/tesla-update` skill automates the entire research and update process:

1. **Research** - Searches preferred news sources (Electrek, Teslarati, robotaxitracker.com, etc.)
2. **Extract** - Pulls key developments with dates and sources
3. **Update JSON** - Adds new weekly summary, metrics, and P&D data
4. **Archive** - Archives old data (keeps current + previous year)
5. **Rebuild** - Runs `npm run build` to create production build
6. **Deploy** - Commits and pushes; GitHub Actions auto-deploys

## 🛠️ Technical Stack

**Frontend:**
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool (fast HMR, optimized builds)
- **Tailwind CSS** - Utility-first styling
- **Chart.js** - Data visualization
- **react-chartjs-2** - React wrapper for Chart.js
- **TradingView Widget** - Live stock chart

**Deployment:**
- **GitHub Actions** - Automated CI/CD
- **GitHub Pages** - Static site hosting
- **Auto-deploy** - Every push to main triggers rebuild and deployment

**Data Management:**
- **JSON** - Single source of truth
- **Direct import** - Vite bundles JSON with app (no sync script needed)
- **Time-based archiving** - Keeps data file size manageable

**Development:**
- **Node.js 20** - Runtime
- **npm** - Package manager
- **ESLint** - Code linting
- **Hot Module Replacement** - Instant updates during development

## 📊 Dashboard Features

### Charts & Metrics Tab
- **Production & Delivery Charts** - Advanced filtering by year/quarter with grouping options
- **Cybercab Production** - Production count over time
- **Robotaxi Fleet** - Total fleet size tracking
- **Job Postings** - Optimus hiring trends
- **City-by-City Breakdown** - Robotaxi service status by location

### Weekly Summary Tab
- Latest developments with sentiment analysis
- Evidence-based reality checks (headline vs actual metrics)
- Status indicators: 🟢 Positive, 🔴 Negative, 🟡 Neutral
- Source links for verification

### Categories Tab
- **AI Chip Production** - Timeline, key points, latest updates
- **Cybercab** - Development milestones
- **FSD Approvals** - Country-by-country progress
- **Optimus Production** - Manufacturing timeline

## 📈 Data Sources

**Preferred News Sources:**
- [Electrek](https://electrek.co) - Tesla news and analysis
- [Teslarati](https://teslarati.com) - Tesla community news
- [TeslaNorth](https://teslanorth.com) - Tesla updates
- [Tesla Oracle](https://teslaoracle.com) - Tesla insights
- [Basenor](https://basenor.com) - Tesla analysis
- [Optimusk Blog](https://optimusk.blog) - Optimus updates
- [Robotaxi Tracker](https://robotaxitracker.com) - Fleet deployment data

**Official Data:**
- [Tesla Investor Relations](https://ir.tesla.com/press) - Quarterly production & delivery reports

## 🚢 Deployment

### Automatic Deployment (GitHub Actions)

Every push to `main` triggers:
```
Push to main
  ↓
GitHub Actions workflow runs
  ↓
npm ci (install dependencies)
  ↓
npm run build (create production build)
  ↓
Deploy dist/ to GitHub Pages
  ↓
Live at https://gsolis31.github.io/Tesla_Research/
```

View workflow runs: [Actions Tab](https://github.com/gsolis31/Tesla_Research/actions)

### Manual Deployment

```bash
# Build locally
npm run build

# Commit and push
git add .
git commit -m "Update dashboard"
git push origin main

# GitHub Actions handles the rest!
```

## 🧪 Data Validation

The project uses a **dual-layer validation system** to ensure data quality:

### Pre-Build Validation (Python)
```bash
python3 scripts/validate_data.py
```
Validates:
- JSON structure and required fields
- Date formats and data types
- Business logic invariants (chronological order, no duplicates)
- Category names match schema
- UI coverage (warns if data won't render)

### Build-Time Validation (Zod)
Automatic validation during `npm run build`:
- Runtime type checking with Zod schema
- Build fails on invalid data
- TypeScript types generated from schema (single source of truth)

### Archive Old Data
Keeps data file manageable (current + previous year):
```bash
python3 scripts/archive_old_data.py
```

**Note**: See `VALIDATION_UPGRADE.md` for full documentation on the validation system.

## 🤝 Contributing

This is a personal research project, but suggestions are welcome! Feel free to:
- Open issues for data corrections
- Suggest additional tracking categories
- Report bugs in the dashboard
- Submit pull requests for features

## 📝 License

Personal research project for educational and investment tracking purposes.

## 🙏 Credits

- **Research & Updates**: Automated via Claude Sonnet 4.5
- **Dashboard Design**: React + TypeScript + Tailwind CSS
- **Data Curation**: Ongoing weekly updates
- **Deployment**: GitHub Actions + GitHub Pages

---

**Note**: This project tracks publicly available information for research purposes. Not financial advice. Always verify information with official sources before making investment decisions.

**Last Updated**: July 3, 2026 | [View Live Dashboard](https://gsolis31.github.io/Tesla_Research/)
