#!/usr/bin/env python3
"""
Spawn a tesla-researcher agent for one category.

Usage:
    python3 scripts/spawn_researcher.py cybercab
    python3 scripts/spawn_researcher.py --all  # spawn all 9 in parallel
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Category configurations
CATEGORIES = {
    "cybercab": {
        "categoryName": "Cybercab Production",
        "priority": "high",
        "sources": {
            "tier1": ["teslarati.com", "teslanorth.com", "teslaoracle.com"],
            "specialized": ["robotaxitracker.com"]
        },
        "keywords": ["Cybercab", "robotaxi", "fleet", "autonomous", "unsupervised"],
        "metrics": ["cybercab", "robotaxiFleet"]
    },
    "fsd": {
        "categoryName": "FSD Country Approvals",
        "priority": "high",
        "sources": {
            "tier1": ["teslarati.com", "teslanorth.com", "teslaoracle.com"]
        },
        "keywords": ["FSD", "approval", "country", "Europe", "regulatory"],
        "metrics": ["fsdApprovals"]
    },
    "optimus": {
        "categoryName": "Optimus Production",
        "priority": "high",
        "sources": {
            "tier1": ["optimusk.blog", "teslarati.com", "teslanorth.com"]
        },
        "keywords": ["Optimus", "humanoid", "robot", "Fremont", "Giga Texas"],
        "metrics": []
    },
    "fsdv15": {
        "categoryName": "FSD v15 Software",
        "priority": "high",
        "sources": {
            "tier1": ["teslarati.com", "teslanorth.com", "notateslaapp.com"]
        },
        "keywords": ["FSD v15", "FSD 15", "supervised", "end-to-end"],
        "metrics": []
    },
    "productionDelivery": {
        "categoryName": "Vehicle Production & Delivery",
        "priority": "critical",
        "sources": {
            "tier1": ["ir.tesla.com"],
            "tier2": ["teslarati.com", "teslanorth.com"]
        },
        "keywords": ["quarterly", "production", "delivery", "Q1", "Q2", "Q3", "Q4"],
        "metrics": ["quarterlyData"]
    },
    "aiChip": {
        "categoryName": "AI Chip Production",
        "priority": "medium",
        "sources": {
            "tier1": ["teslarati.com", "teslanorth.com", "teslaoracle.com"]
        },
        "keywords": ["AI5", "AI6", "Samsung", "TSMC", "2nm", "Dojo"],
        "metrics": []
    },
    "battery4680": {
        "categoryName": "4680 Battery Cell Production",
        "priority": "medium",
        "sources": {
            "tier1": ["teslarati.com", "teslanorth.com", "basenor.com"]
        },
        "keywords": ["4680", "battery cell", "GWh", "yield", "dry electrode"],
        "metrics": []
    },
    "terafab": {
        "categoryName": "Terafab Manufacturing",
        "priority": "medium",
        "sources": {
            "tier1": ["teslarati.com", "teslanorth.com"]
        },
        "keywords": ["Terafab", "North Campus", "chip fab", "Taylor Texas"],
        "metrics": []
    },
    "jobPostings": {
        "categoryName": "Job Postings",
        "priority": "low",
        "sources": {
            "tier1": ["optimusk.blog", "linkedin.com"]
        },
        "keywords": ["Optimus", "hiring", "job posting", "Tesla careers"],
        "metrics": ["jobPostings"]
    }
}

def load_hot_context(category_key):
    """Extract hot context for a category from main data file."""
    data_path = Path(__file__).parent.parent / "tesla-tracking-data.json"
    with open(data_path) as f:
        data = json.load(f)

    hot_context = {
        "criticalNews": data["categories"].get(category_key, {}).get("criticalNews", ""),
        "recentKeyChanges": []
    }

    # Get recent keyChanges for this category
    if data["weeklySummaries"]:
        latest_week = data["weeklySummaries"][0]
        hot_context["recentKeyChanges"] = [
            kc for kc in latest_week.get("keyChanges", [])
            if kc.get("category", "").lower().replace(" ", "").replace("&", "").startswith(category_key.lower())
        ][:3]  # Last 3

    # Get latest metrics
    if category_key == "cybercab" and "cybercab" in data["metrics"]:
        if data["metrics"]["cybercab"]["data"]:
            hot_context["latestMetric"] = data["metrics"]["cybercab"]["data"][-1]
        if data["metrics"]["robotaxiFleet"]["data"]:
            hot_context["latestFleet"] = data["metrics"]["robotaxiFleet"]["data"][-1]
    elif category_key == "jobPostings" and "jobPostings" in data["metrics"]:
        if data["metrics"]["jobPostings"]["data"]:
            hot_context["latestMetric"] = data["metrics"]["jobPostings"]["data"][-1]
    elif category_key == "fsd" and "fsdApprovals" in data["metrics"]:
        if data["metrics"]["fsdApprovals"]["data"]:
            hot_context["latestMetric"] = data["metrics"]["fsdApprovals"]["data"][-1]

    return hot_context

def create_config(category_key, date_from, date_to, week_of):
    """Create research config for a category."""
    if category_key not in CATEGORIES:
        raise ValueError(f"Unknown category: {category_key}")

    config = {
        "categoryKey": category_key,
        "dateFrom": date_from,
        "dateTo": date_to,
        "weekOf": week_of,
        "hotContext": load_hot_context(category_key),
        **CATEGORIES[category_key]
    }

    return config

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/spawn_researcher.py <category>")
        print("       python3 scripts/spawn_researcher.py --all")
        print(f"\nAvailable categories: {', '.join(CATEGORIES.keys())}")
        sys.exit(1)

    # Load main data to get date range
    data_path = Path(__file__).parent.parent / "tesla-tracking-data.json"
    with open(data_path) as f:
        data = json.load(f)

    date_from = data["lastUpdated"]
    date_to = datetime.now().strftime("%Y-%m-%d")

    # Calculate Monday of current week
    now = datetime.now()
    monday = now - timedelta(days=now.weekday())
    week_of = monday.strftime("%Y-%m-%d")

    if sys.argv[1] == "--all":
        # Create configs for all categories
        print(f"Creating configs for all 9 categories...")
        print(f"Research period: {date_from} → {date_to}")
        print(f"Week of: {week_of}\n")

        for category_key in CATEGORIES.keys():
            config = create_config(category_key, date_from, date_to, week_of)

            # Write config file
            config_path = Path(__file__).parent.parent / f"research-config-{category_key}.json"
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)

            priority = config["priority"]
            model = "sonnet" if priority in ["critical", "high"] else "haiku"

            print(f"✓ {category_key:20} priority={priority:8} model={model:6} → research-config-{category_key}.json")

        print(f"\n✅ Created 9 config files")
        print(f"\nNext steps:")
        print(f"1. Spawn researchers in parallel (via Task tool or manually)")
        print(f"2. Wait for all to complete")
        print(f"3. Run tesla-curator to merge findings")

    else:
        category_key = sys.argv[1]

        if category_key not in CATEGORIES:
            print(f"Error: Unknown category '{category_key}'")
            print(f"Available: {', '.join(CATEGORIES.keys())}")
            sys.exit(1)

        config = create_config(category_key, date_from, date_to, week_of)

        # Write config file
        config_path = Path(__file__).parent.parent / f"research-config-{category_key}.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"✅ Created research config: research-config-{category_key}.json")
        print(f"\nConfig summary:")
        print(f"  Category: {config['categoryName']}")
        print(f"  Priority: {config['priority']}")
        print(f"  Period: {date_from} → {date_to}")
        print(f"  Week of: {week_of}")
        print(f"  Sources: {', '.join(config['sources']['tier1'])}")
        print(f"  Keywords: {', '.join(config['keywords'][:3])}...")
        print(f"\nNext: Spawn tesla-researcher agent with this config")

if __name__ == "__main__":
    main()
