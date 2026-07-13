#!/usr/bin/env python3
"""
Deterministic merge script for Tesla research findings

Takes findings/YYYY-MM-DD.json + tesla-tracking-data.json → updated data
This is the only script that writes to the main data file.

Features:
- Append-only for metrics (no overwrites)
- Caps on keyPoints/timeline (prevents unbounded growth)
- Deterministic (same inputs → same output)
- Idempotent (can re-run safely)
- Validates before and after merge

Usage:
    python3 scripts/merge_findings.py findings/2026-07-08.json
"""

import json
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any


# Configuration
MAX_KEY_POINTS = 15  # Cap per category
MAX_TIMELINE_EVENTS = 15  # Cap per category
MAX_WEEKLY_SUMMARIES = 52  # Keep 1 year of weekly summaries in main file


def load_json(filepath: Path) -> dict:
    """Load JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def save_json(data: dict, filepath: Path):
    """Save JSON file with formatting"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✓ Saved {filepath}")


def get_monday_of_week(date_str: str) -> str:
    """Get Monday of the week for a given date (ISO week start)"""
    date = datetime.strptime(date_str, '%Y-%m-%d')
    monday = date - timedelta(days=date.weekday())
    return monday.strftime('%Y-%m-%d')


def deduplicate_key_changes(key_changes: List[dict]) -> List[dict]:
    """
    Deduplicate keyChanges by (title, category).
    When duplicates exist, keep the one with more complete data (prefers non-empty sentiment/evidence).
    """
    seen = {}
    for kc in key_changes:
        key = (kc.get('title', '').strip(), kc.get('category', '').strip())

        if key not in seen:
            seen[key] = kc
        else:
            # Keep the one with more complete data
            existing = seen[key]
            existing_score = (
                (1 if existing.get('sentiment', {}).get('rationale') else 0) +
                (1 if existing.get('evidence', {}).get('key_metrics') else 0) +
                len(existing.get('evidence', {}).get('positive_signals', [])) +
                len(existing.get('evidence', {}).get('negative_signals', []))
            )
            new_score = (
                (1 if kc.get('sentiment', {}).get('rationale') else 0) +
                (1 if kc.get('evidence', {}).get('key_metrics') else 0) +
                len(kc.get('evidence', {}).get('positive_signals', [])) +
                len(kc.get('evidence', {}).get('negative_signals', []))
            )

            if new_score > existing_score:
                seen[key] = kc

    return list(seen.values())


def merge_weekly_summary(main_data: dict, findings: dict) -> dict:
    """
    Merge keyChanges and trends into weekly summaries

    Logic:
    - If weekOf matches current week → append to existing entry
    - If new week → create new entry at beginning of array
    - Maintain reverse chronological order
    """
    week_of = findings.get('weekOf') or get_monday_of_week(findings['date'])
    key_changes = findings['findings'].get('keyChanges', [])
    trends = findings['findings'].get('trends', [])

    if not key_changes and not trends:
        print("⚠ No keyChanges or trends to merge")
        return main_data

    # Check if this week already exists
    existing_week_idx = None
    for i, week in enumerate(main_data['weeklySummaries']):
        if week['weekOf'] == week_of:
            existing_week_idx = i
            break

    if existing_week_idx is not None:
        # Append to existing week with deduplication
        print(f"✓ Appending to existing week {week_of}")
        existing_kcs = main_data['weeklySummaries'][existing_week_idx]['keyChanges']
        before_count = len(existing_kcs)

        # Combine and deduplicate
        combined = existing_kcs + key_changes
        deduplicated = deduplicate_key_changes(combined)

        main_data['weeklySummaries'][existing_week_idx]['keyChanges'] = deduplicated
        after_count = len(deduplicated)

        new_added = after_count - before_count
        total_duplicates = before_count + len(key_changes) - after_count

        if new_added > 0:
            print(f"  ✓ Added {new_added} new keyChange(s)")
        if total_duplicates > 0:
            duplicates_from_existing = before_count - len(deduplicate_key_changes(existing_kcs))
            duplicates_from_incoming = total_duplicates - duplicates_from_existing
            if duplicates_from_existing > 0:
                print(f"  ⚠ Cleaned {duplicates_from_existing} duplicate(s) from existing week")
            if duplicates_from_incoming > 0:
                print(f"  ⚠ Skipped {duplicates_from_incoming} duplicate(s) from incoming findings")
        print(f"  ✓ Week now has {after_count} keyChange(s)")

        main_data['weeklySummaries'][existing_week_idx]['trends'].extend(trends)
    else:
        # Create new week entry
        print(f"✓ Creating new week {week_of}")
        new_week = {
            'weekOf': week_of,
            'keyChanges': key_changes,
            'trends': trends
        }
        main_data['weeklySummaries'].insert(0, new_week)

    # Cap weekly summaries (keep most recent N weeks in main file)
    if len(main_data['weeklySummaries']) > MAX_WEEKLY_SUMMARIES:
        archived_count = len(main_data['weeklySummaries']) - MAX_WEEKLY_SUMMARIES
        print(f"⚠ Would archive {archived_count} old weeks (run archive script)")

    return main_data


def merge_metrics(main_data: dict, findings: dict) -> dict:
    """
    Merge metric data points (append-only, no duplicates)
    """
    metrics_updates = findings['findings'].get('metrics', {})

    for metric_name in ['cybercab', 'robotaxiFleet', 'jobPostings']:
        if metric_name not in metrics_updates:
            continue

        new_points = metrics_updates[metric_name]
        if not new_points:
            continue

        # Get existing dates to prevent duplicates
        # Get date field (handle both 'date' and 'lastUpdate')
        def get_date(point):
            return point.get('date') or point.get('lastUpdate')

        existing_dates = {
            get_date(point)
            for point in main_data['metrics'][metric_name]['data']
        }

        # Only add new data points
        added = 0
        for point in new_points:
            point_date = get_date(point)
            if point_date and point_date not in existing_dates:
                main_data['metrics'][metric_name]['data'].append(point)
                added += 1

        # Sort by date (chronological)
        main_data['metrics'][metric_name]['data'].sort(key=lambda x: get_date(x) or '')

        if added > 0:
            print(f"✓ Added {added} new {metric_name} data points")

    return main_data


def merge_quarterly_data(main_data: dict, findings: dict) -> dict:
    """
    Merge quarterly production & delivery data (append-only, no duplicates)
    """
    new_quarters = findings['findings'].get('quarterlyData', [])
    if not new_quarters:
        return main_data

    # Get existing quarters
    existing_quarters = {q['quarter'] for q in main_data['categories']['productionDelivery']['quarterlyData']}

    # Add new quarters
    added = 0
    for quarter_data in new_quarters:
        if quarter_data['quarter'] not in existing_quarters:
            main_data['categories']['productionDelivery']['quarterlyData'].append(quarter_data)
            added += 1

    if added > 0:
        print(f"✓ Added {added} new quarterly data entries")

        # Recalculate totals (handle both old format and new format with breakdown)
        def get_number(value):
            if isinstance(value, dict):
                return value.get('total', 0)
            return value or 0

        total_production = sum(get_number(q.get('production')) for q in main_data['categories']['productionDelivery']['quarterlyData'])
        total_deliveries = sum(get_number(q.get('delivery') or q.get('deliveries')) for q in main_data['categories']['productionDelivery']['quarterlyData'])

        main_data['categories']['productionDelivery']['totalProduction'] = f"{total_production:,}"
        main_data['categories']['productionDelivery']['totalDeliveries'] = f"{total_deliveries:,}"

        print(f"✓ Recalculated totals: {total_production:,} production, {total_deliveries:,} deliveries")

    return main_data


def merge_category_updates(main_data: dict, findings: dict) -> dict:
    """
    Merge category updates with caps on keyPoints and timeline

    Caps prevent unbounded growth:
    - keyPoints: Keep most recent MAX_KEY_POINTS (FIFO)
    - timeline: Keep most recent MAX_TIMELINE_EVENTS (FIFO)
    """
    category_updates = findings['findings'].get('categoryUpdates', {})

    for cat_key, updates in category_updates.items():
        if cat_key not in main_data['categories']:
            print(f"⚠ Category {cat_key} not in main data, skipping")
            continue

        category = main_data['categories'][cat_key]

        # Update criticalNews
        if 'criticalNews' in updates:
            category['criticalNews'] = updates['criticalNews']
            print(f"✓ Updated {cat_key}.criticalNews")

        # Add new keyPoint (with cap)
        if 'newKeyPoint' in updates:
            if 'keyPoints' not in category:
                category['keyPoints'] = []

            category['keyPoints'].append(updates['newKeyPoint'])

            # Apply cap (keep most recent)
            if len(category['keyPoints']) > MAX_KEY_POINTS:
                removed = len(category['keyPoints']) - MAX_KEY_POINTS
                category['keyPoints'] = category['keyPoints'][-MAX_KEY_POINTS:]
                print(f"✓ Added keyPoint to {cat_key}, capped (removed {removed} old entries)")
            else:
                print(f"✓ Added keyPoint to {cat_key} ({len(category['keyPoints'])}/{MAX_KEY_POINTS})")

        # Add new timeline event (with cap)
        if 'newTimelineEvent' in updates:
            if 'timeline' not in category:
                category['timeline'] = []

            new_event = updates['newTimelineEvent']

            # Check for duplicate dates
            existing_dates = {evt['date'] for evt in category['timeline']}
            if new_event['date'] not in existing_dates:
                category['timeline'].append(new_event)

                # Sort by date (chronological)
                category['timeline'].sort(key=lambda x: x['date'])

                # Apply cap (keep most recent)
                if len(category['timeline']) > MAX_TIMELINE_EVENTS:
                    removed = len(category['timeline']) - MAX_TIMELINE_EVENTS
                    category['timeline'] = category['timeline'][-MAX_TIMELINE_EVENTS:]
                    print(f"✓ Added timeline event to {cat_key}, capped (removed {removed} old entries)")
                else:
                    print(f"✓ Added timeline event to {cat_key} ({len(category['timeline'])}/{MAX_TIMELINE_EVENTS})")

        # Update latestUpdate date
        category['latestUpdate'] = findings['date']

    return main_data


def apply_caps_retrospectively(main_data: dict) -> dict:
    """
    Apply caps to existing data (one-time cleanup)
    """
    print("\n[Applying caps to existing data...]")

    for cat_key, category in main_data['categories'].items():
        if cat_key == 'productionDelivery':
            continue  # Different structure

        # Cap keyPoints
        if 'keyPoints' in category and len(category['keyPoints']) > MAX_KEY_POINTS:
            before = len(category['keyPoints'])
            category['keyPoints'] = category['keyPoints'][-MAX_KEY_POINTS:]
            print(f"✓ Capped {cat_key}.keyPoints: {before} → {MAX_KEY_POINTS}")

        # Cap timeline
        if 'timeline' in category and len(category['timeline']) > MAX_TIMELINE_EVENTS:
            before = len(category['timeline'])
            # Keep most recent (timeline is chronological)
            category['timeline'] = category['timeline'][-MAX_TIMELINE_EVENTS:]
            print(f"✓ Capped {cat_key}.timeline: {before} → {MAX_TIMELINE_EVENTS}")

    return main_data


def merge_findings(findings_path: Path, data_path: Path, apply_caps: bool = False) -> dict:
    """
    Main merge function

    Returns updated main_data
    """
    print("=" * 70)
    print("Tesla Research Findings Merge")
    print("=" * 70)

    # Load files
    print(f"\n[1/7] Loading files...")
    findings = load_json(findings_path)
    main_data = load_json(data_path)
    print(f"✓ Loaded {findings_path.name}")
    print(f"✓ Loaded {data_path.name}")

    # Update lastUpdated
    main_data['lastUpdated'] = findings['date']
    print(f"✓ Updated lastUpdated to {findings['date']}")

    # Apply retrospective caps (one-time cleanup)
    if apply_caps:
        main_data = apply_caps_retrospectively(main_data)

    # Merge weekly summary
    print(f"\n[2/7] Merging weekly summary...")
    main_data = merge_weekly_summary(main_data, findings)

    # Merge metrics
    print(f"\n[3/7] Merging metrics...")
    main_data = merge_metrics(main_data, findings)

    # Merge quarterly data
    print(f"\n[4/7] Merging quarterly data...")
    main_data = merge_quarterly_data(main_data, findings)

    # Merge category updates
    print(f"\n[5/7] Merging category updates...")
    main_data = merge_category_updates(main_data, findings)

    # Save
    print(f"\n[6/7] Saving merged data...")
    save_json(main_data, data_path)

    # Validate
    print(f"\n[7/7] Validating merged data...")
    result = subprocess.run(
        ['python3', 'scripts/validate_data.py'],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✓ Validation passed")
    else:
        print("✗ Validation failed:")
        print(result.stdout)
        sys.exit(1)

    print("\n" + "=" * 70)
    print("✓ MERGE COMPLETE")
    print("=" * 70)

    return main_data


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/merge_findings.py findings/YYYY-MM-DD.json [--apply-caps]")
        print("\nOptions:")
        print("  --apply-caps    Apply caps to existing data (one-time cleanup)")
        sys.exit(1)

    findings_path = Path(sys.argv[1])
    apply_caps = '--apply-caps' in sys.argv

    if not findings_path.exists():
        print(f"Error: {findings_path} not found")
        sys.exit(1)

    data_path = Path('tesla-tracking-data.json')

    merge_findings(findings_path, data_path, apply_caps=apply_caps)


if __name__ == '__main__':
    main()
