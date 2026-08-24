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

# Allow running as scripts/spawn_researcher.py from repo root
sys.path.insert(0, str(Path(__file__).parent))
from paths import (  # noqa: E402
    TRACKING_DATA,
    RAW_DIR,
    ensure_research_dirs,
    research_config_path,
)
from url_cache import load_cache  # noqa: E402

# Canonical display names used in keyChanges.category (for hot-context matching)
CATEGORY_DISPLAY_NAMES = {
    "cybercab": "Cybercab Production",
    "fsd": "FSD Country Approvals",
    "optimus": "Optimus Production",
    "fsdv15": "FSD v15 Software",
    "productionDelivery": "Vehicle Production & Delivery",
    "aiChip": "AI Chip Production",
    "battery4680": "4680 Battery Cell Production",
    "terafab": "Terafab In-House Chip Manufacturing",
    "jobPostings": "Job Postings",
}

# Category configurations with ownership boundaries (cuts cross-researcher dups)
CATEGORIES = {
    "cybercab": {
        "categoryName": "Cybercab Production",
        "priority": "high",
        "sources": {
            "tier1": ["teslarati.com", "teslanorth.com", "teslaoracle.com"],
            "specialized": ["robotaxitracker.com"]
        },
        "keywords": ["Cybercab", "robotaxi", "fleet", "autonomous", "unsupervised"],
        "metrics": ["cybercab", "robotaxiFleet"],
        "ownership": {
            "owns": [
                "Cybercab vehicle production, staging, EPA/certification",
                "Robotaxi fleet size, city launches, geofence, ops quality",
                "Unsupervised ride service expansion (cities, vehicle counts)",
                "Owner-operated robotaxi / app fleet-management features",
            ],
            "doesNotOwn": [
                "Country FSD regulatory approvals → fsd",
                "FSD software version releases (v14.x/v15) → fsdv15",
                "NHTSA/NTSB crash investigations → fsd",
                "Optimus factory/robotics → optimus",
            ],
        },
    },
    "fsd": {
        "categoryName": "FSD Country Approvals",
        "priority": "high",
        "sources": {
            "tier1": ["teslarati.com", "teslanorth.com", "teslaoracle.com"]
        },
        "keywords": ["FSD", "approval", "country", "Europe", "regulatory"],
        "metrics": ["fsdApprovals"],
        "ownership": {
            "owns": [
                "Country/region regulatory approvals for FSD Supervised or unsupervised",
                "EU homologation, mutual recognition, KBA/RDW/DMV decisions",
                "NHTSA, NTSB, civil crash investigations and safety probes",
                "Pending applications (e.g. Italy under review) as regulatory status",
            ],
            "doesNotOwn": [
                "FSD software version OTA releases / changelogs → fsdv15",
                "Cumulative FSD miles as training-data/software milestone → fsdv15",
                "HW3/HW4 software capability ceilings → fsdv15",
                "Robotaxi city ops / fleet counts → cybercab",
            ],
        },
    },
    "optimus": {
        "categoryName": "Optimus Production",
        "priority": "high",
        "sources": {
            "tier1": ["optimusk.blog", "teslarati.com", "teslanorth.com"]
        },
        "keywords": ["Optimus", "humanoid", "robot", "Fremont", "Giga Texas"],
        "metrics": [],
        "ownership": {
            "owns": [
                "Optimus hardware design, production ramp, factory deployment",
                "Internal vs external sales timeline for humanoid robots",
                "Competitor humanoid context only when it directly contrasts Optimus",
            ],
            "doesNotOwn": [
                "Optimus job posting counts → jobPostings",
                "AI inference chips for robots → aiChip",
                "Vehicle production/delivery → productionDelivery",
            ],
        },
    },
    "fsdv15": {
        "categoryName": "FSD v15 Software",
        "priority": "high",
        "sources": {
            "tier1": ["teslarati.com", "teslanorth.com", "notateslaapp.com"]
        },
        "keywords": ["FSD v15", "FSD 15", "supervised", "end-to-end"],
        "metrics": [],
        "ownership": {
            "owns": [
                "FSD software version releases and OTA changelogs (v14.x, v15)",
                "HW3/HW4 software capability ceilings and Lite builds",
                "Cumulative FSD miles / training-data milestones",
                "Architecture roadmap (end-to-end, Grok→planning, parameter scale)",
                "v15 timeline as software ship date (not country approval)",
            ],
            "doesNotOwn": [
                "Country approvals / EU homologation → fsd",
                "NHTSA/NTSB crash reports → fsd",
                "Robotaxi fleet ops / city launches → cybercab",
            ],
        },
    },
    "productionDelivery": {
        "categoryName": "Vehicle Production & Delivery",
        "priority": "critical",
        "sources": {
            "tier1": ["ir.tesla.com"],
            "tier2": ["teslarati.com", "teslanorth.com"]
        },
        "keywords": ["quarterly", "production", "delivery", "Q1", "Q2", "Q3", "Q4"],
        "metrics": ["quarterlyData"],
        "ownership": {
            "owns": [
                "Quarterly production and delivery numbers",
                "IR earnings consensus, auto revenue/margin guidance tied to volume",
                "New vehicle market entries (country sales launches)",
                "Semi / vehicle product pilots as volume-adjacent auto news",
            ],
            "doesNotOwn": [
                "Cybercab unit production → cybercab",
                "4680 cell manufacturing → battery4680",
                "Optimus unit production → optimus",
            ],
        },
    },
    "aiChip": {
        "categoryName": "AI Chip Production",
        "priority": "medium",
        "sources": {
            "tier1": ["teslarati.com", "teslanorth.com", "teslaoracle.com"]
        },
        "keywords": ["AI5", "AI6", "Samsung", "TSMC", "2nm", "Dojo"],
        "metrics": [],
        "ownership": {
            "owns": [
                "AI5/AI6/AI4 chip design and foundry process tape-outs",
                "Samsung/TSMC wafer deals, node (2nm), yields for Tesla inference chips",
                "Dojo training-chip architecture and program status",
                "Chip volume/sample timelines for vehicle AI computers",
            ],
            "doesNotOwn": [
                "Terafab construction, tax deals, school boards, Abbott politics → terafab",
                "Site selection / JETI abatements → terafab",
                "FSD software versions → fsdv15",
            ],
        },
    },
    "battery4680": {
        "categoryName": "4680 Battery Cell Production",
        "priority": "medium",
        "sources": {
            "tier1": ["teslarati.com", "teslanorth.com", "basenor.com"]
        },
        "keywords": ["4680", "battery cell", "GWh", "yield", "dry electrode"],
        "metrics": [],
        "ownership": {
            "owns": [
                "4680 cell production, yield, dry electrode, GWh capacity",
                "Berlin/Texas cell lines and Cell Giga Challenge",
            ],
            "doesNotOwn": [
                "Vehicle delivery volumes → productionDelivery",
                "Energy storage deployment GWh (Megapack) → productionDelivery if quarterly",
            ],
        },
    },
    "terafab": {
        "categoryName": "Terafab In-House Chip Manufacturing",
        "priority": "medium",
        "sources": {
            "tier1": ["teslarati.com", "teslanorth.com"]
        },
        "keywords": ["Terafab", "North Campus", "chip fab", "Taylor Texas"],
        "metrics": [],
        "ownership": {
            "owns": [
                "Terafab / North Campus construction and permits",
                "JETI tax abatements, school board votes, Abbott decisions",
                "Fab site politics and local opposition (water, identity)",
            ],
            "doesNotOwn": [
                "AI5/AI6 design or foundry process tape-out → aiChip",
                "Chip performance specs and volume silicon dates → aiChip",
                "Samsung Taylor wafer deals for AI5 (chip story) → aiChip",
            ],
        },
    },
    "jobPostings": {
        "categoryName": "Job Postings",
        "priority": "low",
        "sources": {
            "tier1": ["optimusk.blog", "linkedin.com"]
        },
        "keywords": ["Optimus", "hiring", "job posting", "Tesla careers"],
        "metrics": ["jobPostings"],
        "ownership": {
            "owns": [
                "AI/robotics/FSD/Optimus job posting counts and hiring signals",
                "LinkedIn/careers headcount trends for AI orgs",
            ],
            "doesNotOwn": [
                "Service-center / retail / sales hiring → skip (out of scope)",
                "Factory conversion narratives without hiring metrics → optimus",
            ],
        },
    },
}


# Dedup only needs identity fields — not last week's essays.
SLIM_KEY_CHANGE_FIELDS = ("title", "date", "category", "source", "status")
NOTE_MAX = 240
# Older cache entries used a shorter Terafab label.
CATEGORY_CACHE_ALIASES = {
    "terafab": ("Terafab Manufacturing",),
}


def _normalize_label(s: str) -> str:
    return s.lower().replace(" ", "").replace("&", "").replace("-", "").replace("/", "")


def slim_key_change(kc):
    """Keep title/date/category/source/status only (enough to skip last week's stories)."""
    return {k: kc[k] for k in SLIM_KEY_CHANGE_FIELDS if kc.get(k) not in (None, "")}


def slim_metric_point(point, note_max=NOTE_MAX):
    """Keep date/count/note/source; truncate long notes."""
    if not point:
        return {}
    out = {}
    for k in ("date", "count", "note", "source"):
        if point.get(k) is not None:
            out[k] = point[k]
    note = out.get("note")
    if isinstance(note, str) and len(note) > note_max:
        out["note"] = note[: note_max - 3] + "..."
    return out


def _category_label_aliases(category_key):
    display = CATEGORY_DISPLAY_NAMES.get(category_key, category_key)
    labels = {display, category_key, *CATEGORY_CACHE_ALIASES.get(category_key, ())}
    return {_normalize_label(x) for x in labels}


def _add_url(url, ordered: list, seen: set) -> None:
    if url and url not in seen:
        seen.add(url)
        ordered.append(url)


def all_seen_urls(cache_urls=None):
    """Flat URL list (normalized key + originalUrl) so agents skip the 64KB cache file."""
    if cache_urls is None:
        cache_urls = load_cache().get("urls", {})
    ordered = []
    seen = set()
    for key, meta in cache_urls.items():
        _add_url(key, ordered, seen)
        if isinstance(meta, dict):
            _add_url(meta.get("originalUrl"), ordered, seen)
    return ordered


def urls_for_category(category_key, cache_urls=None, extra_urls=None):
    """URLs already filed under this category, plus any extra (e.g. last week's sources)."""
    if cache_urls is None:
        cache_urls = load_cache().get("urls", {})
    aliases = _category_label_aliases(category_key)
    ordered = []
    seen = set()
    for key, meta in cache_urls.items():
        cat = meta.get("category") if isinstance(meta, dict) else None
        if not cat or _normalize_label(cat) not in aliases:
            continue
        _add_url(key, ordered, seen)
        if isinstance(meta, dict):
            _add_url(meta.get("originalUrl"), ordered, seen)
    for url in extra_urls or []:
        _add_url(url, ordered, seen)
    return ordered


def load_hot_context(category_key, data=None, cache_urls=None):
    """Extract slim hot context for a category from main data file."""
    if data is None:
        with open(TRACKING_DATA) as f:
            data = json.load(f)

    display_name = CATEGORY_DISPLAY_NAMES.get(category_key, category_key)
    cat_data = data["categories"].get(category_key, {})

    hot_context = {
        "criticalNews": cat_data.get("criticalNews", ""),
        "recentKeyChanges": [],
        "seenUrls": [],
    }

    matched = []
    if data["weeklySummaries"]:
        latest_week = data["weeklySummaries"][0]
        want = {
            _normalize_label(display_name),
            _normalize_label(category_key),
        }
        for kc in latest_week.get("keyChanges", []):
            if _normalize_label(kc.get("category", "")) in want:
                matched.append(kc)
        hot_context["recentKeyChanges"] = [slim_key_change(kc) for kc in matched]

    extra_urls = [kc.get("source") for kc in hot_context["recentKeyChanges"]]
    hot_context["seenUrls"] = urls_for_category(
        category_key, cache_urls=cache_urls, extra_urls=extra_urls
    )

    if category_key == "cybercab" and "cybercab" in data["metrics"]:
        if data["metrics"]["cybercab"].get("data"):
            hot_context["latestMetric"] = slim_metric_point(
                data["metrics"]["cybercab"]["data"][-1]
            )
        if data["metrics"]["robotaxiFleet"].get("data"):
            hot_context["latestFleet"] = slim_metric_point(
                data["metrics"]["robotaxiFleet"]["data"][-1]
            )
    elif category_key == "jobPostings" and "jobPostings" in data["metrics"]:
        if data["metrics"]["jobPostings"].get("data"):
            hot_context["latestMetric"] = slim_metric_point(
                data["metrics"]["jobPostings"]["data"][-1]
            )
    elif category_key == "fsd" and "fsdApprovals" in data["metrics"]:
        countries = data["metrics"]["fsdApprovals"].get("countries", [])
        if countries:
            latest = countries[-1] or {}
            hot_context["latestMetric"] = {
                "totalCountries": len([c for c in countries if c.get("status") == "active"]),
                "latestCountry": {
                    k: latest[k]
                    for k in ("name", "status", "date")
                    if latest.get(k) not in (None, "")
                },
            }

    return hot_context


def create_config(category_key, date_from, date_to, week_of, data=None, cache_urls=None):
    """Create research config for a category."""
    if category_key not in CATEGORIES:
        raise ValueError(f"Unknown category: {category_key}")

    config = {
        "categoryKey": category_key,
        "dateFrom": date_from,
        "dateTo": date_to,
        "weekOf": week_of,
        "outputPath": str(RAW_DIR / f"findings-{category_key}.json"),
        "hotContext": load_hot_context(category_key, data=data, cache_urls=cache_urls),
        **CATEGORIES[category_key]
    }

    return config


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/spawn_researcher.py <category>")
        print("       python3 scripts/spawn_researcher.py --all")
        print(f"\nAvailable categories: {', '.join(CATEGORIES.keys())}")
        sys.exit(1)

    ensure_research_dirs()

    with open(TRACKING_DATA) as f:
        data = json.load(f)
    cache_urls = load_cache().get("urls", {})

    date_from = data["lastUpdated"]
    date_to = datetime.now().strftime("%Y-%m-%d")

    now = datetime.now()
    monday = now - timedelta(days=now.weekday())
    week_of = monday.strftime("%Y-%m-%d")

    if sys.argv[1] == "--all":
        print(f"Creating configs for all 9 categories...")
        print(f"Research period: {date_from} → {date_to}")
        print(f"Week of: {week_of}\n")

        for category_key in CATEGORIES.keys():
            config = create_config(
                category_key, date_from, date_to, week_of,
                data=data, cache_urls=cache_urls,
            )
            config_path = research_config_path(category_key)
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)

            priority = config["priority"]
            model = "sonnet" if priority in ["critical", "high"] else "haiku"
            seen_n = len(config["hotContext"].get("seenUrls", []))
            print(
                f"✓ {category_key:20} priority={priority:8} model={model:6} "
                f"{config_path.stat().st_size:5}B seenUrls={seen_n:2} "
                f"→ {config_path.relative_to(config_path.parents[1])}"
            )

        print(f"\n✅ Created 9 config files in research/configs/")
        print(f"   Researchers write to research/raw/findings-{{category}}.json")
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

        config = create_config(
            category_key, date_from, date_to, week_of,
            data=data, cache_urls=cache_urls,
        )
        config_path = research_config_path(category_key)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"✅ Created research config: {config_path}")
        print(f"\nConfig summary:")
        print(f"  Category: {config['categoryName']}")
        print(f"  Priority: {config['priority']}")
        print(f"  Period: {date_from} → {date_to}")
        print(f"  Week of: {week_of}")
        print(f"  Output: {config['outputPath']}")
        print(f"  Sources: {', '.join(config['sources']['tier1'])}")
        print(f"  Keywords: {', '.join(config['keywords'][:3])}...")
        print(f"  Last-week stories: {len(config['hotContext']['recentKeyChanges'])} (slim)")
        print(f"  seenUrls: {len(config['hotContext']['seenUrls'])}")
        owns = config.get("ownership", {}).get("owns", [])
        if owns:
            print(f"  Owns: {owns[0][:60]}...")
        print(f"\nNext: Spawn tesla-researcher agent with this config")


if __name__ == "__main__":
    main()
