---
name: validation
description: "Prove a change actually works or honestly state what could not be validated, with depth proportional to task risk. Use on every task to run the smallest relevant set of project validation commands, add UI/integration/data/rollback checks when relevant, and report only validations that genuinely ran. Never claims validation passed unless it did."
---

# Validation

## Objective

Prove the change works, or honestly state what could not be validated.

## When to use

- Every task, with depth proportional to risk.

## Inputs expected

- `docs/ai/commands.md`.
- Changed files.
- Acceptance criteria.
- Triggered gates.
- Risk notes.

## Process

1. Identify available validation commands from `docs/ai/commands.md` or project files.
2. Run the smallest relevant set.
3. For UI changes, include responsive/accessibility/state checks.
4. For integrations, include payload, timeout, retry, idempotency, and error checks.
5. For data changes, include schema and migration safety checks.
6. For critical changes, include rollback and monitoring checks.
7. Report only validations actually performed.
8. Record unvalidated areas in the task file for Level 2/3.

## Quality criteria

- No fake validation claims.
- Failed validation is surfaced clearly.
- Manual validation is specific enough to execute.
- Residual risk is stated.

## Checklist

- [ ] Relevant commands identified.
- [ ] Commands run or reason documented.
- [ ] Manual checks documented if needed.
- [ ] Failures reported.
- [ ] Remaining risks stated.
