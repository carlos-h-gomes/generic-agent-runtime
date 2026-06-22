---
name: context-memory
description: "Curate durable written project memory so context is never lost between sessions, tools or context resets. Use on any Level 2/3 task, any multi-session/multi-tool work, anything with business rules, integration contracts, architecture decisions or shared files, or whenever project memory files are growing stale, contradictory or bloated. Decides what to write, where (docs/ai/*), and prunes superseded notes."
---

# Context and Written Memory

## Objective

Prevent context loss by turning important findings, assumptions, decisions, and handoff notes into concise repository documentation.

This skill is a context curator. It must keep the working memory useful, lean, and durable without letting project files grow into noisy chat transcripts.

## When to use

- Any Level 2 or Level 3 task.
- Any task that spans multiple sessions or tools.
- Any task where the agent says or implies it will “remember” something.
- Any task with business rules, integration contracts, architecture decisions, or shared files.
- Any task where project memory files are becoming too long, stale, contradictory, or expensive to load.

## Process

1. Identify what future agents must know.
2. Separate durable knowledge from temporary execution noise.
3. Decide the correct written location:
   - `constitution.md` for durable, rarely-changing principles and hard constraints.
   - `project-profile.md` for project identity, stack, architecture, paths.
   - `commands.md` for verified commands.
   - `conventions.md` for recurring implementation patterns.
   - `risks.md` for durable risks.
   - `shared-context.md` for cross-tool/session context.
   - `decision-log.md` for durable decisions and reusable lessons learned.
   - `docs/ai/tasks/` for task-specific plans and handoffs.
4. Write concise facts, not generic filler.
5. Mark unknowns explicitly.
6. Append durable decisions to `decision-log.md` instead of burying them in chat or bloating `project-profile.md`.
7. Compact or remove stale project-memory rules only when they are explicitly superseded by newer repository evidence, user instruction, or decision-log entry.
8. When removing or replacing stale memory, record the replacement decision in `decision-log.md` or the active task file.
9. Update handoff notes after changes.

## Durable decision examples

Record decisions such as:

- “Rendering moved to `MainHeader` because requirement X needs a single shared header boundary.”
- “Webhook retries use idempotency key Y to avoid duplicate processing.”
- “The project moved from framework A to framework B because deployment constraint Z made A unsuitable.”
- “Architecture artifact X supersedes older flow Y.”

Do not record temporary noise such as:

- Every command attempted during exploration.
- Full terminal logs unless the log is needed for a handoff.
- Generic best practices.
- Repeated summaries that duplicate existing docs.
- Personal chat phrasing that does not change the project.

## Memory pruning rules

`docs/ai/project-profile.md` must stay concise. It should describe the project as it is now, not every historical path that was tried.

When a rule, path, command, architecture note, or integration contract is outdated:

1. Confirm it is superseded by a newer source.
2. Replace it with the current fact.
3. Keep only the durable reason in `decision-log.md` when the historical reason matters.
4. If unsure, do not delete. Mark it as `Needs verification` with a short reason.

## Hard rule

Do not store important information only mentally, in hidden reasoning, or in chat history.

If a future agent must rely on it, write it to the repository.

## Checklist

- [ ] Durable facts written to docs.
- [ ] Temporary execution noise excluded.
- [ ] Open assumptions recorded.
- [ ] Durable decisions appended to `decision-log.md`.
- [ ] Superseded rules removed or marked with reason.
- [ ] `project-profile.md` kept lean.
- [ ] Shared files identified.
- [ ] Handoff notes updated.
- [ ] No generic filler added.
