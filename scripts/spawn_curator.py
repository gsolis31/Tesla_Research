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

sys.path.insert(0, str(Path(__file__).parent))
from paths import (  # noqa: E402
    TRACKING_DATA,
    RAW_DIR,
    URL_CACHE,
    ensure_research_dirs,
    curator_config_path,
    curated_findings_path,
)


def main():
    ensure_research_dirs()

    # Determine date
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = datetime.now().strftime("%Y-%m-%d")

    # Calculate Monday of current week
    now = datetime.now()
    monday = now - timedelta(days=now.weekday())
    week_of = monday.strftime("%Y-%m-%d")

    # Find all findings-*.json files in research/raw/
    findings_files = sorted(RAW_DIR.glob("findings-*.json"))

    if not findings_files:
        print(f"❌ No findings-*.json files found in {RAW_DIR}")
        print("   Run tesla-researcher agents first")
        sys.exit(1)

    print(f"Found {len(findings_files)} category findings:")
    relative_paths = []
    for f in findings_files:
        with open(f) as file:
            data = json.load(file)
            kc_count = len(data.get('keyChanges', []))
            category = data.get('categoryKey', 'unknown')
            rel = str(f.as_posix())
            # Store path relative to repo root for agent portability
            try:
                from paths import ROOT
                rel = str(f.relative_to(ROOT))
            except Exception:
                pass
            relative_paths.append(rel)
            print(f"  ✓ {f.name:30} ({category:20} - {kc_count} keyChanges)")

    with open(TRACKING_DATA) as f:
        data = json.load(f)

    last_week_key_changes = []
    if data['weeklySummaries']:
        last_week_key_changes = data['weeklySummaries'][0].get('keyChanges', [])

    try:
        from paths import ROOT
        url_cache_rel = str(URL_CACHE.relative_to(ROOT))
    except Exception:
        url_cache_rel = str(URL_CACHE)

    config = {
        "date": date,
        "weekOf": week_of,
        "findingsFiles": relative_paths,
        "hotContext": {
            "lastWeekKeyChanges": last_week_key_changes,
            "urlCache": url_cache_rel,
        },
        "outputPath": str(curated_findings_path(date).as_posix()),
    }

    config_path = curator_config_path()
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"\n✅ Created curator config: {config_path}")
    print(f"\nConfig summary:")
    print(f"  Date: {date}")
    print(f"  Week of: {week_of}")
    print(f"  Category findings: {len(findings_files)}")
    print(f"  Last week keyChanges: {len(last_week_key_changes)}")
    print(f"\nNext: Spawn tesla-curator agent with this config")
    print(f"  Expected output: research/findings/{date}.json")


if __name__ == "__main__":
    main()
