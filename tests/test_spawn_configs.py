"""Tests for slim research/curator config hot context."""

from spawn_researcher import (
    SLIM_KEY_CHANGE_FIELDS,
    all_seen_urls,
    load_hot_context,
    slim_key_change,
    slim_metric_point,
    urls_for_category,
)


FAT_KEY_CHANGE = {
    "title": "Nevada grants Las Vegas robotaxi permit capped at 10 vehicles",
    "description": "A long essay that must not land in the researcher config.",
    "date": "2026-08-14",
    "category": "Cybercab Production",
    "status": "negative",
    "sentiment": {
        "headline": "neutral",
        "reality": "negative",
        "confidence": "high",
        "rationale": "Permit was a cap, not a launch.",
    },
    "evidence": {
        "positive_signals": ["Got a permit"],
        "negative_signals": ["Capped at 10"],
        "key_metrics": {"actual": "10", "target": "5000", "trajectory": "stuck"},
    },
    "source": "https://www.axios.com/2026/08/14/tesla-robotaxi-vegas",
    "impact": "high",
}


def test_slim_key_change_drops_essays():
    slim = slim_key_change(FAT_KEY_CHANGE)
    assert set(slim) <= set(SLIM_KEY_CHANGE_FIELDS)
    assert "description" not in slim
    assert "evidence" not in slim
    assert "sentiment" not in slim
    assert slim["title"] == FAT_KEY_CHANGE["title"]
    assert slim["source"] == FAT_KEY_CHANGE["source"]


def test_slim_metric_point_truncates_note():
    point = slim_metric_point(
        {"date": "2026-08-22", "count": 5030, "note": "n" * 500, "breakdown": {"x": 1}}
    )
    assert point["count"] == 5030
    assert len(point["note"]) == 240
    assert point["note"].endswith("...")
    assert "breakdown" not in point


def test_urls_for_category_filters_and_adds_original():
    cache = {
        "https://example.com/cybercab-a": {
            "originalUrl": "https://example.com/cybercab-a/",
            "category": "Cybercab Production",
        },
        "https://example.com/fsd-a": {
            "originalUrl": "https://example.com/fsd-a/",
            "category": "FSD Country Approvals",
        },
        "https://example.com/unknown": {
            "originalUrl": "https://example.com/unknown/",
            "category": "unknown",
        },
    }
    urls = urls_for_category("cybercab", cache_urls=cache, extra_urls=["https://extra.example/last-week"])
    assert "https://example.com/cybercab-a" in urls
    assert "https://example.com/cybercab-a/" in urls
    assert "https://extra.example/last-week" in urls
    assert "https://example.com/fsd-a" not in urls
    assert "https://example.com/unknown" not in urls


def test_terafab_alias_matches_old_cache_label():
    cache = {
        "https://example.com/terafab-old": {
            "originalUrl": "https://example.com/terafab-old/",
            "category": "Terafab Manufacturing",
        }
    }
    urls = urls_for_category("terafab", cache_urls=cache)
    assert "https://example.com/terafab-old" in urls


def test_all_seen_urls_is_flat_list():
    cache = {
        "https://example.com/a": {"originalUrl": "https://example.com/a/", "category": "Research"},
        "https://example.com/b": {"originalUrl": "https://example.com/b", "category": "Cybercab Production"},
    }
    urls = all_seen_urls(cache)
    assert "https://example.com/a" in urls
    assert "https://example.com/a/" in urls
    assert "https://example.com/b" in urls


def test_load_hot_context_is_slim_and_does_not_mix_fsd_with_fsdv15():
    data = {
        "categories": {
            "fsd": {"criticalNews": "Korea origin-split"},
            "fsdv15": {"criticalNews": "v15 stall"},
        },
        "weeklySummaries": [
            {
                "weekOf": "2026-08-17",
                "keyChanges": [
                    {**FAT_KEY_CHANGE, "title": "Korea blocked", "category": "FSD Country Approvals",
                     "source": "https://example.com/korea"},
                    {
                        "title": "v15 still 40 percent of tracks",
                        "description": "Must not leak into fsd config",
                        "date": "2026-08-20",
                        "category": "FSD v15 Software",
                        "status": "negative",
                        "source": "https://example.com/v15",
                        "evidence": {"positive_signals": ["x"], "negative_signals": ["y"]},
                    },
                ],
            }
        ],
        "metrics": {},
    }
    fsd = load_hot_context("fsd", data=data, cache_urls={})
    titles = [kc["title"] for kc in fsd["recentKeyChanges"]]
    assert titles == ["Korea blocked"]
    assert "description" not in fsd["recentKeyChanges"][0]
    assert "evidence" not in fsd["recentKeyChanges"][0]
    assert "https://example.com/korea" in fsd["seenUrls"]
    assert "https://example.com/v15" not in fsd["seenUrls"]

    fsdv15 = load_hot_context("fsdv15", data=data, cache_urls={})
    assert [kc["title"] for kc in fsdv15["recentKeyChanges"]] == ["v15 still 40 percent of tracks"]
