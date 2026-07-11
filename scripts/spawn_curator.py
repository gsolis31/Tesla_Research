#!/usr/bin/env python3
"""
Spawn tesla-curator agent to validate and merge category findings.

Usage:
    python3 scripts/spawn_curator.py 2026-07-08
    python3 scripts/spawn_curator.py  # uses today's date
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
import glob

def main():
    # Determine date
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = datetime.now().strftime("%Y-%m-%d")

    # Calculate Monday of current week
    now = datetime.now()
    monday = now - timedelta(days=now.weekday())
    week_of = monday.strftime("%Y-%m-%d")

    # Find all findings-*.json files
    findings_files = glob.glob("findings-*.json")

    if not findings_files:
        print("❌ No findings-*.json files found")
        print("   Run tesla-researcher agents first")
        sys.exit(1)

    print(f"Found {len(findings_files)} category findings:")
    for f in sorted(findings_files):
        # Check if it has keyChanges
        with open(f) as file:
            data = json.load(file)
            kc_count = len(data.get('keyChanges', []))
            category = data.get('categoryKey', 'unknown')
            print(f"  ✓ {f:30} ({category:20} - {kc_count} keyChanges)")

    # Load hot context
    data_path = Path(__file__).parent.parent / "tesla-tracking-data.json"
    with open(data_path) as f:
        data = json.load(f)

    # Get last week's keyChanges
    last_week_key_changes = []
    if data['weeklySummaries']:
        last_week_key_changes = data['weeklySummaries'][0].get('keyChanges', [])

    # Create curator config
    config = {
        "date": date,
        "weekOf": week_of,
        "findingsFiles": sorted(findings_files),
        "hotContext": {
            "lastWeekKeyChanges": last_week_key_changes,
            "urlCache": "findings/url-cache.json"
        }
    }

    # Write config file
    config_path = Path(__file__).parent.parent / "curator-config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"\n✅ Created curator config: curator-config.json")
    print(f"\nConfig summary:")
    print(f"  Date: {date}")
    print(f"  Week of: {week_of}")
    print(f"  Category findings: {len(findings_files)}")
    print(f"  Last week keyChanges: {len(last_week_key_changes)}")
    print(f"\nNext: Spawn tesla-curator agent with this config")
    print(f"  Expected output: findings/{date}.json")

if __name__ == "__main__":
    main()
