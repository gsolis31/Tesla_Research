#!/usr/bin/env python3
"""Assemble a curated findings draft from raw researcher files.

Copies keyChanges and metrics, drops lint errors and exact duplicates,
and returns a short review list for tesla-curator. The curator edits the
draft. It does not re-copy the nine raw files.

Usage:
    python3 scripts/assemble_findings.py 2026-11-14
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lint_findings import TITLE_MAX, _lint_city_fleet_point  # noqa: E402
from merge_findings import looks_like_registration  # noqa: E402
from paths import (  # noqa: E402
    RAW_DIR,
    curated_findings_path,
    lint_raw_path,
)
from spawn_researcher import CATEGORIES  # noqa: E402
from url_cache import canonical_seen_url, load_cache  # noqa: E402


def _cache_index(cache_urls: dict) -> dict:
    index = {}
    for key, meta in (cache_urls or {}).items():
        index[canonical_seen_url(key)] = meta if isinstance(meta, dict) else {}
        if isinstance(meta, dict):
            original = canonical_seen_url(meta.get("originalUrl") or "")
            if original:
                index[original] = meta
    return index


def _lint_error_titles(lint_report: dict | None) -> set[tuple[str, str]]:
    found = set()
    if not lint_report:
        return found
    for file_result in lint_report.get("files") or []:
        category = file_result.get("category") or ""
        for issue in file_result.get("issues") or []:
            if issue.get("level") != "error":
                continue
            title = (issue.get("title") or "").strip()
            if title:
                found.add((category, title))
    return found


def _city_errors(point: dict, registered_counts: set[int]) -> list[dict]:
    found = []

    def add(level, code, message, title=None, category=None):
        if level == "error":
            found.append({"code": code, "message": message})

    _lint_city_fleet_point(point, add, "cityFleet", registered_counts=registered_counts)
    return found


def assemble_payload(
    category_findings: list[dict],
    *,
    date: str,
    week_of: str,
    date_from: str | None = None,
    date_to: str | None = None,
    lint_report: dict | None = None,
    cache_urls: dict | None = None,
    last_week: list | None = None,
    gaps: list | None = None,
) -> tuple[dict, dict]:
    """Return (findings document, curator review). Does not write files."""
    error_titles = _lint_error_titles(lint_report)
    cache = _cache_index(cache_urls or {})
    last_week_keys = {
        ((kc.get("title") or "").strip(), (kc.get("category") or "").strip())
        for kc in (last_week or [])
    }

    dropped_lint = []
    dropped_dupes = []
    cache_hits = []
    must_fix = []
    metric_drops = []
    kept = []
    seen_this_week = set()

    for raw in category_findings:
        category_key = raw.get("categoryKey") or ""
        for kc in raw.get("keyChanges") or []:
            title = (kc.get("title") or "").strip()
            category = (kc.get("category") or "").strip()
            source = kc.get("source") or ""
            if (category_key, title) in error_titles:
                dropped_lint.append({
                    "categoryKey": category_key,
                    "title": title,
                    "reason": "lint error",
                })
                continue
            ident = (title, category)
            if ident in last_week_keys or ident in seen_this_week:
                dropped_dupes.append({
                    "categoryKey": category_key,
                    "title": title,
                    "category": category,
                    "reason": "same title and category",
                })
                continue
            seen_this_week.add(ident)
            canonical = canonical_seen_url(source)
            cached = cache.get(canonical) if canonical else None
            if cached is not None:
                cache_hits.append({
                    "title": title,
                    "category": category,
                    "source": source,
                    "cachedTitle": cached.get("title") or "",
                })
            sentiment = kc.get("sentiment") or {}
            if kc.get("status") == "positive" and sentiment.get("reality") == "negative":
                must_fix.append({
                    "title": title,
                    "category": category,
                    "issue": "status=positive but reality=negative",
                })
            if len(title) > TITLE_MAX:
                must_fix.append({
                    "title": title,
                    "category": category,
                    "issue": f"title is {len(title)} chars (max {TITLE_MAX})",
                })
            kept.append({k: v for k, v in kc.items() if not str(k).startswith("_")})

    metrics = {
        "cybercab": [],
        "robotaxiFleet": [],
        "robotaxiRegistered": [],
        "cityFleet": [],
        "jobPostings": [],
    }
    quarterly = []
    category_updates = {}
    registered_counts: set[int] = set()
    for raw in category_findings:
        registered = raw.get("registeredUpdate")
        if isinstance(registered, dict) and registered.get("count") is not None:
            registered_counts.add(int(registered["count"]))

    for raw in category_findings:
        category_key = raw.get("categoryKey") or ""
        if raw.get("categoryUpdate"):
            category_updates[category_key] = raw["categoryUpdate"]
        if category_key == "productionDelivery" and raw.get("quarterlyData"):
            quarterly.extend(raw["quarterlyData"])

        registered = raw.get("registeredUpdate")
        if isinstance(registered, dict):
            metrics["robotaxiRegistered"].append(registered)

        fleet = raw.get("fleetUpdate")
        if isinstance(fleet, dict):
            if looks_like_registration(fleet):
                metric_drops.append({
                    "categoryKey": category_key,
                    "field": "fleetUpdate",
                    "reason": "registry count is not an in-service fleet",
                })
            else:
                metrics["robotaxiFleet"].append(fleet)

        metric = raw.get("metricUpdate")
        if isinstance(metric, dict):
            if category_key == "cybercab" and looks_like_registration(metric):
                metric_drops.append({
                    "categoryKey": category_key,
                    "field": "metricUpdate",
                    "reason": "registry count is not Cybercab production",
                })
            elif category_key == "cybercab":
                metrics["cybercab"].append(metric)
            elif category_key == "jobPostings":
                metrics["jobPostings"].append(metric)
            else:
                metric_drops.append({
                    "categoryKey": category_key,
                    "field": "metricUpdate",
                    "reason": "no series mapping; curator decides",
                })

        for point in raw.get("cityFleetUpdate") or []:
            errors = _city_errors(point, registered_counts)
            if errors:
                metric_drops.append({
                    "categoryKey": category_key,
                    "field": "cityFleetUpdate",
                    "name": point.get("name"),
                    "reason": errors[0]["message"],
                })
            else:
                metrics["cityFleet"].append(point)

    trends = _trends(kept)
    sources = []
    urls = []
    seen_urls = set()
    for raw in category_findings:
        for host in (raw.get("metadata") or {}).get("sourcesSearched") or []:
            if host not in sources:
                sources.append(host)
        for url in raw.get("urlsSeen") or []:
            canonical = canonical_seen_url(url)
            if canonical and canonical not in seen_urls:
                seen_urls.add(canonical)
                urls.append(canonical)

    findings = {
        "date": date,
        "weekOf": week_of,
        "findings": {
            "keyChanges": kept,
            "trends": trends,
            "metrics": metrics,
            "quarterlyData": quarterly,
            "categoryUpdates": category_updates,
        },
        "metadata": {
            "sourcesSearched": sources,
            "urlsSeen": urls,
            "categoriesResearched": [
                raw.get("categoryKey")
                for raw in category_findings
                if raw.get("categoryKey")
            ],
            "dateRange": f"{date_from or week_of} to {date_to or date}",
            "coverageGaps": [],
            "validationSummary": {
                "totalKeyChanges": sum(len(raw.get("keyChanges") or []) for raw in category_findings),
                "assembled": len(kept),
                "duplicatesRemoved": len(dropped_dupes),
                "lintDropped": len(dropped_lint),
                "sentimentCorrected": 0,
                "weakClaimsRejected": 0,
            },
        },
    }
    review = {
        "mustFix": must_fix,
        "cacheHits": cache_hits,
        "droppedLintErrors": dropped_lint,
        "droppedDuplicates": dropped_dupes,
        "metricDrops": metric_drops,
        "coverageGaps": gaps or [],
        "keyChangeCount": len(kept),
    }
    return findings, review


def _trends(key_changes: list[dict]) -> list[str]:
    by_category: dict[str, list[dict]] = {}
    for kc in key_changes:
        by_category.setdefault(kc.get("category") or "Unknown", []).append(kc)
    ranked = sorted(by_category.items(), key=lambda item: -len(item[1]))
    trends = []
    for category, items in ranked[:4]:
        negative = [kc for kc in items if kc.get("status") == "negative"]
        lead = (negative or items)[0]
        trends.append(f"{category}: {lead.get('title')}")
    return trends


def load_raw_category_files(raw_dir: Path | None = None) -> list[dict]:
    raw_dir = raw_dir or RAW_DIR
    loaded = []
    for category_key in CATEGORIES:
        path = raw_dir / f"findings-{category_key}.json"
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}")
        loaded.append(json.loads(path.read_text()))
    return loaded


def write_draft(date: str, week_of: str, *, date_from: str | None = None, date_to: str | None = None,
                last_week: list | None = None, gaps: list | None = None) -> tuple[dict, dict]:
    lint_path = lint_raw_path(date)
    if not lint_path.exists():
        raise FileNotFoundError(
            f"Missing {lint_path}. Run lint_findings.py --raw --date {date} --write-logs first."
        )
    lint_report = json.loads(lint_path.read_text())
    findings, review = assemble_payload(
        load_raw_category_files(),
        date=date,
        week_of=week_of,
        date_from=date_from,
        date_to=date_to,
        lint_report=lint_report,
        cache_urls=load_cache().get("urls", {}),
        last_week=last_week,
        gaps=gaps,
    )
    output = curated_findings_path(date)
    output.write_text(json.dumps(findings, indent=2) + "\n")
    return findings, review


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/assemble_findings.py YYYY-MM-DD")
        sys.exit(1)
    date = sys.argv[1]
    print("assemble_findings.py writes the draft as part of spawn_curator.py")
    print(f"Date requested: {date}")
    print("Run: python3 scripts/spawn_curator.py", date)


if __name__ == "__main__":
    main()
