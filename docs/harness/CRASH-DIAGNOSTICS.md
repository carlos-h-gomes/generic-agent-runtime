# Codex Crash Isolation

Use this procedure when the Codex application exits, restarts, or becomes unresponsive rather than merely returning a poor result.

## Controlled A/B test

1. Reproduce the task in a disposable copy of the repository with Harness 4.2 enabled.
2. Repeat the same task in another disposable copy with root `AGENTS.md` and `.agents/skills` temporarily moved outside the repository.
3. Keep the Codex version, model, repository revision, task prompt, and machine state the same.
4. Record whether the crash occurs before any command, while a specific command runs, or while the application renders tool output/diffs.

Interpretation:

- crash only with the Harness, before commands: investigate instruction/context pressure or skill discovery;
- crash only while a project command runs: inspect that command, child processes, memory use, and output volume;
- crash in both cases: prioritize Codex application, extension, operating-system, driver, or repository-level causes;
- no crash after 4.2: compare the 4.1 runtime and host evidence before attributing a native root cause. Harness 4.2 specifically removes the destructive Windows PID probe present in 4.0 and 4.1.

## Evidence to preserve

Preserve the approximate timestamp with timezone, Codex version, operating system, repository revision, task prompt, last visible tool/command, exit code when available, and a bounded redacted log excerpt. Do not store secrets, full customer payloads, private prompts, or unrestricted crash dumps in project memory.
