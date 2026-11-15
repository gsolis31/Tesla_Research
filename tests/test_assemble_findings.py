"""Assemble copies raw findings into a draft. Judgment stays with the curator."""

from __future__ import annotations

from assemble_findings import assemble_payload


def _kc(**overrides) -> dict:
    base = {
        "title": "Austin sighting floor rises",
        "description": "Thirty-day distinct vehicles moved up.",
        "date": "2026-11-14",
        "category": "Cybercab Production",
        "status": "neutral",
        "sentiment": {"headline": "neutral", "reality": "neutral", "confidence": "high"},
        "evidence": {
            "positive_signals": ["Floor rose"],
            "negative_signals": ["Still a floor, not a dispatch count"],
        },
        "source": "https://www.example.com/austin/",
    }
    base.update(overrides)
    return base


def _assemble(raw, **kwargs):
    defaults = {
        "date": "2026-11-14",
        "week_of": "2026-11-09",
        "date_from": "2026-11-07",
        "date_to": "2026-11-14",
    }
    defaults.update(kwargs)
    return assemble_payload(raw, **defaults)


def test_lint_error_title_is_dropped_and_warning_is_kept():
    raw = [{
        "categoryKey": "cybercab",
        "keyChanges": [
            _kc(title="Registry filed as fleet"),
            _kc(title="Paid rides continue", source="https://example.com/rides"),
        ],
    }]
    lint = {
        "files": [{
            "category": "cybercab",
            "issues": [
                {"level": "error", "code": "REGISTRATION_AS_FLEET", "title": "Registry filed as fleet"},
                {"level": "warning", "code": "TITLE_TOO_LONG", "title": "Paid rides continue"},
            ],
        }]
    }
    findings, review = _assemble(raw, lint_report=lint)
    titles = [kc["title"] for kc in findings["findings"]["keyChanges"]]
    assert titles == ["Paid rides continue"]
    assert review["droppedLintErrors"] == [{
        "categoryKey": "cybercab",
        "title": "Registry filed as fleet",
        "reason": "lint error",
    }]
    assert findings["metadata"]["validationSummary"]["lintDropped"] == 1


def test_cache_hit_is_kept_and_listed():
    raw = [{
        "categoryKey": "fsd",
        "keyChanges": [_kc(
            title="Korea filing updated",
            category="FSD Country Approvals",
            source="https://www.example.com/korea/",
        )],
    }]
    cache = {
        "https://example.com/korea": {
            "title": "Earlier Korea note",
            "originalUrl": "https://www.example.com/korea/",
            "category": "FSD Country Approvals",
        }
    }
    findings, review = _assemble(raw, cache_urls=cache)
    assert len(findings["findings"]["keyChanges"]) == 1
    assert review["cacheHits"] == [{
        "title": "Korea filing updated",
        "category": "FSD Country Approvals",
        "source": "https://www.example.com/korea/",
        "cachedTitle": "Earlier Korea note",
    }]


def test_positive_status_with_negative_reality_is_flagged_not_flipped():
    raw = [{
        "categoryKey": "optimus",
        "keyChanges": [_kc(
            title="Optimus demo looks production-ready",
            category="Optimus Production",
            status="positive",
            sentiment={"headline": "positive", "reality": "negative", "confidence": "medium"},
            source="https://example.com/optimus",
        )],
    }]
    findings, review = _assemble(raw)
    assert findings["findings"]["keyChanges"][0]["status"] == "positive"
    assert review["mustFix"] == [{
        "title": "Optimus demo looks production-ready",
        "category": "Optimus Production",
        "issue": "status=positive but reality=negative",
    }]
    assert findings["metadata"]["validationSummary"]["sentimentCorrected"] == 0


def test_long_title_is_flagged_not_truncated():
    title = "T" * 121
    raw = [{"categoryKey": "aiChip", "keyChanges": [_kc(
        title=title,
        category="AI Chip Production",
        source="https://example.com/ai5",
    )]}]
    findings, review = _assemble(raw)
    assert findings["findings"]["keyChanges"][0]["title"] == title
    assert review["mustFix"][0]["issue"] == "title is 121 chars (max 120)"


def test_registration_metrics_stay_off_fleet_production_and_city_rows():
    raw = [{
        "categoryKey": "cybercab",
        "keyChanges": [],
        "registeredUpdate": {
            "date": "2026-11-14",
            "count": 1306,
            "note": "Texas DMV roster",
        },
        "fleetUpdate": {
            "date": "2026-11-14",
            "count": 1306,
            "note": "Texas registered vehicles, DMV registry count",
        },
        "metricUpdate": {
            "date": "2026-11-14",
            "count": 573,
            "note": "automated vehicle registry Cybercab authorizations",
        },
        "cityFleetUpdate": [
            {
                "name": "Austin",
                "activeVehicles": 186,
                "basis": "sighting-floor",
                "date": "2026-11-14",
            },
            {
                "name": "Statewide",
                "activeVehicles": 1306,
                "basis": "sighting-floor",
                "date": "2026-11-14",
            },
            {
                "name": "Dallas",
                "activeVehicles": 56,
                "basis": "registry",
                "date": "2026-11-14",
            },
        ],
    }]
    findings, review = _assemble(raw)
    metrics = findings["findings"]["metrics"]
    assert metrics["robotaxiRegistered"] == [raw[0]["registeredUpdate"]]
    assert metrics["robotaxiFleet"] == []
    assert metrics["cybercab"] == []
    assert [row["name"] for row in metrics["cityFleet"]] == ["Austin"]
    reasons = {item["field"]: item["reason"] for item in review["metricDrops"] if "name" not in item}
    assert reasons["fleetUpdate"] == "registry count is not an in-service fleet"
    assert reasons["metricUpdate"] == "registry count is not Cybercab production"
    city_reasons = [item["reason"] for item in review["metricDrops"] if item["field"] == "cityFleetUpdate"]
    assert any("Statewide" in reason and "registry" in reason for reason in city_reasons)
    assert any("Dallas" in reason and "basis" in reason for reason in city_reasons)


def test_job_postings_copy_and_unmapped_metrics_are_listed():
    raw = [
        {
            "categoryKey": "jobPostings",
            "keyChanges": [],
            "metricUpdate": {"date": "2026-11-14", "count": 2400, "note": "AI and robotics roles"},
        },
        {
            "categoryKey": "fsd",
            "keyChanges": [],
            "metricUpdate": {"date": "2026-11-14", "count": 8, "note": "country approvals"},
        },
    ]
    findings, review = _assemble(raw)
    assert findings["findings"]["metrics"]["jobPostings"][0]["count"] == 2400
    assert findings["findings"]["metrics"]["cybercab"] == []
    assert review["metricDrops"] == [{
        "categoryKey": "fsd",
        "field": "metricUpdate",
        "reason": "no series mapping; curator decides",
    }]


def test_exact_duplicates_drop_and_internal_fields_are_stripped():
    story = _kc(title="Same story", _internal="drop me")
    raw = [{"categoryKey": "cybercab", "keyChanges": [story, dict(story)]}]
    last_week = [{"title": "Already filed", "category": "Cybercab Production"}]
    raw[0]["keyChanges"].append(_kc(title="Already filed", source="https://example.com/old"))
    findings, review = _assemble(raw, last_week=last_week)
    kept = findings["findings"]["keyChanges"]
    assert [kc["title"] for kc in kept] == ["Same story"]
    assert "_internal" not in kept[0]
    assert len(review["droppedDuplicates"]) == 2


def test_trends_prefer_a_negative_lead_and_stop_at_four():
    categories = [
        ("Cybercab Production", "cybercab", 3),
        ("FSD Country Approvals", "fsd", 2),
        ("Optimus Production", "optimus", 2),
        ("AI Chip Production", "aiChip", 1),
        ("Job Postings", "jobPostings", 1),
    ]
    raw = []
    for display, key, count in categories:
        changes = []
        for i in range(count):
            status = "negative" if i == 0 and key == "cybercab" else "neutral"
            title = "Cybercab delay" if status == "negative" else f"{display} item {i}"
            changes.append(_kc(title=title, category=display, status=status, source=f"https://example.com/{key}-{i}"))
        raw.append({"categoryKey": key, "keyChanges": changes})
    findings, _review = _assemble(raw)
    trends = findings["findings"]["trends"]
    assert len(trends) == 4
    assert trends[0] == "Cybercab Production: Cybercab delay"
