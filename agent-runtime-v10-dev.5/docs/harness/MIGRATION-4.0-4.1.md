# Migrating Harness 4.0 to 4.1

Harness 4.1 is a stability and proportional-governance release. It preserves the schemas, bridge, specialist reviews, project memory, and validation capabilities of 4.0 while removing automatic ceremony from ordinary work.

## Main changes

- Replace the 4.0 `AGENTS.md` with the 4.1 kernel. It is intentionally below 8 KiB.
- Keep fast-path Level 0/1 work inline; create task contracts only for Level 2/3, multi-session, multi-writer, high-risk, or explicitly governed tasks.
- Specialist skills are explicit-only by default through `agents/openai.yaml`. `implementation`, `project-profiling`, and `validation` remain eligible for implicit selection.
- Use `scripts/safe_exec.py` for bounded child processes. Timeouts terminate the process group and failure output is limited to a useful tail.
- `scripts/project_checks.py` provides the same project checks on POSIX and Windows.
- Standard validation runs lint and tests. `validate --full` additionally runs build and security checks.
- Validation defaults to two attempts and never repeats the same failure without a change or new evidence.
- The bridge is used only for actual concurrent shared writers.

## Installation

Do not extract over an active repository. Stage the archive, verify `MANIFEST.sha256`, run the runtime checks, then merge deliberately. Preserve project-specific instructions, verified commands, active task state, decisions, and bridge history.

## Compatibility

Task contract v1, GateResult v1, and bridge event v2 are unchanged. Existing 4.0 contracts and ledgers remain readable. The change is primarily when those mechanisms are invoked, not their on-disk format.
