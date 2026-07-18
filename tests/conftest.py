"""Shared fixtures for Tesla pipeline tests."""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def make_minimal_main_data() -> dict:
    """Minimal tracking data structure for merge unit tests (not production schema-complete)."""
    return {
        "lastUpdated": "2026-07-01",
        "weeklySummaries": [
            {
                "weekOf": "2026-06-30",
                "keyChanges": [
                    {
                        "title": "Existing story",
                        "category": "Cybercab Production",
                        "status": "neutral",
                        "description": "Already merged",
                        "source": "https://example.com/old",
                        "sentiment": {"headline": "neutral", "reality": "neutral", "confidence": "high"},
                        "evidence": {
                            "positive_signals": ["a"],
                            "negative_signals": ["b"],
                        },
                    }
                ],
                "trends": ["Old trend"],
            }
        ],
        "metrics": {
            "cybercab": {
                "title": "Cybercab",
                "data": [
                    {"date": "2026-06-01", "count": 100, "note": "baseline"},
                ],
            },
            "robotaxiFleet": {
                "title": "Active Robotaxi Fleet (in service)",
                "data": [
                    {"date": "2026-07-08", "count": 20, "note": "Active in-service fleet"},
                ],
                "target": "scale",
                "breakdown": {"active": 20, "staged": 0, "cities": ["Austin"]},
            },
            "robotaxiRegistered": {
                "title": "Texas Robotaxi Registrations (DMV)",
                "region": "Texas",
                "data": [],
            },
            "jobPostings": {
                "title": "Jobs",
                "data": [],
            },
            "robotaxiCities": {
                "title": "Cities",
                "lastUpdated": "2026-07-08",
                "cities": [],
                "summary": {
                    "totalCities": 0,
                    "activeCities": 0,
                    "mappedOnly": 0,
                    "unsupervisedCapable": 0,
                    "safetyMonitorOnly": 0,
                    "totalActiveVehicles": 0,
                },
            },
            "fsdApprovals": {"title": "FSD", "countries": []},
        },
        "categories": {
            "cybercab": {
                "title": "Cybercab Production",
                "latestUpdate": "2026-07-01",
                "criticalNews": "Old news",
                "keyPoints": ["kp1", "kp2"],
                "timeline": [{"date": "2026-01-01", "event": "start"}],
            },
            "fsd": {
                "title": "FSD Country Approvals",
                "latestUpdate": "2026-07-01",
                "criticalNews": "Old fsd",
                "keyPoints": [],
                "timeline": [],
            },
            "fsdv15": {
                "title": "FSD v15 Software",
                "latestUpdate": "2026-07-01",
                "criticalNews": "Still on v14",
                "keyPoints": [],
                "timeline": [],
            },
            "aiChip": {
                "title": "AI Chip Production",
                "latestUpdate": "2026-07-01",
                "criticalNews": "chips",
                "keyPoints": [],
                "timeline": [],
            },
            "optimus": {
                "title": "Optimus Production",
                "latestUpdate": "2026-07-01",
                "criticalNews": "robots",
                "keyPoints": [],
                "timeline": [],
            },
            "battery4680": {
                "title": "4680 Battery Cell Production",
                "latestUpdate": "2026-07-01",
                "criticalNews": "cells",
                "keyPoints": [],
                "timeline": [],
            },
            "terafab": {
                "title": "Terafab Manufacturing",
                "latestUpdate": "2026-07-01",
                "criticalNews": "fab",
                "keyPoints": [],
                "timeline": [],
            },
            "jobPostings": {
                "title": "Job Postings",
                "latestUpdate": "2026-07-01",
                "criticalNews": "hiring",
                "keyPoints": [],
            },
            "productionDelivery": {
                "title": "Vehicle Production & Delivery",
                "latestUpdate": "2026-07-01",
                "criticalNews": "Q2 beat",
                "totalProduction": "1000",
                "totalDeliveries": "900",
                "quarterlyData": [
                    {"quarter": "Q1-26", "production": 400000, "delivery": 350000},
                ],
                "annualSummary": [],
            },
        },
    }


def make_findings(
    *,
    date: str = "2026-07-17",
    week_of: str = "2026-07-13",
    key_changes: list | None = None,
    trends: list | None = None,
    metrics: dict | None = None,
    quarterly_data: list | None = None,
    category_updates: dict | None = None,
) -> dict:
    return {
        "date": date,
        "weekOf": week_of,
        "findings": {
            "keyChanges": key_changes or [],
            "trends": trends or [],
            "metrics": metrics or {},
            "quarterlyData": quarterly_data or [],
            "categoryUpdates": category_updates or {},
        },
        "metadata": {},
    }


@pytest.fixture
def main_data():
    return make_minimal_main_data()


@pytest.fixture
def main_data_copy(main_data):
    return copy.deepcopy(main_data)
