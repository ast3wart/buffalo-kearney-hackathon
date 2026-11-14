#!/usr/bin/env bash
# Run at the start of every checkpoint. Both people run it on the merged main.
#   ./scripts/checkpoint.sh          (uses data/generated/ if present, else data/sample/)
set -u
cd "$(dirname "$0")/.."
PY=".venv/bin/python"; [ -x "$PY" ] || PY=python3
status=0
step() { echo; echo "── $1"; }
step "git: on main and up to date?"; git fetch -q && git status -sb | head -1
step "data contract + cross-thread consistency"; $PY -m afterlife.check || status=1
step "pipeline run"; $PY -m afterlife.run || status=1
step "python tests"; $PY -m pytest -q tests || status=1
step "frontend types"; (cd web && npx tsc --noEmit && echo "tsc ok") || status=1
step "accuracy (if built)"; $PY -m afterlife.evaluate 2>&1 | tail -15 || true
echo; [ $status -eq 0 ] && echo "✅ checkpoint checks green" || echo "❌ something failed, fix this before reviewing features"
exit $status
