---
name: code-quality-testing
description: "Improve correctness, maintainability and regression safety, and own the autonomous implementation/testing reflection loop after code changes. Use for business-logic changes, shared utilities, refactors, edge-case-heavy code, new validation rules, or any task whose plan includes ./scripts/test.sh or ./scripts/lint.sh. Runs validation, returns exact failure output to implementation, and retries up to the configured attempt limit before pausing for human review."
---

# Code Quality and Testing Specialist

## Objective

Improve correctness, maintainability, and regression safety while avoiding unnecessary complexity.

This specialist owns the autonomous quality reflection loop after implementation.

## When to use

- Business logic changes.
- Shared utilities.
- Refactors.
- Edge-case-heavy code.
- New validation rules.
- Bug fixes that need regression coverage.
- Any task whose validation plan includes `./scripts/test.sh`, `./scripts/lint.sh`, or equivalent project commands.

## Inputs expected

- Structured task specification from `core/task-triage`.
- Acceptance criteria.
- Existing test patterns.
- Changed files.
- Edge cases.
- Validation commands.
- Current attempt number.
- Previous terminal output from failed attempts, when applicable.

## Process

1. Identify behavior under change.
2. Identify edge cases and failure modes.
3. Check existing abstractions and patterns.
4. Keep functions/classes focused.
5. Avoid hidden mutable state where practical.
6. Add or update tests at the lowest useful level.
7. Add integration or contract tests when boundaries are involved.
8. Run the smallest relevant validation commands.
9. Prefer the standard quality loop commands when available:
   - `./scripts/test.sh`
   - `./scripts/lint.sh`
10. Capture command, exit code, stdout summary, and stderr/failure output.
11. If validation fails, return the exact actionable failure output to `core/implementation`.
12. Repeat until validation passes or the attempt limit in `docs/ai/quality-gates.md` is reached.
13. If the limit is reached, pause the task and mark it for human review instead of hiding the failure.

## Reflection loop contract

Use this loop for spec-driven implementation work:

```text
1. implementation changes code
2. code-quality-testing runs validation
3. if validation fails, return stderr/output to implementation
4. implementation fixes the failure
5. code-quality-testing reruns validation
6. stop after pass or after the configured maximum attempts
```

The default maximum is 3 attempts unless `docs/ai/quality-gates.md` defines a different value for the project.

When validation runs through an output-compressing proxy (e.g. rtk), the loop must diagnose from the full tee'd failure output, not the compact summary — fixing code against a truncated test view risks chasing the wrong failure. Treat the filtered output as an index, the tee'd file as the source.

## Over-engineering review (delete-list)

As part of the quality pass, scan the changed diff (or the whole repo on an explicit audit) for over-engineering and produce a delete-list: speculative options nobody asked for, premature abstraction, re-implemented standard-library or native-platform behavior, unused parameters, and dependencies a lower rung would cover. For each item, say which rung of the `core/minimalism` ladder it failed and what replaces it. Never propose deleting validation, security, accessibility or data-loss handling — those stay regardless of line count. The output is a list of safe reductions, not code.

## Deliverables

- Code quality review notes.
- Test plan.
- Edge-case list.
- Over-engineering delete-list (safe reductions only).
- Validation outcome.
- Commands run with pass/fail status.
- Failure packet for implementation when validation fails.
- Human review packet when the loop reaches the maximum attempts.

## Failure packet format

When validation fails, return structured feedback:

```json
{
  "quality_status": "failed",
  "attempt": 1,
  "max_attempts": 3,
  "failed_command": "./scripts/test.sh",
  "exit_code": 1,
  "stderr_or_failure_output": "Paste the actionable terminal failure output here.",
  "likely_cause": "Best grounded hypothesis, or unknown.",
  "required_next_action": "Return to core/implementation for correction."
}
```

## Human review packet format

When the loop reaches the maximum attempts:

```json
{
  "quality_status": "paused_for_human_review",
  "attempts_used": 3,
  "reason": "Validation still fails after the configured reflection loop limit.",
  "last_failed_command": "./scripts/test.sh",
  "last_failure_output": "Paste the final actionable terminal output here.",
  "changed_files": ["path/or/file"],
  "recommended_human_review_focus": ["What the human should inspect first."]
}
```

## Quality criteria

- Code is readable and localized.
- Tests protect important behavior.
- Edge cases are covered or documented.
- No unnecessary dependency or abstraction.
- Validation output is preserved honestly.
- Broken code is not sent for human review until the reflection loop has been attempted, unless validation cannot run.

## Written memory rule

For Level 2/3 work, record durable findings, assumptions, risks, validation outcomes, and handoff notes in the active task file or the appropriate `docs/ai` file. Do not rely on mental notes.

## Checklist

- [ ] Behavior identified.
- [ ] Edge cases identified.
- [ ] Over-engineering delete-list produced (safe reductions only).
- [ ] Existing patterns respected.
- [ ] Tests considered/updated.
- [ ] Validation command identified.
- [ ] `./scripts/test.sh` run when available/relevant.
- [ ] `./scripts/lint.sh` run when available/relevant.
- [ ] Failure output returned to implementation when needed.
- [ ] Attempt count respected.
- [ ] Human review packet produced if the loop fails repeatedly.
