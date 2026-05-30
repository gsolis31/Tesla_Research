#!/usr/bin/env python3
"""
Tesla Tracker Auto-Update Script
Runs automated weekly updates using Claude API and web searches
"""

import json
import os
import re
from datetime import datetime, timedelta
from anthropic import Anthropic

def read_current_data():
    """Read tesla-tracking-data.json"""
    # Read main file only - archive is kept separate to avoid duplication
    with open('tesla-tracking-data.json', 'r') as f:
        data = json.load(f)

    return data

def update_html_dashboard(data):
    """Sync the HTML dashboard with updated JSON data using shared sync script"""
    from sync_dashboard import sync_dashboard

    if not sync_dashboard():
        raise RuntimeError("Failed to sync dashboard")

def run_tesla_update():
    """Main update function using Claude API"""

    # Check for API key
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not found in environment")
        return False

    client = Anthropic(api_key=api_key)

    # Read current data
    data = read_current_data()
    last_updated = data['lastUpdated']
    today = datetime.now().strftime('%Y-%m-%d')

    print(f"Last updated: {last_updated}")
    print(f"Today: {today}")

    # Check if update is needed (skip if updated today)
    if last_updated == today:
        print("Already updated today. Skipping.")
        return False

    # Read the SKILL.md to get update instructions
    with open('.claude/skills/tesla-update/SKILL.md', 'r') as f:
        skill_content = f.read()

    # Create comprehensive prompt for Claude
    prompt = f"""You are updating the Tesla investor tracking dashboard.

Current date: {today}
Last update: {last_updated}

TASK: Research Tesla developments from {last_updated} to {today} and update the tracking data.

Follow the instructions in the skill documentation below, particularly the Multi-Layered Sentiment Analysis framework.

SKILL DOCUMENTATION:
{skill_content}

CURRENT DATA:
{json.dumps(data, indent=2)}

Instructions:
1. Search for Tesla news in these categories since {last_updated}:
   - AI Chip Production (AI5/AI6 at Samsung/TSMC)
   - Cybercab/Robotaxi Production & Fleet Size
   - FSD Country Approvals
   - Job Postings (Optimus-related)
   - Optimus Production
   - Production & Delivery Reports (if new quarter)

2. For each significant update found, apply the Multi-Layered Sentiment Analysis:
   - Extract objective metrics
   - Gather evidence (positive/negative signals)
   - Calculate reality assessment vs headline sentiment
   - Include confidence and rationale

3. Return ONLY a JSON object with this structure:
{{
  "has_updates": true/false,
  "new_weekly_summary": {{...}} or null,
  "metric_updates": {{...}} or null,
  "updated_date": "{today}"
}}

If no significant news found, return {{"has_updates": false}}.

IMPORTANT: Use the multi-layered sentiment analysis framework. Compare actual numbers to targets.
"""

    print("Calling Claude API for research and analysis...")

    try:
        # Note: This is a simplified version. In production, you'd want to use
        # web search tools or APIs to gather real data
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4000,
            temperature=0.3,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        response_text = message.content[0].text
        print(f"Claude response received ({len(response_text)} chars)")

        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if not json_match:
            print("WARNING: No JSON found in response")
            return False

        update_data = json.loads(json_match.group())

        if not update_data.get('has_updates'):
            print("No significant updates found.")
            data['lastUpdated'] = today
            with open('tesla-tracking-data.json', 'w') as f:
                json.dump(data, f, indent=2)
            update_html_dashboard(data)
            return True

        # Apply updates
        if update_data.get('new_weekly_summary'):
            data['weeklySummaries'].insert(0, update_data['new_weekly_summary'])
            print("✓ Added new weekly summary")

        if update_data.get('metric_updates'):
            # Update metrics
            for metric_key, metric_data in update_data['metric_updates'].items():
                if metric_key in data['metrics']:
                    data['metrics'][metric_key]['data'].extend(metric_data)
                    print(f"✓ Updated {metric_key} metrics")

        # Update lastUpdated
        data['lastUpdated'] = today

        # Save updated JSON
        with open('tesla-tracking-data.json', 'w') as f:
            json.dump(data, f, indent=2)

        print("✓ JSON data updated")

        # Sync HTML
        update_html_dashboard(data)

        return True

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Tesla Tracker Auto-Update")
    print("=" * 60)

    success = run_tesla_update()

    if success:
        print("\n✓ Update completed successfully")
    else:
        print("\n✗ Update failed or skipped")
        exit(1)
