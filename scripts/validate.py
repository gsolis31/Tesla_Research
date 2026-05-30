#!/usr/bin/env python3
"""
Validation script for Tesla tracking dashboard

Validates:
1. JSON structure and required fields
2. HTML embedded data matches JSON
3. No syntax errors in embedded JavaScript
"""

import json
import re
import sys
from pathlib import Path


def validate_json_structure(data: dict) -> list:
    """Validate JSON has required fields and structure"""
    errors = []

    # Check required top-level fields
    required_fields = ['lastUpdated', 'weeklySummaries', 'metrics', 'categories']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Validate weeklySummaries structure
    if 'weeklySummaries' in data:
        if not isinstance(data['weeklySummaries'], list):
            errors.append("weeklySummaries must be an array")
        elif len(data['weeklySummaries']) > 0:
            first_week = data['weeklySummaries'][0]
            if 'weekOf' not in first_week:
                errors.append("weeklySummaries[0] missing 'weekOf' field")
            if 'keyChanges' not in first_week:
                errors.append("weeklySummaries[0] missing 'keyChanges' field")

            # Validate keyChanges structure
            if 'keyChanges' in first_week and isinstance(first_week['keyChanges'], list):
                for i, change in enumerate(first_week['keyChanges']):
                    required_change_fields = ['category', 'status', 'title', 'description']
                    for field in required_change_fields:
                        if field not in change:
                            errors.append(f"weeklySummaries[0].keyChanges[{i}] missing '{field}'")

    # Validate categories
    if 'categories' in data:
        expected_categories = ['aiChip', 'cybercab', 'fsd', 'jobPostings', 'optimus']
        for cat in expected_categories:
            if cat not in data['categories']:
                errors.append(f"Missing category: {cat}")
            else:
                cat_data = data['categories'][cat]
                if 'title' not in cat_data:
                    errors.append(f"Category {cat} missing 'title' field")
                if 'criticalNews' not in cat_data:
                    errors.append(f"Category {cat} missing 'criticalNews' field")

    # Validate metrics
    if 'metrics' in data:
        expected_metrics = ['cybercab', 'jobPostings', 'robotaxiFleet']
        for metric in expected_metrics:
            if metric not in data['metrics']:
                errors.append(f"Missing metric: {metric}")

    return errors


def validate_html_embed(html_path: str, json_data: dict) -> list:
    """Validate HTML embedded data"""
    errors = []

    try:
        with open(html_path, 'r') as f:
            html_content = f.read()

        # Check markers exist
        if '<!-- DATA_OBJECT_START -->' not in html_content:
            errors.append("HTML missing <!-- DATA_OBJECT_START --> marker")
        if '<!-- DATA_OBJECT_END -->' not in html_content:
            errors.append("HTML missing <!-- DATA_OBJECT_END --> marker")

        # Extract embedded data
        pattern = r'<!-- DATA_OBJECT_START -->\s*const data = ({.*?});?\s*<!-- DATA_OBJECT_END -->'
        match = re.search(pattern, html_content, re.DOTALL)

        if not match:
            errors.append("Could not extract embedded data from HTML")
            return errors

        embedded_json_str = match.group(1)

        # Try to parse embedded JavaScript as JSON
        try:
            embedded_data = json.loads(embedded_json_str)
        except json.JSONDecodeError as e:
            errors.append(f"Embedded data is not valid JSON: {e}")
            return errors

        # Compare key fields
        if embedded_data.get('lastUpdated') != json_data.get('lastUpdated'):
            errors.append(
                f"lastUpdated mismatch: HTML={embedded_data.get('lastUpdated')}, "
                f"JSON={json_data.get('lastUpdated')}"
            )

        # Check weekly summaries count
        html_weeks = len(embedded_data.get('weeklySummaries', []))
        json_weeks = len(json_data.get('weeklySummaries', []))
        if html_weeks != json_weeks:
            errors.append(
                f"weeklySummaries count mismatch: HTML={html_weeks}, JSON={json_weeks}"
            )

    except FileNotFoundError:
        errors.append(f"HTML file not found: {html_path}")
    except Exception as e:
        errors.append(f"Unexpected error validating HTML: {e}")

    return errors


def validate_dashboard(json_path: str = 'tesla-tracking-data.json',
                       html_path: str = 'index.html') -> bool:
    """
    Run all validations

    Returns:
        True if all validations pass, False otherwise
    """
    print("=" * 60)
    print("Tesla Dashboard Validation")
    print("=" * 60)

    all_errors = []

    # 1. Validate JSON exists and is parseable
    print("\n[1/3] Validating JSON structure...")
    try:
        with open(json_path, 'r') as f:
            json_data = json.load(f)
        print(f"✓ JSON is valid and parseable ({json_path})")
    except FileNotFoundError:
        print(f"✗ JSON file not found: {json_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ JSON parse error: {e}")
        return False

    # 2. Validate JSON structure
    structure_errors = validate_json_structure(json_data)
    if structure_errors:
        print(f"✗ Found {len(structure_errors)} structure errors:")
        for error in structure_errors:
            print(f"  - {error}")
        all_errors.extend(structure_errors)
    else:
        print("✓ JSON structure is valid")

    # 3. Validate HTML embed
    print(f"\n[2/3] Validating HTML embed ({html_path})...")
    html_errors = validate_html_embed(html_path, json_data)
    if html_errors:
        print(f"✗ Found {len(html_errors)} HTML errors:")
        for error in html_errors:
            print(f"  - {error}")
        all_errors.extend(html_errors)
    else:
        print("✓ HTML embed is valid and in sync with JSON")

    # Summary
    print("\n" + "=" * 60)
    if all_errors:
        print(f"VALIDATION FAILED: {len(all_errors)} error(s) found")
        print("=" * 60)
        return False
    else:
        print("✓ ALL VALIDATIONS PASSED")
        print("=" * 60)
        return True


if __name__ == '__main__':
    json_file = sys.argv[1] if len(sys.argv) > 1 else 'tesla-tracking-data.json'
    html_file = sys.argv[2] if len(sys.argv) > 2 else 'index.html'

    success = validate_dashboard(json_file, html_file)
    sys.exit(0 if success else 1)
