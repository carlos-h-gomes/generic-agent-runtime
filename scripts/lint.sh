#!/usr/bin/env bash
set -euo pipefail

ran_any=false

echo "[Lint] Detecting available lint/typecheck commands..."

if [ -f package.json ] && command -v npm >/dev/null 2>&1; then
  echo "==> Running Node.js lint/typecheck when scripts are defined"
  npm run lint --if-present
  npm run typecheck --if-present
  ran_any=true
fi

if { [ -f pyproject.toml ] || [ -f requirements.txt ] || [ -f setup.py ] || [ -f setup.cfg ]; } && command -v ruff >/dev/null 2>&1; then
  echo "==> Running Python lint with Ruff"
  ruff check .
  ran_any=true
fi

if [ "$ran_any" = false ]; then
  echo "[Lint] No supported lint/typecheck command detected. Record this as 'not validated' unless manual checks were performed."
fi
