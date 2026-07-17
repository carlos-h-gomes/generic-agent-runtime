#!/usr/bin/env bash
set -u -o pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"; source "$ROOT/scripts/common.sh"
PYTHON="$(harness_python)" || exit $?; export HARNESS_PYTHON="$PYTHON"; full=0; [ "${1:-}" = "--full" ] && full=1; status=0; incomplete=0
run_stage(){ "$@"; local code=$?; if [ "$code" -eq 3 ]; then incomplete=1; return 0; fi; if [ "$code" -ne 0 ]; then status="$code"; return "$code"; fi; }
run_stage bash scripts/lint.sh || exit "$status"
run_stage bash scripts/test.sh || exit "$status"
if [ -d scaffold ] && [ -f scripts/package_runtime.py ]; then
 timeout="$HARNESS_RUNTIME_TIMEOUT_SECONDS"; harness_run "strict runtime validation" "$timeout" "$PYTHON" -B scripts/runtime_check.py --strict || exit $?; harness_run "deterministic package validation" "$timeout" "$PYTHON" -B scripts/package_runtime.py --check || exit $?
fi
if [ "$full" -eq 1 ]; then run_stage "$PYTHON" -B scripts/project_checks.py build || exit "$status"; run_stage "$PYTHON" -B scripts/project_checks.py security || exit "$status"; fi
if [ "$incomplete" -ne 0 ]; then echo "INCOMPLETE validation: one or more applicable checks were unavailable"; exit 3; fi
echo "PASS validation completed ($([ "$full" -eq 1 ] && echo full || echo standard))"
