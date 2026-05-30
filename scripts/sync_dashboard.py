#!/usr/bin/env python3
"""
Sync Dashboard - Shared utility for syncing JSON data to HTML dashboard

This script reads tesla-tracking-data.json and embeds it into index.html
between the marker comments. Used by both auto_update.py and the /tesla-update skill.
"""

import json
import re
import sys
from pathlib import Path


def sync_dashboard(json_path: str = 'tesla-tracking-data.json', html_path: str = 'index.html') -> bool:
    """
    Sync JSON data to HTML dashboard

    Args:
        json_path: Path to the JSON data file
        html_path: Path to the HTML dashboard file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Read JSON data
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Read HTML file
        with open(html_path, 'r') as f:
            html_content = f.read()

        # Verify markers exist
        if '<!-- DATA_OBJECT_START -->' not in html_content:
            print(f"ERROR: Marker '<!-- DATA_OBJECT_START -->' not found in {html_path}")
            print("See SKILL.md 'One-Time Setup' section for marker installation")
            return False

        if '<!-- DATA_OBJECT_END -->' not in html_content:
            print(f"ERROR: Marker '<!-- DATA_OBJECT_END -->' not found in {html_path}")
            print("See SKILL.md 'One-Time Setup' section for marker installation")
            return False

        # Format JSON as JavaScript with proper indentation (8 spaces base indent)
        json_str = json.dumps(data, indent=2)
        js_lines = json_str.split('\n')

        indented_js = '        const data = ' + js_lines[0] + '\n'
        for line in js_lines[1:]:
            indented_js += '        ' + line + '\n'
        indented_js = indented_js.rstrip() + ';\n'

        # Replace between markers using regex
        pattern = r'(<!-- DATA_OBJECT_START -->\n).*?(<!-- DATA_OBJECT_END -->)'
        new_html = re.sub(pattern, rf'\1{indented_js}        \2', html_content, flags=re.DOTALL)

        # Write updated HTML
        with open(html_path, 'w') as f:
            f.write(new_html)

        print(f"✓ Dashboard synced: {json_path} → {html_path}")
        return True

    except FileNotFoundError as e:
        print(f"ERROR: File not found - {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {json_path} - {e}")
        return False
    except Exception as e:
        print(f"ERROR: Failed to sync dashboard - {e}")
        return False


if __name__ == '__main__':
    # Allow override of file paths via command line
    json_file = sys.argv[1] if len(sys.argv) > 1 else 'tesla-tracking-data.json'
    html_file = sys.argv[2] if len(sys.argv) > 2 else 'index.html'

    success = sync_dashboard(json_file, html_file)
    sys.exit(0 if success else 1)
