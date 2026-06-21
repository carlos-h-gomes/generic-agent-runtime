# Documentation

## Objective

Document durable project knowledge without creating noise.

## When to use

- Architecture decision.
- New integration.
- New endpoint/contract.
- New data model/migration.
- New operational workflow.
- New cost/security/compliance risk.
- Level 2 or 3 task that future agents must understand.
- Cross-tool handoff or shared-file coordination.

## When not to use

- Trivial local changes.
- Cosmetic-only edits.
- Temporary notes that will not matter after the task.

## Process

1. Decide whether documentation is genuinely needed.
2. Prefer updating existing docs over creating new docs.
3. Keep docs factual and concise.
4. Put task-specific planning in `docs/ai/tasks/`.
5. Put durable decisions in `docs/ai/decision-log.md`.
6. Put cross-tool context in `docs/ai/shared-context.md`.
7. Remove stale or contradictory notes when updating.

## Quality criteria

- Useful in future sessions.
- No generic filler.
- Easy to scan.
- Accurate and current.
- Enough context exists for another agent to continue safely.

## Checklist

- [ ] Documentation need justified.
- [ ] Correct file updated.
- [ ] Decision log updated if needed.
- [ ] Shared context updated if needed.
- [ ] No duplicate boilerplate.
