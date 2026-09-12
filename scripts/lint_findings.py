#!/usr/bin/env python3
"""
Deterministic quality gate for Tesla research findings.

Lints researcher (raw) and curator (curated) JSON. Mechanical checks only —
recap-vs-new and ambiguous sentiment stay with tesla-curator.

Usage:
    python3 scripts/lint_findings.py --raw --date 2026-09-06 --write-logs
    python3 scripts/lint_findings.py --curated research/findings/2026-09-06.json --write-logs
    python3 scripts/lint_findings.py --file tests/evals/raw/good_paid_rides.json --category cybercab

Exit 1 if any error-level issues. Warnings never fail the process.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from merge_findings import looks_like_registration  # noqa: E402
from paths import (  # noqa: E402
    RAW_DIR,
    TRACKING_DATA,
    coverage_path,
    curator_config_path,
    ensure_research_dirs,
    lint_curated_path,
    lint_raw_path,
    logs_dir,
    research_config_path,
)
from spawn_researcher import CATEGORIES, CATEGORY_DISPLAY_NAMES, all_seen_urls  # noqa: E402
from url_cache import load_cache, non_canonical_reason, normalize_url  # noqa: E402

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATE_RANGE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})")
VAGUE_WORDS = ("possible", "maybe", "could", "might", "potentially", "reportedly")
TITLE_MAX = 120
_TITLE_STOP = {
    "tesla", "the", "a", "an", "of", "and", "to", "for", "in", "on", "with",
    "is", "as", "at", "by", "from", "its", "still", "new",
}

# (filing categoryKey, compiled regex on title+description, owner categoryKey)
_OWNERSHIP_TRESPASS: list[tuple[str, re.Pattern, str]] = [
    ("terafab", re.compile(r"\bai[56]\b", re.I), "aiChip"),
    ("terafab", re.compile(r"\b(tape-?out|sf2 yield|wafer deal)\b", re.I), "aiChip"),
    ("aiChip", re.compile(r"\b(jeti|school board|grimes county|anderson-shiro)\b", re.I), "terafab"),
    ("fsd", re.compile(r"\b(v14\.\d|fsd v15|ota (merge|release)|teslafi|hw3 lite)\b", re.I), "fsdv15"),
    ("fsdv15", re.compile(r"\b(homologation|kba|rdw|country approval)\b", re.I), "fsd"),
    ("fsdv15", re.compile(r"\b(nhtsa|ntsb)\b", re.I), "fsd"),
    ("fsd", re.compile(r"\b(robotaxi fleet|city launch|geofence|unsupervised rides)\b", re.I), "cybercab"),
]


@dataclass
class Issue:
    level: str  # error | warning
    code: str
    message: str
    category: Optional[str] = None
    title: Optional[str] = None
    path: Optional[str] = None

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class FileLintResult:
    path: str
    category: str
    issues: list[Issue] = field(default_factory=list)
    filed: int = 0
    skip_reason: Optional[str] = None
    search_log: Optional[dict] = None
    status: str = "ok"

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.level == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.level == "warning"]

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "category": self.category,
            "status": self.status,
            "filed": self.filed,
            "skipReason": self.skip_reason,
            "errorCount": len(self.errors),
            "warningCount": len(self.warnings),
            "issues": [i.to_dict() for i in self.issues],
        }


def _parse_date(value: str) -> Optional[datetime]:
    if not value or not DATE_RE.match(value):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return None


def parse_date_range(text: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    if not text:
        return None, None
    m = DATE_RANGE_RE.search(text)
    if not m:
        return None, None
    return m.group(1), m.group(2)


def window_for_raw(
    data: dict,
    category_key: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> tuple[Optional[str], Optional[str]]:
    if date_from and date_to:
        return date_from, date_to
    # Prefer the file's own dateRange so gold fixtures (and researcher output)
    # are not overridden by whatever research-config is on disk.
    meta_from, meta_to = parse_date_range((data.get("metadata") or {}).get("dateRange"))
    if meta_from and meta_to:
        return date_from or meta_from, date_to or meta_to
    cfg_path = research_config_path(category_key)
    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text())
            return cfg.get("dateFrom") or date_from, cfg.get("dateTo") or date_to
        except (OSError, json.JSONDecodeError):
            pass
    return date_from, date_to


def _blob(kc: dict) -> str:
    return f"{kc.get('title') or ''} {kc.get('description') or ''}"


def _as_metric_point(raw: dict) -> dict:
    """Normalize metricUpdate / fleetUpdate into the shape looks_like_registration expects."""
    note = raw.get("note") or ""
    if raw.get("city") and not note:
        note = f"{raw.get('city')} {raw.get('status') or ''}"
    count = raw.get("count")
    if count is None:
        count = raw.get("vehicleCount")
    return {
        "date": raw.get("date") or raw.get("lastUpdate"),
        "count": count,
        "note": note,
        "breakdown": raw.get("breakdown") or {},
        "source": raw.get("source"),
    }


def _search_log_stats(search_log: Optional[dict]) -> dict:
    sl = search_log or {}
    considered = sl.get("considered") or []
    skipped = [c for c in considered if (c.get("decision") or "").lower() == "skip"]
    return {
        "queries": len(sl.get("queries") or []),
        "fetched": len(sl.get("fetched") or []),
        "considered": len(considered),
        "skipped": len(skipped),
        "metricCandidates": len(sl.get("metricCandidates") or []),
    }


def lint_key_change(
    kc: dict,
    *,
    category_key: str,
    date_from: Optional[str],
    date_to: Optional[str],
    path: str,
    curated: bool = False,
) -> list[Issue]:
    issues: list[Issue] = []
    title = (kc.get("title") or "").strip()
    expected = CATEGORY_DISPLAY_NAMES.get(category_key)

    def add(level: str, code: str, message: str) -> None:
        issues.append(
            Issue(
                level=level,
                code=code,
                message=message,
                category=category_key,
                title=title or None,
                path=path,
            )
        )

    if expected and kc.get("category") and kc.get("category") != expected:
        add(
            "error" if curated else "warning",
            "CATEGORY_LABEL_MISMATCH",
            f"category '{kc.get('category')}' does not match {category_key} ({expected})",
        )

    if title and len(title) > TITLE_MAX:
        add(
            "error" if curated else "warning",
            "TITLE_TOO_LONG",
            f"title is {len(title)} chars (max {TITLE_MAX})",
        )

    kc_date = kc.get("date")
    if not kc_date:
        add("error", "MISSING_DATE", "keyChange has no date")
    elif not _parse_date(kc_date):
        add("error", "INVALID_DATE", f"date '{kc_date}' is not YYYY-MM-DD")
    else:
        lo = _parse_date(date_from) if date_from else None
        hi = _parse_date(date_to) if date_to else None
        parsed = _parse_date(kc_date)
        if lo and parsed and parsed < lo:
            add("error", "STALE_DATE", f"date {kc_date} is before window start {date_from}")
        if hi and parsed and parsed > hi:
            add("error", "FUTURE_DATE", f"date {kc_date} is after window end {date_to}")

    source = kc.get("source") or ""
    if not source:
        add("error", "MISSING_SOURCE", "keyChange has no source URL")
    else:
        reason = non_canonical_reason(source)
        if reason:
            add("error", "NOISE_SOURCE_URL", f"source is not a canonical article URL ({reason})")

    sentiment = kc.get("sentiment") or {}
    status = kc.get("status")
    reality = sentiment.get("reality")
    confidence = sentiment.get("confidence") or "medium"
    evidence = kc.get("evidence") or {}
    pos = evidence.get("positive_signals") or []
    neg = evidence.get("negative_signals") or []
    if not isinstance(pos, list):
        pos = []
    if not isinstance(neg, list):
        neg = []

    if status == "positive" and reality == "negative":
        add("error" if curated else "warning", "STATUS_REALITY_MISMATCH",
            "status=positive but reality=negative")
    elif status == "positive" and reality == "neutral":
        add("warning", "STATUS_AHEAD_OF_REALITY",
            "status=positive but reality=neutral")

    if status == "positive" and len(neg) > len(pos):
        add("warning", "MORE_NEGATIVE_THAN_STATUS",
            f"{len(neg)} negative vs {len(pos)} positive signals but status=positive")

    if len(pos) + len(neg) < 2:
        add("error", "INSUFFICIENT_EVIDENCE", "fewer than 2 evidence signals")

    if "electrek.co" in source.lower() and confidence == "low":
        add("error", "ELECTREK_ONLY_LOW", "Electrek-only source with low confidence")

    desc = (kc.get("description") or "").lower()
    vague_count = sum(1 for w in VAGUE_WORDS if w in desc)
    if vague_count >= 3 and confidence == "low":
        add("error", "TOO_VAGUE", f"{vague_count} vague words + low confidence")

    blob = _blob(kc)
    for filing_cat, pat, owner in _OWNERSHIP_TRESPASS:
        if category_key == filing_cat and pat.search(blob):
            add(
                "error",
                "OWNERSHIP_TRESPASS",
                f"looks like {owner} story filed under {filing_cat} ({pat.pattern})",
            )
            break

    return issues


def lint_raw_file(
    data: dict,
    *,
    category_key: str,
    path: str = "",
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> FileLintResult:
    result = FileLintResult(path=path, category=category_key)
    result.search_log = data.get("searchLog")
    result.skip_reason = (data.get("metadata") or {}).get("skipReason")
    key_changes = data.get("keyChanges") or []
    result.filed = len(key_changes)

    def add(level: str, code: str, message: str, title: Optional[str] = None) -> None:
        result.issues.append(
            Issue(level=level, code=code, message=message,
                  category=category_key, title=title, path=path)
        )

    if data.get("categoryKey") and data.get("categoryKey") != category_key:
        add("error", "CATEGORY_KEY_MISMATCH",
            f"file categoryKey '{data.get('categoryKey')}' != '{category_key}'")

    date_from, date_to = window_for_raw(data, category_key, date_from, date_to)

    sl = result.search_log
    queries = (sl or {}).get("queries") if isinstance(sl, dict) else None
    if not sl:
        add("error", "MISSING_SEARCH_LOG", "raw findings missing searchLog")
    elif not queries:
        add("error", "NO_QUERIES", "searchLog.queries is empty — cannot tell if research ran")

    if result.filed == 0 and not result.skip_reason:
        add("error", "EMPTY_NO_SKIP_REASON",
            "no keyChanges and no metadata.skipReason")

    for kc in key_changes:
        result.issues.extend(
            lint_key_change(
                kc,
                category_key=category_key,
                date_from=date_from,
                date_to=date_to,
                path=path,
                curated=False,
            )
        )

    metric_update = data.get("metricUpdate")
    if metric_update:
        point = _as_metric_point(metric_update)
        if looks_like_registration(point):
            add(
                "error",
                "REGISTRATION_AS_PRODUCTION",
                "metricUpdate looks like a DMV/registry count — not cybercab production "
                "and not robotaxiFleet (use robotaxiRegistered)",
            )

    fleet_update = data.get("fleetUpdate")
    if fleet_update:
        point = _as_metric_point(fleet_update)
        if looks_like_registration(point):
            add(
                "error",
                "REGISTRATION_AS_FLEET",
                "fleetUpdate looks like a DMV/registry count — do not write as robotaxiFleet",
            )

    sources = (data.get("metadata") or {}).get("sourcesSearched") or []
    if result.filed > 0 and not sources:
        add("warning", "NO_SOURCES_SEARCHED", "keyChanges present but metadata.sourcesSearched is empty")

    if result.errors:
        result.status = "lint_error"
    elif result.filed == 0:
        result.status = "empty"
    else:
        result.status = "ok"
    return result


def _resolve_curated_category_key(kc: dict) -> Optional[str]:
    label = kc.get("category") or ""
    want = label.lower().replace(" ", "").replace("&", "").replace("-", "")
    for key, display in CATEGORY_DISPLAY_NAMES.items():
        if display.lower().replace(" ", "").replace("&", "").replace("-", "") == want:
            return key
        if key.lower() == want:
            return key
    return None


def lint_curated_file(
    data: dict,
    *,
    path: str = "",
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> FileLintResult:
    result = FileLintResult(path=path, category="curated")
    findings = data.get("findings") or {}
    key_changes = findings.get("keyChanges") or []
    result.filed = len(key_changes)
    result.skip_reason = (data.get("metadata") or {}).get("skipReason")

    def add(level: str, code: str, message: str, title: Optional[str] = None, category: Optional[str] = None) -> None:
        result.issues.append(
            Issue(level=level, code=code, message=message,
                  category=category or "curated", title=title, path=path)
        )

    if not data.get("date"):
        add("error", "MISSING_DATE", "curated findings missing top-level date")
    week_from, week_to = date_from, date_to
    if not week_to and data.get("date"):
        week_to = data["date"]
    if not week_from and data.get("weekOf"):
        week_from = data["weekOf"]

    for kc in key_changes:
        cat_key = _resolve_curated_category_key(kc) or "unknown"
        result.issues.extend(
            lint_key_change(
                kc,
                category_key=cat_key,
                date_from=week_from,
                date_to=week_to,
                path=path,
                curated=True,
            )
        )

    metrics = findings.get("metrics") or {}
    for series in ("cybercab", "robotaxiFleet"):
        for point in metrics.get(series) or []:
            if looks_like_registration(point):
                add(
                    "error",
                    "REGISTRATION_AS_FLEET" if series == "robotaxiFleet" else "REGISTRATION_AS_PRODUCTION",
                    f"metrics.{series} point looks like a registry count (count={point.get('count')})",
                    category=series,
                )

    urls_seen = (data.get("metadata") or {}).get("urlsSeen") or []
    for url in urls_seen:
        reason = non_canonical_reason(url)
        if reason:
            add("warning", "NOISE_URL_IN_CACHE", f"urlsSeen contains non-article URL ({reason}): {url}")

    if result.errors:
        result.status = "lint_error"
    elif result.filed == 0:
        result.status = "empty"
    else:
        result.status = "ok"
    return result


def _missing_result(category_key: str) -> FileLintResult:
    result = FileLintResult(
        path=str(RAW_DIR / f"findings-{category_key}.json"),
        category=category_key,
        status="missing",
    )
    result.issues.append(
        Issue(
            level="error",
            code="MISSING_RAW_FILE",
            message=f"research/raw/findings-{category_key}.json not found",
            category=category_key,
            path=result.path,
        )
    )
    return result


def coverage_norm_url(url: str) -> str:
    if not url or not isinstance(url, str):
        return ""
    try:
        n = normalize_url(url.strip()).lower()
    except Exception:
        n = url.strip().lower().rstrip("/")
    return n.replace("://www.", "://", 1)


def title_tokens(text: str) -> set[str]:
    cleaned = re.sub(r"[^a-z0-9]+", " ", (text or "").lower())
    return {t for t in cleaned.split() if t and t not in _TITLE_STOP and len(t) > 2}


def titles_match(a: str, b: str) -> bool:
    ta, tb = title_tokens(a), title_tokens(b)
    if not ta or not tb:
        return False
    if ta == tb:
        return True
    smaller, larger = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    if len(smaller) >= 3 and smaller <= larger:
        return True
    overlap = len(ta & tb)
    return overlap >= 3 and overlap / min(len(ta), len(tb)) >= 0.6


def researcher_index(findings_list: list[dict]) -> dict:
    """URLs and titles researchers filed or even considered (skips count as covered)."""
    urls: set[str] = set()
    titles: list[str] = []

    def add_url(url: Optional[str]) -> None:
        n = coverage_norm_url(url or "")
        if n:
            urls.add(n)

    for data in findings_list:
        for kc in data.get("keyChanges") or []:
            add_url(kc.get("source"))
            if kc.get("title"):
                titles.append(kc["title"])
        for url in data.get("urlsSeen") or []:
            add_url(url)
        sl = data.get("searchLog") or {}
        for item in sl.get("fetched") or []:
            add_url(item.get("url") if isinstance(item, dict) else item)
        for item in sl.get("considered") or []:
            if isinstance(item, dict):
                add_url(item.get("url"))
                if item.get("title"):
                    titles.append(item["title"])
    return {"urls": urls, "titles": titles}


def diff_coverage(
    coverage: dict,
    *,
    findings_list: list[dict],
    seen_urls: Optional[list[str]] = None,
    last_week_titles: Optional[list[str]] = None,
) -> dict:
    """Compare scout candidates to what researchers filed/considered and to seenUrls."""
    index = researcher_index(findings_list)
    seen = {coverage_norm_url(u) for u in (seen_urls or []) if u}
    last_week = list(last_week_titles or [])

    covered: list[dict] = []
    gaps: list[dict] = []
    ignored: list[dict] = []

    for raw in coverage.get("candidates") or []:
        if not isinstance(raw, dict):
            continue
        title = (raw.get("title") or "").strip()
        url = (raw.get("url") or "").strip()
        item = {
            "title": title,
            "url": url,
            "date": raw.get("date"),
            "likelyCategory": raw.get("likelyCategory") or "unknown",
            "whyItMightMatter": raw.get("whyItMightMatter") or "",
        }
        if url and non_canonical_reason(url):
            item["match"] = "noise_url"
            ignored.append(item)
            continue
        norm = coverage_norm_url(url)
        if norm and norm in index["urls"]:
            item["match"] = "researcher_url"
            covered.append(item)
            continue
        if title and any(titles_match(title, t) for t in index["titles"]):
            item["match"] = "researcher_title"
            covered.append(item)
            continue
        if norm and norm in seen:
            item["match"] = "seen_url"
            covered.append(item)
            continue
        if title and any(titles_match(title, t) for t in last_week):
            item["match"] = "last_week_title"
            covered.append(item)
            continue
        item["match"] = "gap"
        gaps.append(item)

    queries = ((coverage.get("searchLog") or {}).get("queries") or [])
    return {
        "status": "ok",
        "candidates": len(coverage.get("candidates") or []),
        "covered": len(covered),
        "ignored": len(ignored),
        "gapCount": len(gaps),
        "gaps": gaps,
        "queries": len(queries),
    }


def _last_week_titles() -> list[str]:
    cfg = curator_config_path()
    if cfg.exists():
        try:
            titles = [
                kc.get("title")
                for kc in (json.loads(cfg.read_text()).get("hotContext") or {}).get(
                    "lastWeekKeyChanges"
                )
                or []
                if kc.get("title")
            ]
            if titles:
                return titles
        except (OSError, json.JSONDecodeError):
            pass
    try:
        data = json.loads(TRACKING_DATA.read_text())
        if data.get("weeklySummaries"):
            return [
                kc.get("title")
                for kc in data["weeklySummaries"][0].get("keyChanges") or []
                if kc.get("title")
            ]
    except (OSError, json.JSONDecodeError, KeyError):
        pass
    return []


def load_raw_findings() -> list[dict]:
    out: list[dict] = []
    for key in CATEGORIES:
        path = RAW_DIR / f"findings-{key}.json"
        if not path.exists():
            continue
        try:
            out.append(json.loads(path.read_text()))
        except json.JSONDecodeError:
            continue
    return out


def load_coverage_diff(
    date: str,
    *,
    findings_list: Optional[list[dict]] = None,
    coverage_file: Optional[Path] = None,
    seen_urls: Optional[list[str]] = None,
    last_week_titles: Optional[list[str]] = None,
) -> dict:
    path = Path(coverage_file) if coverage_file else coverage_path(date)
    if not path.exists():
        return {
            "status": "missing",
            "candidates": 0,
            "covered": 0,
            "ignored": 0,
            "gapCount": 0,
            "gaps": [],
            "queries": 0,
        }
    try:
        coverage = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {
            "status": "invalid",
            "candidates": 0,
            "covered": 0,
            "ignored": 0,
            "gapCount": 0,
            "gaps": [],
            "queries": 0,
        }
    if seen_urls is None:
        seen_urls = all_seen_urls(load_cache().get("urls", {}))
    if last_week_titles is None:
        last_week_titles = _last_week_titles()
    return diff_coverage(
        coverage,
        findings_list=findings_list if findings_list is not None else load_raw_findings(),
        seen_urls=seen_urls,
        last_week_titles=last_week_titles,
    )


def attach_coverage_warnings(raw_results: list[FileLintResult], coverage: dict) -> None:
    if coverage.get("status") == "missing":
        return
    if coverage.get("status") == "invalid":
        return
    by_cat = {r.category: r for r in raw_results}
    for gap in coverage.get("gaps") or []:
        cat = gap.get("likelyCategory") or "unknown"
        result = by_cat.get(cat)
        if not result:
            continue
        result.issues.append(
            Issue(
                level="warning",
                code="COVERAGE_GAP",
                message=f"scout listed unmatched story: {gap.get('title')}",
                category=cat,
                title=gap.get("title"),
                path=result.path,
            )
        )


def lint_all_raw(
    *,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> list[FileLintResult]:
    results: list[FileLintResult] = []
    for category_key in CATEGORIES:
        path = RAW_DIR / f"findings-{category_key}.json"
        if not path.exists():
            results.append(_missing_result(category_key))
            continue
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            bad = FileLintResult(path=str(path), category=category_key, status="lint_error")
            bad.issues.append(
                Issue(level="error", code="INVALID_JSON", message=str(exc),
                      category=category_key, path=str(path))
            )
            results.append(bad)
            continue
        results.append(
            lint_raw_file(
                data,
                category_key=category_key,
                path=str(path),
                date_from=date_from,
                date_to=date_to,
            )
        )
    return results


def _agent_entry(result: FileLintResult) -> dict:
    stats = _search_log_stats(result.search_log)
    return {
        "status": result.status,
        "filed": result.filed,
        "queries": stats["queries"],
        "fetched": stats["fetched"],
        "considered": stats["considered"],
        "skipped": stats["skipped"],
        "lintErrors": len(result.errors),
        "lintWarnings": len(result.warnings),
        "skipReason": result.skip_reason,
        "errorCodes": [i.code for i in result.errors],
    }


def build_run_ledger(
    *,
    date: str,
    week_of: Optional[str] = None,
    raw_results: Optional[list[FileLintResult]] = None,
    curated_result: Optional[FileLintResult] = None,
    curated_data: Optional[dict] = None,
    coverage: Optional[dict] = None,
    existing: Optional[dict] = None,
) -> dict:
    ledger = existing or {}
    ledger["date"] = date
    if week_of:
        ledger["weekOf"] = week_of
    elif curated_data and curated_data.get("weekOf"):
        ledger["weekOf"] = curated_data["weekOf"]

    if raw_results is not None:
        ledger["stage"] = "researchers"
        ledger["agents"] = {r.category: _agent_entry(r) for r in raw_results}
        err = sum(len(r.errors) for r in raw_results)
        warn = sum(len(r.warnings) for r in raw_results)
        ledger["lint"] = {
            "rawErrors": err,
            "rawWarnings": warn,
            "report": str(lint_raw_path(date).as_posix()),
        }

    if coverage is not None:
        ledger["coverage"] = {
            "status": coverage.get("status"),
            "candidates": coverage.get("candidates", 0),
            "covered": coverage.get("covered", 0),
            "ignored": coverage.get("ignored", 0),
            "gapCount": coverage.get("gapCount", 0),
            "queries": coverage.get("queries", 0),
            "gaps": [
                {
                    "title": g.get("title"),
                    "url": g.get("url"),
                    "likelyCategory": g.get("likelyCategory"),
                }
                for g in coverage.get("gaps") or []
            ],
        }

    if curated_result is not None:
        ledger["stage"] = "curated"
        vs = ((curated_data or {}).get("metadata") or {}).get("validationSummary") or {}
        findings = (curated_data or {}).get("findings") or {}
        ledger["curator"] = {
            "accepted": curated_result.filed,
            "duplicatesRemoved": vs.get("duplicatesRemoved"),
            "sentimentCorrected": vs.get("sentimentCorrected"),
            "weakClaimsRejected": vs.get("weakClaimsRejected"),
            "totalKeyChanges": vs.get("totalKeyChanges"),
            "lintErrors": len(curated_result.errors),
            "lintWarnings": len(curated_result.warnings),
            "errorCodes": [i.code for i in curated_result.errors],
            "skipReason": curated_result.skip_reason,
            "trends": len(findings.get("trends") or []),
        }
        lint = ledger.get("lint") or {}
        lint["curatedErrors"] = len(curated_result.errors)
        lint["curatedWarnings"] = len(curated_result.warnings)
        lint["curatedReport"] = str(lint_curated_path(date).as_posix())
        ledger["lint"] = lint

    return ledger


def write_quality_logs(
    date: str,
    *,
    raw_results: Optional[list[FileLintResult]] = None,
    curated_result: Optional[FileLintResult] = None,
    curated_data: Optional[dict] = None,
    coverage: Optional[dict] = None,
    week_of: Optional[str] = None,
    out_dir: Optional[Path] = None,
) -> Path:
    dest = Path(out_dir) if out_dir else logs_dir(date)
    dest.mkdir(parents=True, exist_ok=True)

    if raw_results is not None:
        payload = {
            "date": date,
            "errorCount": sum(len(r.errors) for r in raw_results),
            "warningCount": sum(len(r.warnings) for r in raw_results),
            "files": [r.to_dict() for r in raw_results],
        }
        (dest / "lint-raw.json").write_text(json.dumps(payload, indent=2) + "\n")
        for r in raw_results:
            (dest / f"{r.category}.json").write_text(
                json.dumps(
                    {
                        "categoryKey": r.category,
                        "date": date,
                        "filed": r.filed,
                        "skipReason": r.skip_reason,
                        "status": r.status,
                        "searchLog": r.search_log or {},
                    },
                    indent=2,
                )
                + "\n"
            )

    if curated_result is not None:
        payload = {
            "date": date,
            "errorCount": len(curated_result.errors),
            "warningCount": len(curated_result.warnings),
            "file": curated_result.to_dict(),
        }
        (dest / "lint-curated.json").write_text(json.dumps(payload, indent=2) + "\n")

    if coverage is not None:
        (dest / "coverage-gaps.json").write_text(
            json.dumps(
                {
                    "date": date,
                    "status": coverage.get("status"),
                    "candidates": coverage.get("candidates", 0),
                    "covered": coverage.get("covered", 0),
                    "ignored": coverage.get("ignored", 0),
                    "gapCount": coverage.get("gapCount", 0),
                    "gaps": coverage.get("gaps") or [],
                },
                indent=2,
            )
            + "\n"
        )

    ledger_path = dest / "run.json"
    existing = None
    if ledger_path.exists():
        try:
            existing = json.loads(ledger_path.read_text())
        except json.JSONDecodeError:
            existing = None
    ledger = build_run_ledger(
        date=date,
        week_of=week_of,
        raw_results=raw_results,
        curated_result=curated_result,
        curated_data=curated_data,
        coverage=coverage,
        existing=existing,
    )
    lint_meta = ledger.setdefault("lint", {})
    if raw_results is not None:
        lint_meta["report"] = str((dest / "lint-raw.json").as_posix())
    if curated_result is not None:
        lint_meta["curatedReport"] = str((dest / "lint-curated.json").as_posix())
    ledger_path.write_text(json.dumps(ledger, indent=2) + "\n")
    return ledger_path


def _print_summary(results: list[FileLintResult], label: str) -> None:
    errors = sum(len(r.errors) for r in results)
    warnings = sum(len(r.warnings) for r in results)
    print(f"\n{label}: {errors} error(s), {warnings} warning(s)")
    for r in results:
        mark = "✗" if r.errors else ("!" if r.warnings else "✓")
        print(f"  {mark} {r.category:20} status={r.status:11} filed={r.filed:2} "
              f"err={len(r.errors)} warn={len(r.warnings)}")
        for issue in r.issues:
            loc = issue.title or ""
            print(f"      [{issue.level}] {issue.code}: {issue.message}"
                  + (f" ({loc})" if loc else ""))


def _infer_date(cli_date: Optional[str], curated_path: Optional[str] = None) -> str:
    if cli_date:
        return cli_date
    if curated_path:
        stem = Path(curated_path).stem
        if DATE_RE.match(stem):
            return stem
    cfg = curator_config_path()
    if cfg.exists():
        try:
            return json.loads(cfg.read_text()).get("date") or datetime.now().strftime("%Y-%m-%d")
        except (OSError, json.JSONDecodeError):
            pass
    return datetime.now().strftime("%Y-%m-%d")


def _infer_week_of(date: str) -> Optional[str]:
    cfg = curator_config_path()
    if cfg.exists():
        try:
            return json.loads(cfg.read_text()).get("weekOf")
        except (OSError, json.JSONDecodeError):
            pass
    parsed = _parse_date(date)
    if not parsed:
        return None
    monday = parsed - timedelta(days=parsed.weekday())
    return monday.strftime("%Y-%m-%d")


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint Tesla research findings")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--raw", action="store_true", help="Lint all research/raw/findings-*.json")
    group.add_argument("--curated", metavar="PATH", help="Lint a curated findings/YYYY-MM-DD.json")
    group.add_argument("--file", metavar="PATH", help="Lint a single raw findings JSON")
    parser.add_argument("--date", help="Run date (YYYY-MM-DD); default: curator config or today")
    parser.add_argument("--date-from", help="Window start (overrides config/metadata)")
    parser.add_argument("--date-to", help="Window end")
    parser.add_argument("--category", help="categoryKey for --file")
    parser.add_argument("--write-logs", action="store_true",
                        help="Write research/logs/DATE/{lint,run,category}.json")
    parser.add_argument("--out-dir", help="Override logs directory")
    args = parser.parse_args()

    ensure_research_dirs()
    date = _infer_date(args.date, args.curated)
    week_of = _infer_week_of(date)
    out_dir = Path(args.out_dir) if args.out_dir else None

    if args.raw:
        results = lint_all_raw(date_from=args.date_from, date_to=args.date_to or date)
        coverage_file = (out_dir / "coverage.json") if out_dir else coverage_path(date)
        coverage = load_coverage_diff(
            date,
            findings_list=load_raw_findings(),
            coverage_file=coverage_file if coverage_file.exists() else coverage_path(date),
        )
        attach_coverage_warnings(results, coverage)
        _print_summary(results, "raw")
        if coverage.get("status") == "missing":
            print("\ncoverage: missing (scout did not write coverage.json — recall check skipped)")
        elif coverage.get("status") == "invalid":
            print("\ncoverage: invalid JSON")
        else:
            print(f"\ncoverage: {coverage['candidates']} candidates, "
                  f"{coverage['covered']} covered, {coverage['gapCount']} gap(s)")
            for gap in coverage.get("gaps") or []:
                print(f"      [gap] {gap.get('likelyCategory')}: {gap.get('title')}")
        if args.write_logs:
            path = write_quality_logs(
                date,
                raw_results=results,
                coverage=coverage,
                week_of=week_of,
                out_dir=out_dir,
            )
            print(f"\n✓ Wrote logs → {path.parent}")
        return 1 if any(r.errors for r in results) else 0

    if args.file:
        path = Path(args.file)
        data = json.loads(path.read_text())
        category = args.category or data.get("categoryKey")
        if not category:
            print("✗ --category required when file has no categoryKey")
            return 2
        result = lint_raw_file(
            data,
            category_key=category,
            path=str(path),
            date_from=args.date_from,
            date_to=args.date_to or date,
        )
        _print_summary([result], f"file {path}")
        if args.write_logs:
            write_quality_logs(
                date, raw_results=[result], week_of=week_of, out_dir=out_dir,
            )
        return 1 if result.errors else 0

    curated_path = Path(args.curated)
    data = json.loads(curated_path.read_text())
    result = lint_curated_file(
        data,
        path=str(curated_path),
        date_from=args.date_from,
        date_to=args.date_to or data.get("date") or date,
    )
    _print_summary([result], "curated")
    if args.write_logs:
        path = write_quality_logs(
            date,
            curated_result=result,
            curated_data=data,
            week_of=week_of or data.get("weekOf"),
            out_dir=out_dir,
        )
        print(f"\n✓ Wrote logs → {path.parent}")
    return 1 if result.errors else 0


if __name__ == "__main__":
    sys.exit(main())
