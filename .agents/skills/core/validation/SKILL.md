---
name: validation
description: "Validate an authorized change with the smallest relevant evidence set, bounded commands, honest skips, and no automatic repeated failures."
---

# Validation

Validation certifies the task outcome; it does not redesign the solution or rerun every possible command.

## Procedure

1. Read the request or managed task contract, current diff/state, applicable specialist results, and verified commands.
2. Map each acceptance criterion to a code/config/document pointer, automated command, or explicit manual check.
3. Run the smallest relevant test, lint, typecheck, build, security, UI, integration, adversarial-plan, and package checks in risk order. Inspect project commands before granting explicit trust.
4. Record command, environment or revision/state, exit code, and a bounded result. A trusted zero exit code is sufficient evidence unless output is filtered, truncated, suspicious, or the command itself has weak coverage.
5. On failure, preserve a redacted actionable excerpt and controlled full-artifact pointer/hash. Never paste secrets, raw customer data, private prompts, or full terminal logs into project memory.
6. Classify unavailable applicable checks as `INCOMPLETE` and absent triggers as `NOT_APPLICABLE`; neither is proof that behavior passed. Record a typed gap as out of scope, blocked, or accepted residual risk; accepted residual risk needs a scoped human reference.
7. Confirm triggered gate results are fresh and no blocking condition or unapproved external action remains.

Allow at most two implementation/validation attempts by default, including the initial run. Never repeat the same failure without a change or new evidence; then stop and report the blocker.

## Completion rule

Use `done` only when all acceptance criteria are met or every unvalidated portion is explicitly accepted by the task's authorization model. A green generic script that found no applicable checks is a skip, not proof of behavior.

Return acceptance-criterion status, commands and exit codes, manual checks, skipped areas, gate/approval state, residual risks, and handoff.
