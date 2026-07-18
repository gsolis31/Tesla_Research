#!/usr/bin/env python3
"""
URL deduplication cache manager

Tracks all URLs seen across research runs to avoid:
- Re-analyzing same articles
- Duplicate keyChanges
- Wasted LLM tokens

Only canonical article URLs should be cached. Search pages, RSS feeds,
homepages, and careers listings are rejected by default.

Usage:
    # Check if URL seen before
    python3 scripts/url_cache.py check "https://electrek.co/..."

    # Add URL to cache (rejects non-canonical unless --force)
    python3 scripts/url_cache.py add "https://electrek.co/..." "Cybercab Production" "Title"

    # List recent URLs
    python3 scripts/url_cache.py list --days 7

    # Stats
    python3 scripts/url_cache.py stats

Prefer bulk update from findings:
    python3 scripts/update_url_cache.py findings/YYYY-MM-DD.json
    python3 scripts/update_url_cache.py --prune
"""

import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict
from urllib.parse import urlparse

CACHE_FILE = Path('findings/url-cache.json')

# Paths that are research noise, not article sources
_NOISE_PATH_PATTERNS = [
    re.compile(r'/feed/?$', re.I),
    re.compile(r'/rss/?$', re.I),
    re.compile(r'/feed/rss', re.I),
    re.compile(r'/search/?$', re.I),
    re.compile(r'/search/', re.I),
    re.compile(r'/careers/search', re.I),
    re.compile(r'/jobs/search', re.I),
    re.compile(r'^/?$', re.I),  # bare homepage
]

_NOISE_HOST_PATTERNS = [
    re.compile(r'(^|\.)news\.google\.com$', re.I),
    re.compile(r'(^|\.)google\.[a-z.]+$', re.I),
    re.compile(r'(^|\.)bing\.com$', re.I),
]

_NOISE_QUERY_KEYS = {'s', 'q', 'query', 'keywords'}

_SECTION_ROOTS = {
    'blog', 'news', 'newsroom', 'press', 'category', 'tag', 'tags',
    'author', 'page', 'videos', 'about', 'search'
}


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


def non_canonical_reason(url: str) -> Optional[str]:
    """
    Return a short reason if URL is not a cacheable article source, else None.

    Rejects search pages, RSS/feeds, Google News queries, careers/job search
    listings, bare homepages, and other research-navigation noise.
    """
    if not url or not isinstance(url, str):
        return "empty"

    url = url.strip()
    try:
        parsed = urlparse(url)
    except Exception:
        return "unparseable"

    if parsed.scheme not in ('http', 'https'):
        return "non-http scheme"

    host = (parsed.netloc or '').lower()
    if host.startswith('www.'):
        host = host[4:]
    if not host:
        return "no host"

    path = parsed.path or '/'
    query = parsed.query or ''

    for pat in _NOISE_HOST_PATTERNS:
        if pat.search(host):
            return f"noise host ({host})"

    for pat in _NOISE_PATH_PATTERNS:
        if pat.search(path):
            return f"noise path ({path})"

    # Query-string search endpoints: ?s=AI5, ?q=..., ?query=optimus
    if query:
        for part in query.split('&'):
            key = part.split('=', 1)[0].lower()
            if key in _NOISE_QUERY_KEYS:
                return f"search query (?{key}=...)"

    # LinkedIn / careers listing roots (not a specific posting article)
    if 'linkedin.com' in host and '/jobs' in path and '/view' not in path:
        return "linkedin jobs listing"
    if 'tesla.com' in host and '/careers' in path and path.rstrip('/').count('/') <= 1:
        return "careers index"

    # Require a real article-like path (not just / or /blog)
    segments = [s for s in path.split('/') if s]
    if len(segments) < 1:
        return "homepage / no article path"
    if len(segments) == 1 and segments[0].lower() in _SECTION_ROOTS:
        return f"section root (/{segments[0]})"

    return None


def is_canonical_article_url(url: str) -> bool:
    """True if URL looks like a specific article worth caching for dedup."""
    return non_canonical_reason(url) is None


def check_url(url: str) -> Optional[Dict]:
    """Check if URL has been seen before"""
    cache = load_cache()
    normalized = normalize_url(url)

    if normalized in cache['urls']:
        return cache['urls'][normalized]

    return None


def add_url(url: str, category: str, title: str = "", force: bool = False) -> bool:
    """
    Add URL to cache.

    By default rejects non-canonical (search/feed/homepage) URLs.
    Returns True if cached (new or refreshed), False if rejected.
    """
    if not force and not is_canonical_article_url(url):
        reason = non_canonical_reason(url)
        print(f"✗ Skipped non-canonical URL ({reason}): {url[:80]}")
        return False

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
    return True


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
            print("Usage: python3 scripts/url_cache.py add <url> <category> [title] [--force]")
            sys.exit(1)

        url = sys.argv[2]
        category = sys.argv[3]
        # title is optional positional; --force may appear anywhere after
        force = '--force' in sys.argv
        title_parts = [a for a in sys.argv[4:] if a != '--force']
        title = title_parts[0] if title_parts else ""

        ok = add_url(url, category, title, force=force)
        if not ok:
            sys.exit(2)

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
