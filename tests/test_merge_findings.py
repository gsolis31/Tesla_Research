"""
Unit tests for scripts/merge_findings.py

Regression-focused: protects against bugs we've already hit in production data.
"""

from __future__ import annotations

import copy

import pytest

from merge_findings import (
    MAX_KEY_POINTS,
    deduplicate_key_changes,
    get_monday_of_week,
    merge_category_updates,
    merge_metrics,
    merge_quarterly_data,
    merge_weekly_summary,
    resolve_category_key,
    _normalize_quarter_key,
    _recalculate_pd_totals,
)
# helpers live in conftest (pytest loads it automatically for fixtures;
# import for factory functions used outside fixtures)
import conftest as _cf

make_findings = _cf.make_findings
make_minimal_main_data = _cf.make_minimal_main_data


# ---------------------------------------------------------------------------
# Helpers / pure functions
# ---------------------------------------------------------------------------


class TestGetMondayOfWeek:
    def test_wednesday_maps_to_monday(self):
        assert get_monday_of_week("2026-07-15") == "2026-07-13"

    def test_monday_stays(self):
        assert get_monday_of_week("2026-07-13") == "2026-07-13"


class TestNormalizeQuarterKey:
    def test_space_full_year(self):
        assert _normalize_quarter_key("Q2 2026") == "Q2-26"

    def test_dash_full_year(self):
        assert _normalize_quarter_key("Q2-2026") == "Q2-26"

    def test_already_short(self):
        assert _normalize_quarter_key("Q2-26") == "Q2-26"

    def test_q1_historical(self):
        assert _normalize_quarter_key("Q1-15") == "Q1-15"


class TestDeduplicateKeyChanges:
    def test_same_title_category_keeps_richer(self):
        thin = {
            "title": "Story",
            "category": "Cybercab Production",
            "sentiment": {},
            "evidence": {"positive_signals": [], "negative_signals": []},
        }
        rich = {
            "title": "Story",
            "category": "Cybercab Production",
            "sentiment": {"rationale": "because"},
            "evidence": {
                "positive_signals": ["a", "b"],
                "negative_signals": ["c"],
                "key_metrics": {"actual": "1", "target": "2", "trajectory": "up"},
            },
        }
        out = deduplicate_key_changes([thin, rich])
        assert len(out) == 1
        assert out[0]["sentiment"].get("rationale") == "because"

    def test_different_titles_kept(self):
        a = {"title": "A", "category": "FSD", "sentiment": {}, "evidence": {"positive_signals": [], "negative_signals": []}}
        b = {"title": "B", "category": "FSD", "sentiment": {}, "evidence": {"positive_signals": [], "negative_signals": []}}
        assert len(deduplicate_key_changes([a, b])) == 2


class TestResolveCategoryKey:
    def test_direct(self, main_data):
        assert resolve_category_key("cybercab", main_data) == "cybercab"

    def test_alias_fsdv15(self, main_data):
        assert resolve_category_key("fsdV15", main_data) == "fsdv15"

    def test_unknown(self, main_data):
        assert resolve_category_key("nope", main_data) is None


# ---------------------------------------------------------------------------
# Weekly summary merge
# ---------------------------------------------------------------------------


class TestMergeWeeklySummary:
    def test_new_week_prepended(self, main_data):
        findings = make_findings(
            week_of="2026-07-13",
            key_changes=[
                {
                    "title": "New story",
                    "category": "Cybercab Production",
                    "status": "neutral",
                    "description": "x",
                    "source": "https://example.com/new",
                }
            ],
            trends=["New trend"],
        )
        out = merge_weekly_summary(main_data, findings)
        assert out["weeklySummaries"][0]["weekOf"] == "2026-07-13"
        assert len(out["weeklySummaries"][0]["keyChanges"]) == 1
        assert out["weeklySummaries"][0]["trends"] == ["New trend"]

    def test_append_same_week_dedupes_key_changes(self, main_data):
        findings = make_findings(
            week_of="2026-06-30",
            key_changes=[
                {
                    "title": "Existing story",
                    "category": "Cybercab Production",
                    "status": "neutral",
                    "description": "dup",
                    "source": "https://example.com/dup",
                    "sentiment": {},
                    "evidence": {"positive_signals": [], "negative_signals": []},
                },
                {
                    "title": "Brand new",
                    "category": "Cybercab Production",
                    "status": "positive",
                    "description": "new",
                    "source": "https://example.com/brand",
                    "sentiment": {},
                    "evidence": {"positive_signals": ["x"], "negative_signals": []},
                },
            ],
        )
        out = merge_weekly_summary(main_data, findings)
        week = next(w for w in out["weeklySummaries"] if w["weekOf"] == "2026-06-30")
        titles = [kc["title"] for kc in week["keyChanges"]]
        assert titles.count("Existing story") == 1
        assert "Brand new" in titles

    def test_empty_findings_noop(self, main_data):
        before = copy.deepcopy(main_data)
        out = merge_weekly_summary(main_data, make_findings())
        assert out["weeklySummaries"] == before["weeklySummaries"]


# ---------------------------------------------------------------------------
# Metrics — active vs registration routing (high-value regression)
# ---------------------------------------------------------------------------


class TestMergeMetrics:
    def test_active_fleet_appends_clean_point(self, main_data):
        findings = make_findings(
            metrics={
                "robotaxiFleet": [
                    {
                        "date": "2026-07-20",
                        "count": 22,
                        "note": "Active in-service fleet across cities",
                    }
                ]
            }
        )
        out = merge_metrics(main_data, findings)
        dates = [p["date"] for p in out["metrics"]["robotaxiFleet"]["data"]]
        assert "2026-07-20" in dates
        assert out["metrics"]["robotaxiFleet"]["breakdown"]["active"] == 22

    def test_registration_point_rerouted_away_from_active_fleet(self, main_data):
        """Regression: 175 TX DMV must not land on active series."""
        findings = make_findings(
            metrics={
                "robotaxiFleet": [
                    {
                        "date": "2026-07-15",
                        "count": 175,
                        "note": (
                            "Texas-registered Tesla robotaxi fleet jumped 117→175. "
                            "Status upgraded on registration basis; active utilization unproven."
                        ),
                        "breakdown": {"texasRegistered": 175},
                    }
                ]
            }
        )
        out = merge_metrics(main_data, findings)

        active_counts = [p["count"] for p in out["metrics"]["robotaxiFleet"]["data"]]
        assert 175 not in active_counts
        assert out["metrics"]["robotaxiFleet"]["data"][-1]["count"] == 20  # unchanged last active

        reg = out["metrics"]["robotaxiRegistered"]["data"]
        assert any(p["date"] == "2026-07-15" and p["count"] == 175 for p in reg)

    def test_dmv_registry_note_reroutes(self, main_data):
        findings = make_findings(
            metrics={
                "robotaxiFleet": [
                    {
                        "date": "2026-07-14",
                        "count": 117,
                        "note": "Texas DMV automated-vehicle registry count for Tesla robotaxi",
                    }
                ]
            }
        )
        out = merge_metrics(main_data, findings)
        assert all(p["count"] != 117 for p in out["metrics"]["robotaxiFleet"]["data"])
        assert any(p["count"] == 117 for p in out["metrics"]["robotaxiRegistered"]["data"])

    def test_idempotent_same_date_not_duplicated(self, main_data):
        findings = make_findings(
            metrics={
                "robotaxiFleet": [
                    {"date": "2026-07-08", "count": 20, "note": "same day again"},
                ]
            }
        )
        out = merge_metrics(main_data, findings)
        assert len([p for p in out["metrics"]["robotaxiFleet"]["data"] if p["date"] == "2026-07-08"]) == 1

    def test_explicit_robotaxi_registered_path(self, main_data):
        findings = make_findings(
            metrics={
                "robotaxiRegistered": [
                    {"date": "2026-07-15", "count": 175, "note": "TX registry"},
                ]
            }
        )
        out = merge_metrics(main_data, findings)
        assert out["metrics"]["robotaxiRegistered"]["data"][0]["count"] == 175

    def test_normalizes_vehicle_count_field(self, main_data):
        findings = make_findings(
            metrics={
                "cybercab": [
                    {"date": "2026-07-10", "vehicleCount": 50, "note": "staged"},
                ]
            }
        )
        out = merge_metrics(main_data, findings)
        point = next(p for p in out["metrics"]["cybercab"]["data"] if p["date"] == "2026-07-10")
        assert point["count"] == 50
        assert "vehicleCount" not in point


# ---------------------------------------------------------------------------
# Quarterly P&D
# ---------------------------------------------------------------------------


class TestMergeQuarterlyData:
    def test_adds_new_quarter_and_recalculates_totals(self, main_data):
        findings = make_findings(
            quarterly_data=[
                {"quarter": "Q2-26", "production": 451758, "delivery": 480126},
            ]
        )
        out = merge_quarterly_data(main_data, findings)
        qs = out["categories"]["productionDelivery"]["quarterlyData"]
        assert any(q["quarter"] == "Q2-26" for q in qs)
        # 400000 + 451758
        assert out["categories"]["productionDelivery"]["totalProduction"] == "851,758"
        assert out["categories"]["productionDelivery"]["totalDeliveries"] == "830,126"

    def test_duplicate_q2_2026_vs_q2_26_skipped(self, main_data):
        """Regression: both labels must not double-count."""
        main_data["categories"]["productionDelivery"]["quarterlyData"].append(
            {"quarter": "Q2-26", "production": 451758, "delivery": 480126}
        )
        _recalculate_pd_totals(main_data)
        before_prod = main_data["categories"]["productionDelivery"]["totalProduction"]

        findings = make_findings(
            quarterly_data=[
                {
                    "quarter": "Q2 2026",
                    "production": {"total": 451758},
                    "deliveries": {"total": 480126},
                }
            ]
        )
        out = merge_quarterly_data(main_data, findings)
        keys = [_normalize_quarter_key(q["quarter"]) for q in out["categories"]["productionDelivery"]["quarterlyData"]]
        assert keys.count("Q2-26") == 1
        assert out["categories"]["productionDelivery"]["totalProduction"] == before_prod

    def test_incoming_normalized_to_short_form(self, main_data):
        findings = make_findings(
            quarterly_data=[{"quarter": "Q3-2026", "production": 1, "delivery": 2}]
        )
        out = merge_quarterly_data(main_data, findings)
        assert any(q["quarter"] == "Q3-26" for q in out["categories"]["productionDelivery"]["quarterlyData"])


# ---------------------------------------------------------------------------
# Category updates
# ---------------------------------------------------------------------------


class TestMergeCategoryUpdates:
    def test_latest_status_maps_to_critical_news(self, main_data):
        findings = make_findings(
            category_updates={
                "cybercab": {
                    "latestStatus": "Fleet constrained by software",
                    "nextMilestone": "Earnings July 22",
                }
            }
        )
        out = merge_category_updates(main_data, findings)
        cat = out["categories"]["cybercab"]
        assert cat["criticalNews"] == "Fleet constrained by software"
        assert any(p.startswith("Next milestone:") for p in cat["keyPoints"])
        assert cat["latestUpdate"] == "2026-07-17"

    def test_exact_duplicate_keypoint_skipped(self, main_data):
        findings = make_findings(
            category_updates={
                "cybercab": {"newKeyPoint": "kp1"}
            }
        )
        out = merge_category_updates(main_data, findings)
        assert out["categories"]["cybercab"]["keyPoints"].count("kp1") == 1

    def test_key_points_capped(self, main_data):
        main_data["categories"]["cybercab"]["keyPoints"] = [f"old-{i}" for i in range(MAX_KEY_POINTS)]
        findings = make_findings(
            category_updates={
                "cybercab": {"newKeyPoint": "brand-new-point"}
            }
        )
        out = merge_category_updates(main_data, findings)
        kps = out["categories"]["cybercab"]["keyPoints"]
        assert len(kps) == MAX_KEY_POINTS
        assert "brand-new-point" in kps
        assert "old-0" not in kps  # FIFO drop oldest

    def test_production_delivery_no_keypoints(self, main_data):
        findings = make_findings(
            category_updates={
                "productionDelivery": {
                    "latestStatus": "Q2 strong",
                    "nextMilestone": "Q3",
                }
            }
        )
        out = merge_category_updates(main_data, findings)
        pd = out["categories"]["productionDelivery"]
        assert pd["criticalNews"] == "Q2 strong"
        assert "keyPoints" not in pd

    def test_fsdv15_resolves(self, main_data):
        findings = make_findings(
            category_updates={
                "fsdv15": {"latestStatus": "Still on supervised v14.x"}
            }
        )
        out = merge_category_updates(main_data, findings)
        assert out["categories"]["fsdv15"]["criticalNews"] == "Still on supervised v14.x"

    def test_unknown_category_skipped(self, main_data):
        findings = make_findings(
            category_updates={"ghostCategory": {"latestStatus": "nope"}}
        )
        out = merge_category_updates(main_data, findings)
        assert "ghostCategory" not in out["categories"]


# ---------------------------------------------------------------------------
# Multi-step integration (still unit-level, no disk/CI)
# ---------------------------------------------------------------------------


class TestMergePipelineSmoke:
    def test_weekly_metrics_and_quarters_together(self):
        data = make_minimal_main_data()
        findings = make_findings(
            week_of="2026-07-13",
            key_changes=[
                {
                    "title": "Italy FSD under review",
                    "category": "FSD Country Approvals",
                    "status": "neutral",
                    "description": "app only",
                    "source": "https://example.com/italy",
                    "sentiment": {},
                    "evidence": {"positive_signals": ["x"], "negative_signals": ["y"]},
                }
            ],
            metrics={
                "robotaxiFleet": [
                    {
                        "date": "2026-07-15",
                        "count": 175,
                        "note": "Texas registered robotaxi DMV registry",
                        "breakdown": {"texasRegistered": 175},
                    }
                ]
            },
            quarterly_data=[{"quarter": "Q2 2026", "production": 10, "delivery": 20}],
            category_updates={"fsd": {"latestStatus": "Italy pending"}},
        )
        data = merge_weekly_summary(data, findings)
        data = merge_metrics(data, findings)
        data = merge_quarterly_data(data, findings)
        data = merge_category_updates(data, findings)

        assert data["weeklySummaries"][0]["weekOf"] == "2026-07-13"
        assert 175 not in [p["count"] for p in data["metrics"]["robotaxiFleet"]["data"]]
        assert any(p["count"] == 175 for p in data["metrics"]["robotaxiRegistered"]["data"])
        assert any(q["quarter"] == "Q2-26" for q in data["categories"]["productionDelivery"]["quarterlyData"])
        assert data["categories"]["fsd"]["criticalNews"] == "Italy pending"
