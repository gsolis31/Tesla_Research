#!/usr/bin/env python3
"""
Parallel category research coordinator

Splits research across categories, runs them in parallel (or sequentially),
then merges findings into a single file.

Usage:
    # Research all categories in parallel
    python3 scripts/parallel_research.py --date 2026-07-08 --parallel

    # Research specific categories only
    python3 scripts/parallel_research.py --date 2026-07-08 --categories "Cybercab Production,FSD Country Approvals"

    # Sequential (for testing)
    python3 scripts/parallel_research.py --date 2026-07-08

Architecture:
    1. Create category-specific research prompts
    2. Launch parallel agents (or sequential for safety)
    3. Each agent writes findings-{category}.json
    4. Merge all category findings → findings/YYYY-MM-DD.json
    5. Run merge_findings.py
"""

import json
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional


# Category research configuration
CATEGORIES = {
    'AI Chip Production': {
        'key': 'aiChip',
        'priority': 'medium',
        'sources': ['teslarati.com', 'teslanorth.com', 'teslaoracle.com'],
        'keywords': ['AI5', 'AI6', 'Samsung', 'TSMC', '2nm', 'wafer', 'Dojo']
    },
    '4680 Battery Cell Production': {
        'key': 'battery4680',
        'priority': 'medium',
        'sources': ['teslarati.com', 'teslanorth.com'],
        'keywords': ['4680', 'battery', 'cell', 'GWh', 'dry coating', 'yield']
    },
    'Cybercab Production': {
        'key': 'cybercab',
        'priority': 'high',
        'sources': ['teslarati.com', 'robotaxitracker.com', 'electrek.co'],
        'keywords': ['Cybercab', 'robotaxi', 'fleet', 'autonomous', 'FSD']
    },
    'FSD Country Approvals': {
        'key': 'fsd',
        'priority': 'high',
        'sources': ['teslarati.com', 'teslanorth.com', 'teslaoracle.com'],
        'keywords': ['FSD', 'approval', 'country', 'regulatory', 'subscription']
    },
    'Job Postings': {
        'key': 'jobPostings',
        'priority': 'low',
        'sources': ['optimusk.blog', 'teslarati.com'],
        'keywords': ['Optimus', 'hiring', 'job', 'posting', 'roles']
    },
    'Optimus Production': {
        'key': 'optimus',
        'priority': 'high',
        'sources': ['optimusk.blog', 'teslarati.com', 'teslanorth.com'],
        'keywords': ['Optimus', 'humanoid', 'robot', 'production', 'Fremont', 'Texas']
    },
    'Vehicle Production & Delivery': {
        'key': 'productionDelivery',
        'priority': 'critical',
        'sources': ['ir.tesla.com/press'],
        'keywords': ['quarterly', 'production', 'delivery', 'Q1', 'Q2', 'Q3', 'Q4']
    },
    'Terafab In-House Chip Manufacturing': {
        'key': 'terafab',
        'priority': 'medium',
        'sources': ['teslarati.com', 'teslanorth.com'],
        'keywords': ['Terafab', 'chip', 'fab', 'manufacturing', 'North Campus']
    },
    'FSD v15 Software': {
        'key': 'fsdv15',
        'priority': 'high',
        'sources': ['teslarati.com', 'teslanorth.com', 'electrek.co'],
        'keywords': ['FSD v15', 'rewrite', 'end-to-end', 'neural net']
    }
}


def get_monday_of_week(date_str: str) -> str:
    """Get Monday of the week for a given date"""
    date = datetime.strptime(date_str, '%Y-%m-%d')
    monday = date - timedelta(days=date.weekday())
    return monday.strftime('%Y-%m-%d')


def load_hot_context(category_key: str) -> Dict:
    """
    Load hot context for a category (last updates only)
    Returns: {lastUpdate, latestMetric, criticalNews}
    """
    data = json.load(open('tesla-tracking-data.json'))

    context = {
        'lastUpdated': data['lastUpdated'],
        'categoryKey': category_key
    }

    # Get category-specific context
    if category_key == 'productionDelivery':
        category = data['categories']['productionDelivery']
        context['latestQuarter'] = category['quarterlyData'][-1] if category['quarterlyData'] else None
        context['criticalNews'] = category['criticalNews']
    else:
        if category_key in data['categories']:
            category = data['categories'][category_key]
            context['criticalNews'] = category.get('criticalNews', '')
            context['latestUpdate'] = category.get('latestUpdate', '')

    # Get latest metric if exists
    metric_map = {
        'cybercab': 'cybercab',
        'jobPostings': 'jobPostings',
    }

    if category_key in metric_map:
        metric_name = metric_map[category_key]
        if metric_name in data['metrics'] and data['metrics'][metric_name]['data']:
            context['latestMetric'] = data['metrics'][metric_name]['data'][-1]

    # Special handling for robotaxi
    if category_key == 'cybercab' and 'robotaxiFleet' in data['metrics']:
        context['latestFleet'] = data['metrics']['robotaxiFleet']['data'][-1]

    # Get last week's keyChanges to avoid duplicates
    context['recentKeyChanges'] = []
    if data['weeklySummaries']:
        last_week = data['weeklySummaries'][0]
        context['recentKeyChanges'] = [
            kc for kc in last_week.get('keyChanges', [])
            if kc.get('category') == category_key or
               (category_key == 'cybercab' and kc.get('category') in ['Cybercab Production', 'Robotaxi'])
        ]

    return context


def create_research_prompt(category_name: str, category_config: Dict, date: str, context: Dict) -> str:
    """
    Create a focused research prompt for a single category
    """
    last_updated = context.get('lastUpdated', '2026-07-01')
    sources = ', '.join(category_config['sources'])
    keywords = ', '.join(category_config['keywords'])

    prompt = f"""Research Task: {category_name}

**Research Period**: {last_updated} → {date}

**Context**:
- Last updated: {last_updated}
- Critical news: {context.get('criticalNews', 'N/A')[:200]}
- Latest metric: {json.dumps(context.get('latestMetric', {}), indent=2) if context.get('latestMetric') else 'N/A'}

**Recent keyChanges** (avoid duplicates):
{json.dumps(context.get('recentKeyChanges', []), indent=2)[:500]}

**Your Task**:
1. Search these sources: {sources}
2. Focus on these keywords: {keywords}
3. Find NEW developments since {last_updated}
4. Check URL cache before processing each URL:
   ```bash
   python3 scripts/url_cache.py check "<url>"
   ```
5. Skip URLs already seen (exit code 0)

**Output Format** (findings-{category_config['key']}.json):
{{
  "category": "{category_name}",
  "categoryKey": "{category_config['key']}",
  "keyChanges": [
    {{
      "status": "positive|negative|neutral",
      "sentiment": {{
        "headline": "...",
        "reality": "...",
        "confidence": "high|medium|low",
        "rationale": "..."
      }},
      "evidence": {{
        "positive_signals": ["..."],
        "negative_signals": ["..."],
        "key_metrics": {{
          "actual": "...",
          "target": "...",
          "trajectory": "..."
        }}
      }},
      "category": "{category_name}",
      "title": "...",
      "description": "...",
      "source": "https://..."
    }}
  ],
  "metricUpdate": {{
    "date": "{date}",
    "count": 0,
    "note": "..."
  }},
  "categoryUpdate": {{
    "criticalNews": "...",
    "newKeyPoint": "...",
    "newTimelineEvent": {{
      "date": "YYYY-MM-DD",
      "event": "..."
    }}
  }},
  "urlsSeen": ["https://...", "https://..."]
}}

**Important**:
- Only include NEW developments (check recentKeyChanges above)
- If no news found, return empty keyChanges array
- Use multi-source verification (check 2-3 Tier 1 sources)
- Validate all URLs are real and accessible

Write the output to: findings-{category_config['key']}.json
"""

    return prompt


def research_category_sequential(category_name: str, category_config: Dict, date: str) -> Optional[Path]:
    """
    Research a single category (sequential/manual mode)
    Returns path to findings file or None if skipped
    """
    print(f"\n{'=' * 70}")
    print(f"Researching: {category_name}")
    print(f"{'=' * 70}")

    # Load hot context
    context = load_hot_context(category_config['key'])

    # Create research prompt
    prompt = create_research_prompt(category_name, category_config, date, context)

    # Save prompt for manual execution
    prompt_file = Path(f"findings-{category_config['key']}-prompt.txt")
    with open(prompt_file, 'w') as f:
        f.write(prompt)

    print(f"\n📝 Research prompt saved to: {prompt_file}")
    print(f"📊 Hot context size: ~{len(json.dumps(context))} bytes")
    print(f"\nManual execution:")
    print(f"1. Read the prompt in {prompt_file}")
    print(f"2. Execute research using WebSearch")
    print(f"3. Write findings to findings-{category_config['key']}.json")

    findings_file = Path(f"findings-{category_config['key']}.json")

    # Check if findings already exist
    if findings_file.exists():
        print(f"✓ Found existing findings: {findings_file}")
        return findings_file

    print(f"⏳ Waiting for findings file to be created...")
    print(f"   (Create {findings_file} when research is complete)")

    return None


def merge_category_findings(date: str, category_findings: List[Path]) -> Path:
    """
    Merge all category-specific findings into a single findings/YYYY-MM-DD.json file
    """
    print(f"\n{'=' * 70}")
    print(f"Merging {len(category_findings)} category findings")
    print(f"{'=' * 70}\n")

    week_of = get_monday_of_week(date)

    merged = {
        'date': date,
        'weekOf': week_of,
        'findings': {
            'keyChanges': [],
            'trends': [],
            'metrics': {},
            'quarterlyData': [],
            'categoryUpdates': {}
        },
        'metadata': {
            'sourcesSearched': set(),
            'urlsSeen': [],
            'researchDuration': 'parallel',
            'categoriesResearched': []
        }
    }

    for findings_path in category_findings:
        try:
            with open(findings_path, 'r') as f:
                category_findings_data = json.load(f)

            category_key = category_findings_data.get('categoryKey', 'unknown')
            print(f"✓ Merging {category_key} ({len(category_findings_data.get('keyChanges', []))} keyChanges)")

            # Merge keyChanges
            merged['findings']['keyChanges'].extend(category_findings_data.get('keyChanges', []))

            # Merge metric update
            if 'metricUpdate' in category_findings_data and category_findings_data['metricUpdate']:
                metric_map = {
                    'cybercab': 'cybercab',
                    'jobPostings': 'jobPostings'
                }

                if category_key in metric_map:
                    metric_name = metric_map[category_key]
                    if metric_name not in merged['findings']['metrics']:
                        merged['findings']['metrics'][metric_name] = []
                    merged['findings']['metrics'][metric_name].append(category_findings_data['metricUpdate'])

            # Handle robotaxiFleet special case
            if category_key == 'cybercab' and 'fleetUpdate' in category_findings_data:
                if 'robotaxiFleet' not in merged['findings']['metrics']:
                    merged['findings']['metrics']['robotaxiFleet'] = []
                merged['findings']['metrics']['robotaxiFleet'].append(category_findings_data['fleetUpdate'])

            # Merge category updates
            if 'categoryUpdate' in category_findings_data and category_findings_data['categoryUpdate']:
                merged['findings']['categoryUpdates'][category_key] = category_findings_data['categoryUpdate']

            # Merge quarterly data (for productionDelivery)
            if 'quarterlyData' in category_findings_data:
                merged['findings']['quarterlyData'].extend(category_findings_data.get('quarterlyData', []))

            # Track URLs
            merged['metadata']['urlsSeen'].extend(category_findings_data.get('urlsSeen', []))
            merged['metadata']['categoriesResearched'].append(category_key)

        except Exception as e:
            print(f"✗ Error merging {findings_path}: {e}")

    # Convert sets to lists for JSON
    merged['metadata']['sourcesSearched'] = list(merged['metadata']['sourcesSearched'])
    merged['metadata']['urlsSeen'] = list(set(merged['metadata']['urlsSeen']))  # Deduplicate

    # Save merged findings
    output_path = Path(f'findings/{date}.json')
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(merged, f, indent=2)

    print(f"\n✓ Merged findings saved to: {output_path}")
    print(f"  - {len(merged['findings']['keyChanges'])} total keyChanges")
    print(f"  - {len(merged['metadata']['urlsSeen'])} URLs seen")
    print(f"  - {len(merged['metadata']['categoriesResearched'])} categories researched")

    return output_path


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Parallel category research coordinator')
    parser.add_argument('--date', default=datetime.now().strftime('%Y-%m-%d'),
                        help='Research date (default: today)')
    parser.add_argument('--categories', help='Comma-separated category names (default: all)')
    parser.add_argument('--parallel', action='store_true',
                        help='Run in parallel (requires Task tool support)')
    parser.add_argument('--merge-only', action='store_true',
                        help='Only merge existing category findings (skip research)')

    args = parser.parse_args()

    print("=" * 70)
    print("Tesla Parallel Research Coordinator")
    print("=" * 70)
    print(f"\nDate: {args.date}")
    print(f"Mode: {'Parallel' if args.parallel else 'Sequential'}")

    # Determine which categories to research
    if args.categories:
        selected_categories = [c.strip() for c in args.categories.split(',')]
        categories_to_research = {
            name: config for name, config in CATEGORIES.items()
            if name in selected_categories
        }
    else:
        categories_to_research = CATEGORIES

    print(f"Categories: {', '.join(categories_to_research.keys())}\n")

    # Research phase
    category_findings = []

    if not args.merge_only:
        if args.parallel:
            print("⚠ Parallel mode requires Task tool with subagents")
            print("   This is a placeholder - implement with Claude Code Task tool")
            print("   For now, running sequentially...\n")

        for category_name, category_config in categories_to_research.items():
            result = research_category_sequential(category_name, category_config, args.date)
            if result:
                category_findings.append(result)

    else:
        # Find existing category findings
        for category_name, category_config in categories_to_research.items():
            findings_file = Path(f"findings-{category_config['key']}.json")
            if findings_file.exists():
                category_findings.append(findings_file)
                print(f"✓ Found {findings_file}")

    # Merge phase
    if category_findings:
        merged_path = merge_category_findings(args.date, category_findings)

        print(f"\n{'=' * 70}")
        print("Next Steps")
        print(f"{'=' * 70}\n")
        print(f"1. Review merged findings: {merged_path}")
        print(f"2. Run merge: python3 scripts/merge_findings.py {merged_path}")
        print(f"3. Update URL cache")
        print(f"4. Build and deploy")

    else:
        print("\n⚠ No category findings found. Research categories first.")


if __name__ == '__main__':
    main()
