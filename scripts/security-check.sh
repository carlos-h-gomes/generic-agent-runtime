#!/usr/bin/env bash
set -u -o pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"; source "$ROOT/scripts/common.sh"
PYTHON="$(harness_python)" || exit $?; export HARNESS_PYTHON="$PYTHON"; CI=1 "$PYTHON" -B scripts/project_checks.py security
