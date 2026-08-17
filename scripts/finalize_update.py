#!/usr/bin/env python3
"""
Post-research finalization pipeline.

Chains all steps that follow curator output into a single command:
  merge → url-cache → archive → python-validate → zod-validate → build

Usage:
    python3 scripts/finalize_update.py research/findings/YYYY-MM-DD.json
    python3 scripts/finalize_update.py research/findings/YYYY-MM-DD.json --skip-build
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(label: str, cmd: list[str], **kwargs) -> None:
    print(f"\n→ {label}")
    result = subprocess.run(cmd, cwd=ROOT, **kwargs)
    if result.returncode != 0:
        print(f"\n✗ {label} failed (exit {result.returncode})")
        sys.exit(result.returncode)
    print(f"✓ {label}")


def main() -> None:
    args = sys.argv[1:]
    skip_build = "--skip-build" in args
    findings_args = [a for a in args if not a.startswith("--")]

    if not findings_args:
        print("Usage: python3 scripts/finalize_update.py research/findings/YYYY-MM-DD.json")
        sys.exit(1)

    findings_file = findings_args[0]

    if not Path(ROOT / findings_file).exists():
        print(f"✗ Findings file not found: {findings_file}")
        sys.exit(1)

    run("merge findings", ["python3", "scripts/merge_findings.py", findings_file])
    run("update url cache", ["python3", "scripts/update_url_cache.py", findings_file])
    run("archive old data", ["python3", "scripts/archive_old_data.py"])
    run("python validate", ["python3", "scripts/validate_data.py"])
    run("zod validate", ["npx", "tsx", "scripts/validate-zod-schema.ts"])

    if not skip_build:
        run("npm build", ["npm", "run", "build"])

    print("\n✅ Finalization complete.")
    print(f"   Findings: {findings_file}")
    if skip_build:
        print("   (build skipped — run `npm run build` separately)")


if __name__ == "__main__":
    main()
