#!/usr/bin/env python3
"""
Archive old data to keep main file size manageable.

Strategy: Keep current year + previous year in main file.
Archive everything older by year.

Example (in 2026):
- Keep: 2025 + 2026 data
- Archive: 2024 and earlier → archives/2024.json, archives/2023.json, etc.
"""

import json
import os
from datetime import datetime
from collections import defaultdict


def load_data(filepath='tesla-tracking-data.json'):
    """Load the main data file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def save_data(data, filepath='tesla-tracking-data.json'):
    """Save the main data file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def save_archive(archive_data, year):
    """Save archived data to archives/YEAR.json."""
    os.makedirs('archives', exist_ok=True)
    filepath = f'archives/{year}.json'

    with open(filepath, 'w') as f:
        json.dump(archive_data, f, indent=2)

    print(f"✓ Archived {year} data to {filepath}")


def archive_by_year(data):
    """
    Archive old data by year, keeping current + previous year in main file.

    Returns:
        - updated_data: Main file with only recent years
        - archives: Dict of {year: archived_data}
    """
    current_year = datetime.now().year
    cutoff_year = current_year - 1  # Keep current + previous year

    archives = defaultdict(lambda: {
        'weeklySummaries': [],
        'metrics': {
            'robotaxiFleet': {'data': []},
            'cybercab': {'data': []},
            'jobPostings': {'data': []}
        }
    })

    # Track what we're archiving
    archived_count = {'weeklySummaries': 0, 'robotaxiFleet': 0, 'cybercab': 0, 'jobPostings': 0}

    # Archive old weekly summaries
    recent_summaries = []
    for summary in data.get('weeklySummaries', []):
        week_year = int(summary['weekOf'][:4])
        if week_year >= cutoff_year:
            recent_summaries.append(summary)
        else:
            archives[week_year]['weeklySummaries'].append(summary)
            archived_count['weeklySummaries'] += 1

    data['weeklySummaries'] = recent_summaries

    # Archive old robotaxi fleet data
    if 'metrics' in data and 'robotaxiFleet' in data['metrics']:
        recent_fleet_data = []
        for entry in data['metrics']['robotaxiFleet'].get('data', []):
            entry_year = int(entry['date'][:4])
            if entry_year >= cutoff_year:
                recent_fleet_data.append(entry)
            else:
                archives[entry_year]['metrics']['robotaxiFleet']['data'].append(entry)
                archived_count['robotaxiFleet'] += 1

        data['metrics']['robotaxiFleet']['data'] = recent_fleet_data

    # Archive old cybercab data
    if 'metrics' in data and 'cybercab' in data['metrics']:
        recent_cybercab_data = []
        for entry in data['metrics']['cybercab'].get('data', []):
            entry_year = int(entry['date'][:4])
            if entry_year >= cutoff_year:
                recent_cybercab_data.append(entry)
            else:
                archives[entry_year]['metrics']['cybercab']['data'].append(entry)
                archived_count['cybercab'] += 1

        data['metrics']['cybercab']['data'] = recent_cybercab_data

    # Archive old job postings data
    if 'metrics' in data and 'jobPostings' in data['metrics']:
        recent_job_data = []
        for entry in data['metrics']['jobPostings'].get('data', []):
            entry_year = int(entry['date'][:4])
            if entry_year >= cutoff_year:
                recent_job_data.append(entry)
            else:
                archives[entry_year]['metrics']['jobPostings']['data'].append(entry)
                archived_count['jobPostings'] += 1

        data['metrics']['jobPostings']['data'] = recent_job_data

    # NOTE: We keep ALL quarterlyData forever (only 4 entries per year, valuable for YoY comparison)

    return data, archives, archived_count


def main():
    """Main archive process."""
    print("============================================================")
    print("Tesla Data Archiving")
    print("============================================================\n")

    current_year = datetime.now().year
    cutoff_year = current_year - 1

    print(f"Current year: {current_year}")
    print(f"Retention policy: Keep {cutoff_year} + {current_year} in main file")
    print(f"Archive: {cutoff_year - 1} and earlier\n")

    # Load data
    print("[1/4] Loading tesla-tracking-data.json...")
    data = load_data()

    # Count current data
    weekly_count = len(data.get('weeklySummaries', []))
    fleet_count = len(data.get('metrics', {}).get('robotaxiFleet', {}).get('data', []))

    print(f"✓ Loaded {weekly_count} weekly summaries, {fleet_count} fleet data points\n")

    # Archive old data
    print("[2/4] Archiving old data...")
    updated_data, archives, archived_count = archive_by_year(data)

    if not any(archives.values()):
        print("✓ No data to archive (all data is recent)\n")
    else:
        print(f"✓ Found data to archive:")
        for year, archive in sorted(archives.items()):
            summary_count = len(archive['weeklySummaries'])
            fleet_count = len(archive['metrics']['robotaxiFleet']['data'])
            if summary_count > 0 or fleet_count > 0:
                print(f"  - {year}: {summary_count} summaries, {fleet_count} fleet points")
        print()

    # Save archives
    print("[3/4] Saving archives...")
    if archives:
        for year, archive_data in sorted(archives.items()):
            save_archive(archive_data, year)
    else:
        print("✓ No archives to save\n")

    # Save updated main file
    print("[4/4] Updating main file...")
    save_data(updated_data)

    new_weekly_count = len(updated_data.get('weeklySummaries', []))
    new_fleet_count = len(updated_data.get('metrics', {}).get('robotaxiFleet', {}).get('data', []))

    print(f"✓ Main file now contains:")
    print(f"  - {new_weekly_count} weekly summaries (was {weekly_count})")
    print(f"  - {new_fleet_count} fleet data points (was {fleet_count})")

    if archived_count['weeklySummaries'] > 0 or archived_count['robotaxiFleet'] > 0:
        print(f"\n✓ Archived:")
        print(f"  - {archived_count['weeklySummaries']} weekly summaries")
        print(f"  - {archived_count['robotaxiFleet']} fleet data points")

    print("\n============================================================")
    print("✓ ARCHIVING COMPLETE")
    print("============================================================")


if __name__ == '__main__':
    main()
