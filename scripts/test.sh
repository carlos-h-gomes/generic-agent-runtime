#!/usr/bin/env bash
set -euo pipefail

if [ -f package.json ] && command -v npm >/dev/null 2>&1; then
  npm test --if-present
fi

if command -v pytest >/dev/null 2>&1; then
  pytest
fi
