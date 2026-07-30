#!/usr/bin/env bash
HARNESS_RUNTIME_TIMEOUT_SECONDS="${HARNESS_RUNTIME_TIMEOUT_SECONDS:-120}"
HARNESS_COMMAND_TIMEOUT_SECONDS="${HARNESS_COMMAND_TIMEOUT_SECONDS:-300}"
HARNESS_KILL_GRACE_SECONDS="${HARNESS_KILL_GRACE_SECONDS:-5}"
HARNESS_FAILURE_TAIL_LINES="${HARNESS_FAILURE_TAIL_LINES:-120}"
HARNESS_MAX_OUTPUT_BUFFER_BYTES="${HARNESS_MAX_OUTPUT_BUFFER_BYTES:-262144}"
harness_python() {
  local candidate
  for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then printf '%s\n' "$candidate"; return 0; fi
  done
  echo "FAIL Harness requires Python 3.10 or newer" >&2; return 2
}
harness_run() {
  local label="$1" timeout="$2" python
  shift 2
  if [ -n "${HARNESS_PYTHON:-}" ]; then python="$HARNESS_PYTHON"; else python="$(harness_python)" || return $?; fi
  "$python" -B scripts/safe_exec.py --label "$label" --timeout "$timeout" --grace "$HARNESS_KILL_GRACE_SECONDS" --tail-lines "$HARNESS_FAILURE_TAIL_LINES" --max-buffer-bytes "$HARNESS_MAX_OUTPUT_BUFFER_BYTES" -- "$@"
}
