#!/usr/bin/env bash
# Run before pushing and after merging: same checks as GitHub CI.
set -u
cd "$(dirname "$0")/.."
PY=".venv/bin/python"; [ -x "$PY" ] || PY=python3
status=0
step() { echo; echo "── $1"; }
step "git: branch and sync"; git fetch -q && git status -sb | head -1
step "python tests"; $PY -m pytest -q tests || status=1
step "frontend types"; (cd web && npx tsc --noEmit && echo "tsc ok") || status=1
echo; [ $status -eq 0 ] && echo "✅ checks green" || echo "❌ something failed"
exit $status
