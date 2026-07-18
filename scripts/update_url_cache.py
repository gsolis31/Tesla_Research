#!/usr/bin/env python3
"""
Update URL cache from a validated findings file.

Only caches canonical article source URLs from accepted keyChanges.
Search pages, RSS feeds, homepage queries, and careers listings are rejected.

Usage:
    python3 scripts/update_url_cache.py research/findings/2026-07-17.json
    python3 scripts/update_url_cache.py research/findings/2026-07-17.json --dry-run
    python3 scripts/update_url_cache.py --prune  # remove non-canonical URLs already in cache
"""

import json
import sys
from pathlib import Path

# Allow running as scripts/update_url_cache.py
sys.path.insert(0, str(Path(__file__).parent))
from url_cache import (  # noqa: E402
    add_url,
    is_canonical_article_url,
    load_cache,
    save_cache,
    normalize_url,
    non_canonical_reason,
)


def update_from_findings(findings_path: Path, dry_run: bool = False) -> dict:
    """Cache source URLs from keyChanges only."""
    with open(findings_path) as f:
        findings = json.load(f)

    key_changes = findings.get('findings', {}).get('keyChanges', [])
    added = 0
    skipped = 0
    rejected = 0

    print("=" * 60)
    print("URL Cache Update (canonical article sources only)")
    print("=" * 60)
    print(f"Findings: {findings_path}")
    print(f"keyChanges: {len(key_changes)}")
    if dry_run:
        print("(dry-run — no writes)\n")
    else:
        print()

    seen_normalized = set()

    for kc in key_changes:
        url = (kc.get('source') or '').strip()
        if not url:
            skipped += 1
            continue

        category = kc.get('category', 'unknown')
        title = (kc.get('title') or '')[:120]

        if not is_canonical_article_url(url):
            reason = non_canonical_reason(url)
            print(f"✗ reject  {url[:70]}  ({reason})")
            rejected += 1
            continue

        norm = normalize_url(url)
        if norm in seen_normalized:
            skipped += 1
            continue
        seen_normalized.add(norm)

        if dry_run:
            print(f"+ would add  [{category[:24]:24}] {url[:70]}")
            added += 1
        else:
            # add_url prints its own confirmation; suppress noise by calling carefully
            before = load_cache()
            already = normalize_url(url) in before['urls']
            add_url(url, category, title)
            if already:
                skipped += 1
            else:
                added += 1

    print()
    print(f"Added: {added}  |  Already present / dup: {skipped}  |  Rejected noise: {rejected}")
    print("=" * 60)
    return {'added': added, 'skipped': skipped, 'rejected': rejected}


def prune_cache(dry_run: bool = False) -> dict:
    """Remove non-canonical URLs from the existing cache."""
    cache = load_cache()
    urls = cache.get('urls', {})
    to_remove = []

    for url, data in urls.items():
        original = data.get('originalUrl', url)
        if not is_canonical_article_url(original) and not is_canonical_article_url(url):
            to_remove.append((url, non_canonical_reason(original or url)))

    print("=" * 60)
    print("URL Cache Prune (remove non-canonical entries)")
    print("=" * 60)
    print(f"Total entries: {len(urls)}")
    print(f"To remove: {len(to_remove)}")
    if dry_run:
        print("(dry-run — no writes)\n")
    else:
        print()

    for url, reason in to_remove:
        print(f"✗ remove  {url[:70]}  ({reason})")
        if not dry_run:
            del cache['urls'][url]

    if not dry_run and to_remove:
        # Rebuild stats
        category_counts: dict = {}
        for data in cache['urls'].values():
            cat = data.get('category', 'unknown')
            category_counts[cat] = category_counts.get(cat, 0) + 1
        cache['stats']['totalUrls'] = len(cache['urls'])
        cache['stats']['categoryCounts'] = category_counts
        save_cache(cache)
        print(f"\n✓ Cache now has {len(cache['urls'])} URLs")
    elif dry_run:
        print(f"\nWould leave {len(urls) - len(to_remove)} URLs")

    print("=" * 60)
    return {'removed': len(to_remove), 'remaining': len(urls) - len(to_remove)}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    dry_run = '--dry-run' in sys.argv
    args = [a for a in sys.argv[1:] if a != '--dry-run']

    if not args:
        print(__doc__)
        sys.exit(1)

    if args[0] == '--prune':
        prune_cache(dry_run=dry_run)
        return

    findings_path = Path(args[0])
    if not findings_path.exists():
        print(f"Error: {findings_path} not found")
        sys.exit(1)

    update_from_findings(findings_path, dry_run=dry_run)


if __name__ == '__main__':
    main()
