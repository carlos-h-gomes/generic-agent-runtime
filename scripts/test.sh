#!/usr/bin/env bash
set -u -o pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"; source "$ROOT/scripts/common.sh"
PYTHON="$(harness_python)" || exit $?; export HARNESS_PYTHON="$PYTHON"; RUNTIME_TIMEOUT="$HARNESS_RUNTIME_TIMEOUT_SECONDS"; status=0
harness_run "Harness functional tests" "$RUNTIME_TIMEOUT" "$PYTHON" -B scripts/test_runtime.py || status=$?
if [ "$status" -eq 0 ]; then CI=1 "$PYTHON" -B scripts/project_checks.py test || status=$?; fi
exit "$status"
