#!/usr/bin/env bash
# Point this clone at repo-managed hooks under .githooks/
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

git config core.hooksPath .githooks
chmod +x .githooks/pre-commit 2>/dev/null || true

echo "✓ git core.hooksPath → .githooks"
echo "  pre-commit will run: validate_data.py + pytest (if installed)"
echo "  Bypass: git commit --no-verify"
