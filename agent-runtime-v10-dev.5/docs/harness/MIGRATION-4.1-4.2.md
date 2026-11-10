# Migrating Harness 4.1 to 4.2

Harness 4.2 is a Windows crash-safety and validation-adapter release. Contract versions and project memory formats are unchanged.

## Required procedure

1. Stage `agent-runtime-v4.2.zip` in a new directory; do not extract directly over an active repository.
2. Verify `MANIFEST.sha256` and run `python -B scripts/runtime_check.py --static --strict` in the staged copy.
3. Merge the kernel, runtime scripts, tests, skills, schemas and Harness documentation deliberately.
4. Preserve project-specific `docs/ai`, active tasks, bridge ledger, verified commands and product validation adapters.
5. On Windows, confirm `scripts/bridge.py` routes process liveness through the query-only Win32 probe before running bridge tests.
6. Run the targeted Windows regressions, the complete runtime suite and the project's bounded validation commands.

## Corrections in 4.2

- Windows process liveness no longer calls `os.kill(pid, 0)`. Unknown query errors fail closed by treating the lock owner as potentially alive.
- PowerShell passes Bash script paths with `/`, avoiding backslash escaping on Git Bash.
- npm discovery supports root and immediate-child packages and resolves `.cmd` executables on Windows.

## Rollback

No data migration exists. Restore the previously verified 4.1 runtime files while retaining project `docs/ai` and bridge state. Never restore the unsafe 4.1 `bridge.py` over a Windows-safe local correction.
