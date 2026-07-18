#!/usr/bin/env python3
"""
Canonical paths for the Tesla Research repo.

All scripts should import from here so layout changes stay in one place.

Layout:
  data/                 live tracking data + year archives
  research/configs/     generated research-config-*.json, curator-config.json
  research/raw/         per-category findings-{category}.json (pipeline stage)
  research/findings/    curated findings/YYYY-MM-DD.json, reports, url-cache, schema
  scripts/              pipeline tooling
  docs/                 architecture & design notes
  src/                  React dashboard
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Dashboard source of truth
DATA_DIR = ROOT / "data"
TRACKING_DATA = DATA_DIR / "tesla-tracking-data.json"
ARCHIVES_DIR = DATA_DIR / "archives"

# Research pipeline
RESEARCH_DIR = ROOT / "research"
CONFIGS_DIR = RESEARCH_DIR / "configs"
RAW_DIR = RESEARCH_DIR / "raw"
FINDINGS_DIR = RESEARCH_DIR / "findings"
URL_CACHE = FINDINGS_DIR / "url-cache.json"
FINDINGS_SCHEMA = FINDINGS_DIR / "schema.json"

# Docs
DOCS_DIR = ROOT / "docs"

# Scripts
SCRIPTS_DIR = ROOT / "scripts"


def ensure_research_dirs() -> None:
    """Create research subdirs if missing."""
    for d in (CONFIGS_DIR, RAW_DIR, FINDINGS_DIR, DATA_DIR, ARCHIVES_DIR):
        d.mkdir(parents=True, exist_ok=True)


def research_config_path(category_key: str) -> Path:
    return CONFIGS_DIR / f"research-config-{category_key}.json"


def raw_findings_path(category_key: str) -> Path:
    return RAW_DIR / f"findings-{category_key}.json"


def curated_findings_path(date: str) -> Path:
    return FINDINGS_DIR / f"{date}.json"


def curator_report_path(date: str) -> Path:
    return FINDINGS_DIR / f"curator-report-{date}.md"


def curator_config_path() -> Path:
    return CONFIGS_DIR / "curator-config.json"
