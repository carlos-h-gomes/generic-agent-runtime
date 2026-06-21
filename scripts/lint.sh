#!/usr/bin/env bash
set -euo pipefail

if [ -f package.json ] && command -v npm >/dev/null 2>&1; then
  npm run lint --if-present
  npm run typecheck --if-present
fi

if command -v ruff >/dev/null 2>&1; then
  ruff check .
fi
