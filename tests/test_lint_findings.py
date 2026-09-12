"""Gold-set evals for scripts/lint_findings.py.

Fixtures under tests/evals/ encode production bugs (Sep 6 registration-as-fleet,
Aug 22 Nevada status=positive vs reality=neutral) plus mechanical rejects.
No network, no LLM.
"""

from __future__ import annotations

import json
from pathlib import Path

from lint_findings import (
    build_run_ledger,
    lint_curated_file,
    lint_raw_file,
    write_quality_logs,
)
from merge_findings import looks_like_registration

EVALS = Path(__file__).resolve().parent / "evals"


def _load(rel: str) -> dict:
    return json.loads((EVALS / rel).read_text())


def _codes(result, level: str | None = None) -> set[str]:
    issues = result.issues if level is None else [i for i in result.issues if i.level == level]
    return {i.code for i in issues}


def _lint_raw(rel: str, category: str | None = None):
    data = _load(rel)
    return lint_raw_file(
        data,
        category_key=category or data["categoryKey"],
        path=rel,
    )


# ---------------------------------------------------------------------------
# Production regressions
# ---------------------------------------------------------------------------


class TestSep6RegistrationAsFleet:
    def test_metric_and_fleet_are_errors(self):
        result = _lint_raw("raw/sep6_registration_as_fleet.json")
        assert "REGISTRATION_AS_PRODUCTION" in _codes(result, "error")
        assert "REGISTRATION_AS_FLEET" in _codes(result, "error")
        assert result.status == "lint_error"

    def test_paid_rides_keychange_is_not_dropped(self):
        result = _lint_raw("raw/sep6_registration_as_fleet.json")
        kc_codes = {
            i.code
            for i in result.issues
            if i.title and "Paid Austin" in i.title
        }
        assert "REGISTRATION_AS_PRODUCTION" not in kc_codes
        assert "INSUFFICIENT_EVIDENCE" not in kc_codes


class TestAug22NevadaPositive:
    def test_status_ahead_of_reality_is_warning(self):
        result = _lint_raw("raw/aug22_nevada_positive.json")
        assert "STATUS_AHEAD_OF_REALITY" in _codes(result, "warning")
        assert "MORE_NEGATIVE_THAN_STATUS" in _codes(result, "warning")
        assert result.errors == []
        assert result.status == "ok"


class TestLooksLikeRegistration:
    def test_txmccs_note(self):
        assert looks_like_registration(
            {"count": 45, "note": "Texas TxMCCS 45 Cybercabs"}
        )

    def test_active_fleet_note_is_clean(self):
        assert not looks_like_registration(
            {"count": 21, "note": "Last verified active unsupervised fleet in Austin"}
        )


# ---------------------------------------------------------------------------
# Mechanical gates
# ---------------------------------------------------------------------------


class TestSearchLogContract:
    def test_empty_with_searchlog_passes(self):
        result = _lint_raw("raw/empty_with_searchlog.json")
        assert result.errors == []
        assert result.status == "empty"
        assert result.skip_reason

    def test_empty_without_searchlog_errors(self):
        result = _lint_raw("raw/empty_no_searchlog.json")
        assert "MISSING_SEARCH_LOG" in _codes(result, "error")
        assert result.status == "lint_error"


class TestWeakClaims:
    def test_electrek_only_low(self):
        result = _lint_raw("raw/electrek_only_low.json")
        assert "ELECTREK_ONLY_LOW" in _codes(result, "error")

    def test_insufficient_evidence(self):
        result = _lint_raw("raw/insufficient_evidence.json")
        assert "INSUFFICIENT_EVIDENCE" in _codes(result, "error")

    def test_noise_source_url(self):
        result = _lint_raw("raw/noise_source_url.json")
        assert "NOISE_SOURCE_URL" in _codes(result, "error")

    def test_stale_date(self):
        result = _lint_raw("raw/stale_date.json")
        assert "STALE_DATE" in _codes(result, "error")

    def test_title_too_long_is_warning_on_raw(self):
        result = _lint_raw("raw/title_too_long.json")
        assert "TITLE_TOO_LONG" in _codes(result, "warning")
        assert "TITLE_TOO_LONG" not in _codes(result, "error")


class TestOwnership:
    def test_ai5_tapeout_not_terafab(self):
        result = _lint_raw("raw/terafab_ai5_tapeout.json")
        assert "OWNERSHIP_TRESPASS" in _codes(result, "error")


class TestKnownGood:
    def test_paid_rides_clean(self):
        result = _lint_raw("raw/good_paid_rides.json")
        assert result.errors == []
        assert result.status == "ok"
        assert result.filed == 1


class TestCurated:
    def test_good_minimal_passes(self):
        data = _load("curated/good_minimal.json")
        result = lint_curated_file(data, path="good_minimal.json")
        assert result.errors == []
        assert result.status == "ok"

    def test_registration_in_fleet_errors(self):
        data = _load("curated/registration_in_fleet.json")
        result = lint_curated_file(data, path="registration_in_fleet.json")
        assert "REGISTRATION_AS_FLEET" in _codes(result, "error")
        assert result.status == "lint_error"

    def test_title_too_long_is_error_once_curated(self):
        raw = _load("raw/title_too_long.json")
        curated = {
            "date": "2026-09-06",
            "weekOf": "2026-08-31",
            "findings": {"keyChanges": raw["keyChanges"], "metrics": {}},
            "metadata": {},
        }
        result = lint_curated_file(curated, path="title_too_long_curated.json")
        assert "TITLE_TOO_LONG" in _codes(result, "error")


class TestRunLedger:
    def test_write_logs_merges_stages(self, tmp_path: Path):
        raw = _lint_raw("raw/good_paid_rides.json")
        curated_data = _load("curated/good_minimal.json")
        curated = lint_curated_file(curated_data, path="good_minimal.json")

        write_quality_logs(
            "2026-09-06",
            raw_results=[raw],
            week_of="2026-08-31",
            out_dir=tmp_path,
        )
        write_quality_logs(
            "2026-09-06",
            curated_result=curated,
            curated_data=curated_data,
            week_of="2026-08-31",
            out_dir=tmp_path,
        )

        ledger = json.loads((tmp_path / "run.json").read_text())
        assert ledger["date"] == "2026-09-06"
        assert ledger["weekOf"] == "2026-08-31"
        assert ledger["stage"] == "curated"
        assert ledger["agents"]["cybercab"]["status"] == "ok"
        assert ledger["agents"]["cybercab"]["filed"] == 1
        assert ledger["agents"]["cybercab"]["queries"] >= 1
        assert ledger["curator"]["accepted"] == 1
        assert (tmp_path / "lint-raw.json").exists()
        assert (tmp_path / "lint-curated.json").exists()
        assert (tmp_path / "cybercab.json").exists()
        search = json.loads((tmp_path / "cybercab.json").read_text())
        assert search["searchLog"]["queries"]

    def test_build_run_ledger_records_lint_errors(self):
        raw = _lint_raw("raw/sep6_registration_as_fleet.json")
        ledger = build_run_ledger(
            date="2026-09-06",
            week_of="2026-08-31",
            raw_results=[raw],
        )
        assert ledger["agents"]["cybercab"]["status"] == "lint_error"
        assert "REGISTRATION_AS_FLEET" in ledger["agents"]["cybercab"]["errorCodes"]
        assert ledger["lint"]["rawErrors"] >= 2
