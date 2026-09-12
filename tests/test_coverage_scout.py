"""Coverage-scout recall diff (URL + title match). No network, no LLM."""

from __future__ import annotations

import json
from pathlib import Path

from lint_findings import (
    attach_coverage_warnings,
    diff_coverage,
    load_coverage_diff,
    titles_match,
    write_quality_logs,
)
from spawn_researcher import SLIM_KEY_CHANGE_FIELDS, create_scout_config

EVALS = Path(__file__).resolve().parent / "evals"


def _load(rel: str) -> dict:
    return json.loads((EVALS / rel).read_text())


def _findings():
    return [
        _load("raw/good_paid_rides.json"),
        _load("raw/empty_with_searchlog.json"),
    ]


def _coverage():
    return _load("coverage/scout_candidates.json")


class TestTitleMatch:
    def test_same_story_different_wording(self):
        assert titles_match(
            "Paid Austin Cybercab rides start — 45 registered, dispatch pool unstated",
            "Paid Austin Cybercab rides start — dispatch pool unstated",
        )

    def test_unrelated_titles(self):
        assert not titles_match(
            "Paid Austin Cybercab rides start",
            "AI5 sample wafers rumored at Samsung Taylor",
        )


class TestDiffCoverage:
    def setup_method(self):
        self.result = diff_coverage(
            _coverage(),
            findings_list=_findings(),
            seen_urls=["https://www.koreatimes.co.kr/tesla-taylor-2nm"],
            last_week_titles=[],
        )

    def test_counts(self):
        # 7 candidates: 2 cybercab covered (url + title), 1 rgb considered skip,
        # 1 korea seen/considered, 1 noise ignored, 2 gaps (NHTSA + AI5 wafers)
        assert self.result["status"] == "ok"
        assert self.result["candidates"] == 7
        assert self.result["ignored"] == 1
        assert self.result["gapCount"] == 2
        assert self.result["covered"] == 4

    def test_filed_url_is_covered(self):
        gap_titles = {g["title"] for g in self.result["gaps"]}
        assert "Paid Austin Cybercab rides start" not in gap_titles

    def test_title_match_different_host_is_covered(self):
        gap_urls = {g["url"] for g in self.result["gaps"]}
        assert "https://teslanorth.com/2026/09/04/cybercab-public-rides-austin/" not in gap_urls

    def test_considered_skip_is_covered(self):
        gap_urls = {g["url"] for g in self.result["gaps"]}
        assert "https://www.teslarati.com/tesla-cybercab-rgb-lights/" not in gap_urls

    def test_noise_homepage_not_a_gap(self):
        gap_urls = {g["url"] for g in self.result["gaps"]}
        assert "https://www.teslarati.com/" not in gap_urls

    def test_nhtsa_and_ai5_are_gaps(self):
        gap_cats = {g["likelyCategory"] for g in self.result["gaps"]}
        gap_titles = {g["title"] for g in self.result["gaps"]}
        assert "cybercab" in gap_cats
        assert "aiChip" in gap_cats
        assert any("AQ26002" in t for t in gap_titles)
        assert any("AI5 sample" in t for t in gap_titles)

    def test_seen_url_without_researcher_hit_is_covered(self):
        only_korea = diff_coverage(
            {
                "candidates": [
                    {
                        "title": "Unrelated restatement",
                        "url": "https://www.koreatimes.co.kr/tesla-taylor-2nm",
                        "likelyCategory": "aiChip",
                    }
                ],
                "searchLog": {"queries": [{"q": "x"}]},
            },
            findings_list=[],
            seen_urls=["https://www.koreatimes.co.kr/tesla-taylor-2nm"],
        )
        assert only_korea["gapCount"] == 0
        assert only_korea["covered"] == 1


class TestMissingCoverage:
    def test_missing_file_is_not_an_error(self, tmp_path: Path):
        result = load_coverage_diff(
            "2099-01-01",
            findings_list=[],
            coverage_file=tmp_path / "nope.json",
            seen_urls=[],
            last_week_titles=[],
        )
        assert result["status"] == "missing"
        assert result["gapCount"] == 0


class TestAttachAndLedger:
    def test_gap_warns_owning_category(self):
        from lint_findings import lint_raw_file

        cyber = lint_raw_file(
            _load("raw/good_paid_rides.json"),
            category_key="cybercab",
            path="cybercab.json",
        )
        chip = lint_raw_file(
            _load("raw/empty_with_searchlog.json"),
            category_key="aiChip",
            path="aiChip.json",
        )
        coverage = diff_coverage(
            _coverage(),
            findings_list=_findings(),
            seen_urls=["https://www.koreatimes.co.kr/tesla-taylor-2nm"],
        )
        attach_coverage_warnings([cyber, chip], coverage)
        chip_codes = {i.code for i in chip.issues}
        assert "COVERAGE_GAP" in chip_codes
        assert chip.status == "empty"
        assert chip.errors == []

    def test_run_ledger_records_gaps(self, tmp_path: Path):
        from lint_findings import lint_raw_file

        cyber = lint_raw_file(
            _load("raw/good_paid_rides.json"),
            category_key="cybercab",
            path="cybercab.json",
        )
        coverage = diff_coverage(
            _coverage(),
            findings_list=_findings(),
            seen_urls=["https://www.koreatimes.co.kr/tesla-taylor-2nm"],
        )
        write_quality_logs(
            "2026-09-06",
            raw_results=[cyber],
            coverage=coverage,
            week_of="2026-08-31",
            out_dir=tmp_path,
        )
        ledger = json.loads((tmp_path / "run.json").read_text())
        assert ledger["coverage"]["gapCount"] == 2
        gaps_file = json.loads((tmp_path / "coverage-gaps.json").read_text())
        assert len(gaps_file["gaps"]) == 2


class TestScoutConfig:
    def test_scout_config_is_slim_no_url_cache(self):
        data = {
            "weeklySummaries": [
                {
                    "weekOf": "2026-08-24",
                    "keyChanges": [
                        {
                            "title": "Old story",
                            "description": "Must not appear",
                            "date": "2026-08-28",
                            "category": "Cybercab Production",
                            "status": "neutral",
                            "source": "https://example.com/old",
                            "evidence": {"positive_signals": ["x"]},
                        }
                    ],
                }
            ]
        }
        cfg = create_scout_config("2026-08-31", "2026-09-06", "2026-08-31", data=data)
        assert "seenUrls" not in cfg["hotContext"]
        last = cfg["hotContext"]["lastWeekKeyChanges"]
        assert last[0]["title"] == "Old story"
        assert set(last[0]) <= set(SLIM_KEY_CHANGE_FIELDS)
        assert "description" not in last[0]
        assert cfg["outputPath"].endswith("coverage.json")
        assert cfg["maxCandidates"] == 15
        assert "cybercab" in cfg["categoryKeys"]
