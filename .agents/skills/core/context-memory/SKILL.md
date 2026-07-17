---
name: context-memory
description: "Use for concise durable state in multi-session, multi-writer, or Level 2/3 work; skip for ordinary single-session tasks."
---

# Context memory

Own continuity during work. `core/documentation` owns durable user/technical documentation after the change.

## Memory map

- `constitution.md`: stable non-negotiable project principles.
- `project-profile.md`: current project facts and boundaries.
- `commands.md`: verified commands only.
- `conventions.md`: project-specific patterns.
- `standards.md`: dated changing normative references.
- `risks.md`: durable security, privacy, cost, operational, and UX risks.
- `decision-log.md`: decisions, rejected options, supersession, and reasons.
- `shared-context.md`: concise cross-session current state.
- `tasks/`: task contract, notes, gate indexes, evidence pointers, status, and handoff.
- `bridge/`: coordination pointers, not task payloads.

## Procedure

1. Read the active task contract and only the referenced memory needed for the current step.
2. Write facts that another agent must know to resume safely: acceptance criteria, ownership, material decisions, contract changes, unresolved risks, approvals, validation state, and next action.
3. Link to source files or controlled evidence rather than copying large payloads.
4. Mark facts as verified, inferred, historical, or superseded where ambiguity is possible.
5. Replace stale summaries; append only where chronology matters, such as decisions and bridge events.
6. Before compaction or handoff, ensure the task contract and notes can restore current status without chat history.

Never store chain-of-thought, secrets, raw customer data, full logs, unredacted screenshots, or private prompt payloads. Use bounded redacted summaries plus pointers/hashes.

Memory writes require write authorization. In a read-only task, return a proposed handoff packet in the response instead.

## Hygiene test

Keep an item only if its absence could cause rework, a wrong decision, a safety failure, or an unsafe handoff. Delete duplicate prose, resolve contradictions, and retain the authoritative pointer.
