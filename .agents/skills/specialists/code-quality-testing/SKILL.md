---
name: code-quality-testing
description: "Explicit specialist review for meaningful logic, shared refactors, edge cases, and regression-sensitive changes."
---

# Code quality and testing gate

Return an implementation-review `GateResult` conforming to `schemas/gate-result.schema.json`. `core/validation` performs final acceptance certification.

## Review and test

1. Read the task contract, changed behavior, current diff/state, relevant conventions, and existing tests.
2. Check correctness, explicit failure handling, boundary cases, compatibility, scope creep, unnecessary concepts/dependencies, and test seams.
3. Prefer the lowest useful test level; add integration, contract, end-to-end, migration, or rollback checks only when the boundary requires them.
4. Use verified project commands for targeted tests, lint, typecheck, and build. Distinguish pre-existing baseline failures from failures introduced by the task.
5. Classify failures: implementation defect, test defect, baseline, flaky, environment/tooling, missing secret/service, or approval boundary.

## Reflection loop

The default limit is two total validation attempts, including the first run:

```text
implement -> attempt 1 -> correct -> attempt 2 -> correct -> attempt 3
```

Stop earlier if the same failure repeats without new evidence, a protected action is required, or correction would expand scope. After the limit, preserve changes and return a human review packet with paths, commands, exit codes, bounded actionable output, attempt history, residual risk, and review focus.

Record command, working state/revision, exit code, and redacted excerpt. Full logs remain in controlled temporary artifacts referenced by pointer/hash only. Never persist secrets, customer data, real payloads, private prompts, or unrestricted logs.

Pass only when all applicable required checks have evidence and no blocker remains. Missing or unavailable checks are `not_verified`, not passed.
