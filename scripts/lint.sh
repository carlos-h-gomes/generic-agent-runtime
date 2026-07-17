#!/usr/bin/env bash
set -u -o pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"; source "$ROOT/scripts/common.sh"
PYTHON="$(harness_python)" || exit $?; export HARNESS_PYTHON="$PYTHON"; RUNTIME_TIMEOUT="$HARNESS_RUNTIME_TIMEOUT_SECONDS"; status=0
bash -n scripts/*.sh || status=$?
if [ "$status" -eq 0 ]; then harness_run "Harness structural lint" "$RUNTIME_TIMEOUT" "$PYTHON" -B scripts/runtime_check.py --static || status=$?; fi
if [ "$status" -eq 0 ] && command -v powershell.exe >/dev/null 2>&1; then
  harness_run "PowerShell parser" "$RUNTIME_TIMEOUT" powershell.exe -NoProfile -NonInteractive -Command '$errors=@(); foreach($path in @("scripts/run.ps1","scripts/bridge.ps1")){ $tokens=$null; $found=$null; [void][System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path $path),[ref]$tokens,[ref]$found); $errors+=$found }; if($errors.Count){$errors|ForEach-Object{[Console]::Error.WriteLine($_.Message)}; exit 1}' || status=$?
fi
if [ "$status" -eq 0 ]; then CI=1 "$PYTHON" -B scripts/project_checks.py lint || status=$?; fi
exit "$status"
