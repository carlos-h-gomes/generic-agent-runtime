---
name: minimalism
description: "Size the solution down to the minimum code that satisfies the acceptance criteria, before and during implementation, without ever cutting validation, security, accessibility or data-loss handling. Use on any code-writing task (Level 1+) as a YAGNI / anti-over-engineering lens: stop at the first rung that solves the need (skip it -> stdlib -> native platform -> existing dependency -> one line -> minimum that works), and as a delete-list review of a diff or repo for over-engineering. Sizes solution code only; never weakens runtime gates, written-memory or approval boundaries."
---

# Minimalism (YAGNI ladder)

## Objective

Write only the code the task needs. The smallest correct solution, not the cleverest or the most complete one. Reduce lines, dependencies, and surface area — without ever reducing safety.

Adapted from the ponytail project (DietrichGebert/ponytail, MIT): the best code is the code you never wrote.

## When to use

- Any task that writes or changes code or config (Level 1 and up).
- As a scoping lens inside `core/task-triage` (rung 1 below).
- As a delete-list review inside `specialists/code-quality-testing`.
- Not for sizing the governance process itself — see Scope boundary.

## The ladder

Before writing code, stop at the first rung that holds:

```text
1. Does this need to exist?        -> no: don't build it (YAGNI)
2. Does the stdlib/framework do it? -> use it
3. Native platform feature?         -> use it  (e.g. <input type="date"> over a date-picker component)
4. Already-installed dependency?    -> use it; don't add a new one
5. Fits in one line?                -> one line
6. Only then:                        the minimum that works
```

Prefer the lowest rung that works, and existing patterns over new abstractions.

## Non-negotiable floor

Lazy, not negligent. The ladder never removes:

- Trust-boundary / external-input validation.
- Data-loss and failure handling.
- Security and least-privilege.
- Accessibility.

These are required by `docs/ai/constitution.md` and the security/UX gates; minimalism never overrides them. If a "minimal" version drops one of these, it is not minimal — it is broken.

## Scope boundary

Minimalism sizes **solution code**. It does **not** size the runtime's own process. It is never a reason to skip a triggered gate, a task file, written memory, a validation command, or a human-approval boundary. The "does this need to exist?" question applies to product/solution artifacts, not to governance controls. When in doubt, the source-of-truth hierarchy and the preservation rule in `AGENTS.md` win.

## Process

1. At triage: apply rung 1 to the request's scope; drop or defer anything the acceptance criteria do not require.
2. At implementation: walk the ladder for each new unit of code; prefer existing patterns over new abstractions.
3. Justify any new dependency or new abstraction against the ladder; if a lower rung covers it, use the lower rung.
4. Tag intentional shortcuts with a `minimal:` (or `ponytail:`) marker plus a reason, so deferred work is harvestable, not lost.
5. At code-quality review: scan the diff (or the repo, for an explicit audit) and produce a delete-list of code that exists but is not needed.
6. Keep the floor intact at every step.

## Review mode (delete-list)

On request (a "minimalism review" of the diff, or an "over-engineering audit" of the repo), output:

- what can be deleted or collapsed, and which rung it failed;
- what must stay (floor items, justified complexity);
- the net reduction — without touching validation, security, accessibility, or data-loss handling.

The output is a list of safe reductions, not code.

## Quality criteria

- Every retained unit of code maps to an acceptance criterion or a floor requirement.
- No re-implementation of stdlib / native / existing-dependency behavior.
- No new dependency where a lower rung suffices.
- No speculative generality ("might need it later").
- Safety floor fully intact.

## Checklist

- [ ] Rung 1 applied to scope (does it need to exist?).
- [ ] Ladder walked before new code/abstraction/dependency.
- [ ] Existing patterns preferred over new abstractions.
- [ ] Validation / security / accessibility / data-loss handling preserved.
- [ ] Governance gates and approval boundaries untouched.
- [ ] Intentional shortcuts tagged with a reason.
- [ ] Delete-list produced when reviewing.
