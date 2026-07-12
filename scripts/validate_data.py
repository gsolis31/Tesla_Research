#!/usr/bin/env python3
"""
Validation script for Tesla tracking data (React/Vite version)

This script validates:
1. JSON is valid and parseable
2. Required schema fields exist
3. Data types are correct
4. Business logic invariants hold
5. No orphaned categories (data exists but not rendered in UI)

Exit codes:
  0 - All validations passed
  1 - Validation failed
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


def validate_json_structure(data: dict) -> List[str]:
    """Validate JSON has required fields and correct types"""
    errors = []

    # Check required top-level fields
    required_fields = ['lastUpdated', 'weeklySummaries', 'metrics', 'categories']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
            return errors  # Can't continue without these

    # Validate lastUpdated format (YYYY-MM-DD)
    try:
        datetime.strptime(data['lastUpdated'], '%Y-%m-%d')
    except ValueError:
        errors.append(f"lastUpdated must be YYYY-MM-DD format, got: {data['lastUpdated']}")

    # Validate weeklySummaries structure
    if not isinstance(data['weeklySummaries'], list):
        errors.append("weeklySummaries must be an array")
    else:
        for i, week in enumerate(data['weeklySummaries']):
            if 'weekOf' not in week:
                errors.append(f"weeklySummaries[{i}] missing 'weekOf' field")
            else:
                try:
                    datetime.strptime(week['weekOf'], '%Y-%m-%d')
                except ValueError:
                    errors.append(f"weeklySummaries[{i}].weekOf must be YYYY-MM-DD format")

            if 'keyChanges' not in week:
                errors.append(f"weeklySummaries[{i}] missing 'keyChanges' field")
            elif isinstance(week['keyChanges'], list):
                for j, change in enumerate(week['keyChanges']):
                    required_change_fields = ['category', 'status', 'title', 'description', 'source']
                    for field in required_change_fields:
                        if field not in change:
                            errors.append(f"weeklySummaries[{i}].keyChanges[{j}] missing '{field}'")

                    # Validate status enum
                    if 'status' in change and change['status'] not in ['positive', 'negative', 'neutral']:
                        errors.append(f"weeklySummaries[{i}].keyChanges[{j}].status must be positive/negative/neutral")

                    # Validate source is URL
                    if 'source' in change and not change['source'].startswith('http'):
                        errors.append(f"weeklySummaries[{i}].keyChanges[{j}].source must be a URL")

                    # Validate title length
                    if 'title' in change and len(change['title']) > 120:
                        errors.append(f"weeklySummaries[{i}].keyChanges[{j}].title exceeds 120 chars")

    # Validate categories
    expected_categories = {
        'aiChip': 'AI Chip Production',
        'battery4680': '4680 Battery Cell Production',
        'cybercab': 'Cybercab Production',
        'fsd': 'FSD Country Approvals',
        'jobPostings': 'Job Postings',
        'optimus': 'Optimus Production',
        'productionDelivery': 'Vehicle Production & Delivery',
        'terafab': 'Terafab In-House Chip Manufacturing',
    }

    if 'categories' in data:
        for cat_key, cat_name in expected_categories.items():
            if cat_key not in data['categories']:
                errors.append(f"Missing category: {cat_key} ({cat_name})")
            else:
                cat_data = data['categories'][cat_key]
                required_cat_fields = ['title', 'latestUpdate', 'criticalNews']
                for field in required_cat_fields:
                    if field not in cat_data:
                        errors.append(f"Category {cat_key} missing '{field}' field")

                # Validate latestUpdate date
                if 'latestUpdate' in cat_data:
                    try:
                        datetime.strptime(cat_data['latestUpdate'], '%Y-%m-%d')
                    except ValueError:
                        errors.append(f"Category {cat_key}.latestUpdate must be YYYY-MM-DD format")

        # Check for extra categories not in the expected list
        for cat_key in data['categories'].keys():
            if cat_key not in expected_categories:
                errors.append(f"Unknown category '{cat_key}' found in data (not in schema)")

    # Validate metrics
    expected_metrics = ['cybercab', 'jobPostings', 'robotaxiFleet', 'robotaxiCities', 'fsdApprovals']
    if 'metrics' in data:
        for metric in expected_metrics:
            if metric not in data['metrics']:
                errors.append(f"Missing metric: {metric}")

        # Validate metric data arrays
        for metric_name in ['cybercab', 'jobPostings', 'robotaxiFleet']:
            if metric_name in data['metrics'] and 'data' in data['metrics'][metric_name]:
                metric_data = data['metrics'][metric_name]['data']
                if not isinstance(metric_data, list):
                    errors.append(f"metrics.{metric_name}.data must be an array")
                else:
                    for i, point in enumerate(metric_data):
                        if 'date' not in point:
                            errors.append(f"metrics.{metric_name}.data[{i}] missing 'date'")
                        if 'count' not in point:
                            errors.append(f"metrics.{metric_name}.data[{i}] missing 'count'")
                        elif not isinstance(point['count'], int) or point['count'] < 0:
                            errors.append(f"metrics.{metric_name}.data[{i}].count must be non-negative integer")

    return errors


def validate_data_invariants(data: dict) -> Tuple[List[str], List[Tuple[str, str]]]:
    """
    Validate business logic and data consistency
    Returns (errors, warnings) tuple
    """
    errors = []
    warnings = []

    # Check weekly summaries are in reverse chronological order
    weeks = [w['weekOf'] for w in data.get('weeklySummaries', [])]
    for i in range(len(weeks) - 1):
        if weeks[i] < weeks[i + 1]:
            errors.append(f"Weekly summaries not in reverse chronological order: {weeks[i]} < {weeks[i + 1]}")

    # Check for duplicate weeks
    week_set = set(weeks)
    if len(week_set) != len(weeks):
        duplicates = [w for w in weeks if weeks.count(w) > 1]
        errors.append(f"Duplicate weekly summaries found: {set(duplicates)}")

    # Check metric dates are in chronological order
    def check_metric_dates(metric_name: str, metric_data: List[Dict[str, Any]]):
        dates = [d['date'] for d in metric_data if 'date' in d]
        for i in range(len(dates) - 1):
            if dates[i] > dates[i + 1]:
                errors.append(f"metrics.{metric_name}.data not in chronological order: {dates[i]} > {dates[i + 1]}")

    metrics = data.get('metrics', {})
    if 'cybercab' in metrics and 'data' in metrics['cybercab']:
        check_metric_dates('cybercab', metrics['cybercab']['data'])
    if 'robotaxiFleet' in metrics and 'data' in metrics['robotaxiFleet']:
        check_metric_dates('robotaxiFleet', metrics['robotaxiFleet']['data'])
    if 'jobPostings' in metrics and 'data' in metrics['jobPostings']:
        check_metric_dates('jobPostings', metrics['jobPostings']['data'])

    # Check robotaxi cities summary consistency
    if 'robotaxiCities' in metrics:
        cities = metrics['robotaxiCities']
        if 'cities' in cities and 'summary' in cities:
            actual_total = sum(c.get('activeVehicles') or 0 for c in cities['cities'])
            expected_total = cities['summary'].get('totalActiveVehicles', 0)
            if actual_total != expected_total:
                warnings.append((
                    'summary_mismatch',
                    f"RobotaxiCities summary mismatch: sum of city vehicles ({actual_total}) != "
                    f"summary.totalActiveVehicles ({expected_total})"
                ))

            actual_active_cities = len([c for c in cities['cities'] if c.get('status') == 'active'])
            expected_active_cities = cities['summary'].get('activeCities', 0)
            if actual_active_cities != expected_active_cities:
                warnings.append((
                    'summary_mismatch',
                    f"RobotaxiCities summary mismatch: active cities count ({actual_active_cities}) != "
                    f"summary.activeCities ({expected_active_cities})"
                ))

    # Validate keyChange categories match known categories
    # These are the canonical category names (full versions)
    canonical_category_names = {
        'AI Chip Production',
        '4680 Battery Cell Production',
        'Cybercab Production',
        'FSD Country Approvals',
        'FSD v15 Software',
        'Job Postings',
        'Optimus Production',
        'Vehicle Production & Delivery',
        'Terafab In-House Chip Manufacturing',
    }

    # Legacy/abbreviated names that should be updated but are still valid
    legacy_category_names = {
        'AI Chip': 'AI Chip Production',
        'Cybercab': 'Cybercab Production',
        'FSD': 'FSD Country Approvals',
        'FSD Approvals': 'FSD Country Approvals',
        'FSD v14 Software': 'FSD v15 Software',
        'Optimus': 'Optimus Production',
        'Production & Delivery': 'Vehicle Production & Delivery',
        'Robotaxi': 'Cybercab Production',
        'Terafab Manufacturing': 'Terafab In-House Chip Manufacturing',
    }

    valid_category_names = canonical_category_names | set(legacy_category_names.keys())

    for i, week in enumerate(data.get('weeklySummaries', [])):
        for j, change in enumerate(week.get('keyChanges', [])):
            category = change.get('category', '')
            if category and category not in valid_category_names:
                errors.append(
                    f"weeklySummaries[{i}].keyChanges[{j}].category '{category}' not recognized"
                )

    return errors, warnings


def validate_ui_coverage(data: dict) -> List[Tuple[str, str]]:
    """
    Check for data that exists in JSON but might not render in UI
    Returns list of (warning_type, message) tuples
    """
    warnings = []

    # Categories in JSON vs expected UI tabs
    json_categories = set(data.get('categories', {}).keys())

    # Check src/components/Categories.tsx to see what actually renders
    # For now, we'll check against the type definition
    ui_categories = {
        'aiChip',
        'battery4680',
        'cybercab',
        'fsd',
        'jobPostings',
        'optimus',
        'productionDelivery',
        'terafab',
    }

    orphaned = json_categories - ui_categories
    if orphaned:
        warnings.append((
            'orphaned_data',
            f"Categories in JSON but not in UI: {orphaned}"
        ))

    return warnings


def main():
    """Run all validations"""
    print("=" * 70)
    print("Tesla Dashboard Data Validation (React/Vite)")
    print("=" * 70)

    json_path = Path(__file__).parent.parent / 'tesla-tracking-data.json'

    all_errors = []
    all_warnings = []

    # 1. Load and parse JSON
    print("\n[1/4] Loading JSON file...")
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        print(f"✓ JSON loaded successfully ({json_path.name}, {json_path.stat().st_size:,} bytes)")
    except FileNotFoundError:
        print(f"✗ JSON file not found: {json_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ JSON parse error: {e}")
        return False

    # 2. Validate structure
    print("\n[2/4] Validating data structure...")
    structure_errors = validate_json_structure(data)
    if structure_errors:
        print(f"✗ Found {len(structure_errors)} structure errors:")
        for error in structure_errors:
            print(f"  - {error}")
        all_errors.extend(structure_errors)
    else:
        print("✓ Data structure is valid")

    # 3. Validate invariants
    print("\n[3/4] Validating data invariants...")
    invariant_errors, invariant_warnings = validate_data_invariants(data)
    if invariant_errors:
        print(f"✗ Found {len(invariant_errors)} invariant errors:")
        for error in invariant_errors:
            print(f"  - {error}")
        all_errors.extend(invariant_errors)
    else:
        print("✓ Data invariants are valid")

    if invariant_warnings:
        print(f"⚠  Found {len(invariant_warnings)} invariant warnings:")
        for _, warning in invariant_warnings:
            print(f"  - {warning}")
        all_warnings.extend(invariant_warnings)

    # 4. Check UI coverage
    print("\n[4/4] Checking UI coverage...")
    ui_warnings = validate_ui_coverage(data)
    if ui_warnings:
        print(f"⚠ Found {len(ui_warnings)} warnings:")
        for warning_type, message in ui_warnings:
            print(f"  - {message}")
        all_warnings.extend(ui_warnings)
    else:
        print("✓ All data is covered by UI")

    # Summary
    print("\n" + "=" * 70)
    if all_errors:
        print(f"❌ VALIDATION FAILED: {len(all_errors)} error(s) found")
        if all_warnings:
            print(f"⚠  Plus {len(all_warnings)} warning(s)")
        print("=" * 70)
        return False
    elif all_warnings:
        print(f"⚠  VALIDATION PASSED WITH WARNINGS: {len(all_warnings)} warning(s)")
        print("=" * 70)
        return True
    else:
        print("✅ ALL VALIDATIONS PASSED")
        print("=" * 70)
        return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
