#!/usr/bin/env python3
"""
URL deduplication cache manager

Tracks all URLs seen across research runs to avoid:
- Re-analyzing same articles
- Duplicate keyChanges
- Wasted LLM tokens

Usage:
    # Check if URL seen before
    python3 scripts/url_cache.py check "https://electrek.co/..."

    # Add URL to cache
    python3 scripts/url_cache.py add "https://electrek.co/..." "Cybercab Production" "Title"

    # List recent URLs
    python3 scripts/url_cache.py list --days 7

    # Stats
    python3 scripts/url_cache.py stats
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
from urllib.parse import urlparse


CACHE_FILE = Path('findings/url-cache.json')


def load_cache() -> dict:
    """Load URL cache"""
    if not CACHE_FILE.exists():
        return {
            'version': '1.0',
            'lastUpdated': datetime.now().strftime('%Y-%m-%d'),
            'urls': {},
            'stats': {
                'totalUrls': 0,
                'categoryCounts': {}
            }
        }

    with open(CACHE_FILE, 'r') as f:
        return json.load(f)


def save_cache(cache: dict):
    """Save URL cache"""
    cache['lastUpdated'] = datetime.now().strftime('%Y-%m-%d')
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)


def normalize_url(url: str) -> str:
    """
    Normalize URL for comparison
    - Remove query params (except for specific domains)
    - Remove trailing slashes
    - Lowercase domain
    """
    parsed = urlparse(url)

    # For most sites, ignore query params (they're often tracking/session IDs)
    # Exception: Keep query params for specific domains if needed
    if parsed.netloc in ['ir.tesla.com', 'robotaxitracker.com']:
        return url.rstrip('/')

    normalized = f"{parsed.scheme}://{parsed.netloc.lower()}{parsed.path.rstrip('/')}"
    return normalized


def check_url(url: str) -> Optional[Dict]:
    """Check if URL has been seen before"""
    cache = load_cache()
    normalized = normalize_url(url)

    if normalized in cache['urls']:
        return cache['urls'][normalized]

    return None


def add_url(url: str, category: str, title: str = ""):
    """Add URL to cache"""
    cache = load_cache()
    normalized = normalize_url(url)
    today = datetime.now().strftime('%Y-%m-%d')

    if normalized in cache['urls']:
        # Update lastSeen
        cache['urls'][normalized]['lastSeen'] = today
    else:
        # Add new entry
        cache['urls'][normalized] = {
            'originalUrl': url,
            'firstSeen': today,
            'lastSeen': today,
            'category': category,
            'title': title
        }

        # Update stats
        cache['stats']['totalUrls'] += 1
        if category not in cache['stats']['categoryCounts']:
            cache['stats']['categoryCounts'][category] = 0
        cache['stats']['categoryCounts'][category] += 1

    save_cache(cache)
    print(f"✓ Added to cache: {url[:80]}...")


def list_urls(days: int = 7):
    """List URLs seen in last N days"""
    cache = load_cache()
    cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    recent = []
    for url, data in cache['urls'].items():
        if data['lastSeen'] >= cutoff:
            recent.append((url, data))

    recent.sort(key=lambda x: x[1]['lastSeen'], reverse=True)

    print(f"\nURLs seen in last {days} days: {len(recent)}\n")
    for url, data in recent[:50]:  # Show max 50
        print(f"{data['lastSeen']} | {data['category'][:20]:20} | {url[:80]}")


def stats():
    """Show cache statistics"""
    cache = load_cache()

    print("\n" + "=" * 60)
    print("URL Cache Statistics")
    print("=" * 60)
    print(f"\nTotal URLs: {cache['stats']['totalUrls']}")
    print(f"Last Updated: {cache['lastUpdated']}")

    print("\nBy Category:")
    for category, count in sorted(cache['stats']['categoryCounts'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {category[:40]:40} {count:>5}")

    # Age distribution
    now = datetime.now()
    age_buckets = {'< 7 days': 0, '7-30 days': 0, '30-90 days': 0, '> 90 days': 0}

    for url, data in cache['urls'].items():
        last_seen = datetime.strptime(data['lastSeen'], '%Y-%m-%d')
        age = (now - last_seen).days

        if age < 7:
            age_buckets['< 7 days'] += 1
        elif age < 30:
            age_buckets['7-30 days'] += 1
        elif age < 90:
            age_buckets['30-90 days'] += 1
        else:
            age_buckets['> 90 days'] += 1

    print("\nBy Age (last seen):")
    for bucket, count in age_buckets.items():
        pct = (count / cache['stats']['totalUrls'] * 100) if cache['stats']['totalUrls'] > 0 else 0
        print(f"  {bucket:15} {count:>5} ({pct:>5.1f}%)")

    print("\n" + "=" * 60 + "\n")


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == 'check':
        if len(sys.argv) < 3:
            print("Usage: python3 scripts/url_cache.py check <url>")
            sys.exit(1)

        url = sys.argv[2]
        result = check_url(url)

        if result:
            print(f"✓ URL seen before:")
            print(f"  First seen: {result['firstSeen']}")
            print(f"  Last seen: {result['lastSeen']}")
            print(f"  Category: {result['category']}")
            print(f"  Title: {result.get('title', 'N/A')}")
            sys.exit(0)
        else:
            print(f"✗ URL not in cache")
            sys.exit(1)

    elif command == 'add':
        if len(sys.argv) < 4:
            print("Usage: python3 scripts/url_cache.py add <url> <category> [title]")
            sys.exit(1)

        url = sys.argv[2]
        category = sys.argv[3]
        title = sys.argv[4] if len(sys.argv) > 4 else ""

        add_url(url, category, title)

    elif command == 'list':
        days = 7
        if '--days' in sys.argv:
            days_idx = sys.argv.index('--days')
            days = int(sys.argv[days_idx + 1])

        list_urls(days)

    elif command == 'stats':
        stats()

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()
