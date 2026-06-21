# Context and Written Memory

## Objective

Prevent context loss by turning important findings, assumptions, decisions, and handoff notes into concise repository documentation.

## When to use

- Any Level 2 or Level 3 task.
- Any task that spans multiple sessions or tools.
- Any task where the agent says or implies it will “remember” something.
- Any task with business rules, integration contracts, architecture decisions, or shared files.

## Process

1. Identify what future agents must know.
2. Decide the correct written location:
   - `project-profile.md` for project identity, stack, architecture, paths.
   - `commands.md` for verified commands.
   - `conventions.md` for recurring implementation patterns.
   - `risks.md` for durable risks.
   - `shared-context.md` for cross-tool/session context.
   - `decision-log.md` for durable decisions.
   - `docs/ai/tasks/` for task-specific plans and handoffs.
3. Write concise facts, not generic filler.
4. Mark unknowns explicitly.
5. Update handoff notes after changes.

## Hard rule

Do not store important information only mentally, in hidden reasoning, or in chat history.

## Checklist

- [ ] Durable facts written to docs.
- [ ] Open assumptions recorded.
- [ ] Shared files identified.
- [ ] Handoff notes updated.
- [ ] No generic filler added.
