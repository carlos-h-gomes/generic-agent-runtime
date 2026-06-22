#!/usr/bin/env bash
set -euo pipefail

ran_any=false

echo "[Test] Detecting available test commands..."

if [ -f package.json ] && command -v npm >/dev/null 2>&1; then
  echo "==> Running Node.js tests when npm test is defined"
  npm test --if-present
  ran_any=true
fi

if { [ -f pyproject.toml ] || [ -f requirements.txt ] || [ -f setup.py ] || [ -f setup.cfg ]; } && command -v pytest >/dev/null 2>&1; then
  if [ -d tests ] || find . -maxdepth 3 \( -name 'test_*.py' -o -name '*_test.py' \) | grep -q .; then
    echo "==> Running Python tests with pytest"
    pytest
    ran_any=true
  else
    echo "[Test] Python project detected, but no pytest test files were found. Skipping pytest."
  fi
fi

if [ "$ran_any" = false ]; then
  echo "[Test] No supported test command detected. Record this as 'not validated' unless manual checks were performed."
fi
