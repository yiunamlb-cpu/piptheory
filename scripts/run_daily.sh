#!/usr/bin/env bash
# piptheory daily bias engine run (Linux / Render).
#
# This script:
#   1. Sets working directory to the project root (CWD when spawned)
#   2. Sets PYTHONPATH so src/ is importable
#   3. Runs the bias engine
#   4. Appends stdout+stderr to logs/bias_engine.log with a timestamped header
#
# The dashboard reads bias_cards/{date}/ output, so once this finishes the
# next time the dashboard auto-reruns it'll show the fresh brief.

set -e
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

export PYTHONPATH="$REPO"
export PYTHONIOENCODING=utf-8

mkdir -p logs

{
  echo ""
  echo "================================================================"
  echo "Run started $(date '+%Y-%m-%d %H:%M:%S')"
  echo "================================================================"
} >> logs/bias_engine.log

python3 scripts/run_bias_engine.py >> logs/bias_engine.log 2>&1

{
  echo ""
  echo "Run finished $(date '+%Y-%m-%d %H:%M:%S') (exit $?)"
} >> logs/bias_engine.log
