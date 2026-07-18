# Tesla Data Archives

This directory contains historical data that has been archived to keep the main `tesla-tracking-data.json` file manageable.

## Archiving Strategy

**Retention Policy:** Keep current year + previous year in main file

**Example (in 2026):**
- Main file: Contains 2025 + 2026 data
- Archives: 2024 and earlier → `data/archives/2024.json`, `data/archives/2023.json`, etc.

**What Gets Archived:**
- ✅ `weeklySummaries` older than previous year
- ✅ `metrics.robotaxiFleet.data` older than previous year
- ✅ `metrics.cybercab.data` older than previous year
- ✅ `metrics.jobPostings.data` older than previous year
- ❌ `quarterlyData` - kept forever (only 4 per year, valuable for YoY comparison)

## Archive Files

Each archive file contains data for a specific year:

```json
{
  "weeklySummaries": [...],  // All weekly summaries from that year
  "metrics": {
    "robotaxiFleet": { "data": [...] },
    "cybercab": { "data": [...] },
    "jobPostings": { "data": [...] }
  }
}
```

## How Archiving Works

The archiving process runs automatically during `/tesla-update`:

1. **Check current year:** Determine cutoff (e.g., 2025 in 2026)
2. **Identify old data:** Find entries older than cutoff year
3. **Archive by year:** Move to `data/archives/YEAR.json`
4. **Update main file:** Remove archived data

## Manual Archiving

To manually run the archive process:

```bash
python3 scripts/archive_old_data.py
```

## When Archiving Happens

**First archive:** January 1, 2027
- Archives all 2025 data
- Main file keeps only 2026 + 2027 data

**Ongoing:** Automatic on each update
- Continuously moves old data as years complete

## Archive File Sizes

Estimated archive file sizes based on update frequency:

- 2026 archive (~150 weekly updates): ~500 KB
- 2027 archive (~150 weekly updates): ~500 KB
- Older years: Smaller (fewer updates when tracking started)

## Accessing Archived Data

**Current:** Archives are stored as JSON files in this directory

**Future (with React migration):** Dashboard will include an archive browser:
- Select year to view
- Search archived data
- Compare across years
