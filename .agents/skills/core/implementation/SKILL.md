---
name: implementation
description: "Execute the smallest safe code/config/docs change that satisfies an already-approved structured task specification, respecting project conventions and architecture/UX artifacts. Use only AFTER core/task-triage returns ready_for_implementation. Must not invent product scope, architecture, data contracts or deployment topology; returns the task to triage or a specialist when preconditions are missing."
---

# Implementation

## Objective

Implement the requested change with the smallest safe modification while respecting project conventions, written context, and the structured task specification produced by `core/task-triage`.

Implementation is an execution role. It must not invent product scope, acceptance criteria, architecture, data contracts, integration behavior, or deployment topology.

## When to use

- Any code/config/docs change after task triage has produced a valid task specification.

## Inputs expected

- Structured task specification from `core/task-triage`.
- User request.
- Task level.
- Relevant project memory.
- Existing patterns.
- Acceptance criteria.
- Architecture/UML artifact when triggered.
- UX/Product artifact when triggered.
- File coordination notes for shared files.
- Validation plan.

## Preconditions

Before implementing, verify that:

- `triage_status` is `ready_for_implementation`.
- Acceptance criteria are present.
- Owned/shared/do-not-touch files or a file discovery plan are present.
- Required architecture/UML and UX/Product artifacts exist when their gates are triggered.
- Human approval has been granted when the task crosses an approval boundary.

If a precondition fails, stop and return the task to `core/task-triage` or the missing specialist. Do not compensate by guessing.

## Process

1. Read relevant files first.
2. Confirm no shared-file conflict exists.
3. Confirm implementation constraints from architecture/UML and UX/Product artifacts, when present.
4. Prefer existing patterns over new abstractions.
5. Make the smallest coherent change.
6. Keep boundaries clear: UI, application, domain, infrastructure, integrations.
7. Handle errors explicitly.
8. Avoid hidden side effects.
9. Avoid new dependencies unless clearly justified.
10. Do not introduce secrets.
11. Preserve backward compatibility unless the task requires otherwise.
12. Update tests or validation checklist.
13. Hand off changed files, commands, and assumptions to `specialists/code-quality-testing` for the reflection loop.
14. Update task/handoff notes for Level 2/3.

## Spec-driven development rule

Implementation must code against the task specification, not against vague chat intent.

For every acceptance criterion, map the implementation change or validation path that proves it. If an acceptance criterion cannot be implemented or validated, mark the task as blocked before making speculative changes.

## Architecture boundary rule

Implementation may make local code-organization decisions inside the approved design, but it must not create architecture for a new feature.

When a task changes architecture, workflows, data models, integrations, deployment, or cross-cutting concerns, implementation must wait for `specialists/software-architecture-uml` to define the Markdown/Mermaid architecture artifact and implementation constraints.

## Reflection loop participation

After implementation, do not stop at “ready for approval” if validation commands are available. Hand the task to `specialists/code-quality-testing` to run the quality loop:

```text
Implementation → code-quality-testing runs ./scripts/test.sh and ./scripts/lint.sh → failures with stderr return to implementation → implementation fixes → repeat up to the configured attempt limit.
```

Implementation must use the exact failure output as feedback. Do not hide or summarize away actionable terminal errors.

## Quality criteria

- Change is scoped.
- Code is readable.
- Failure modes are handled.
- Existing behavior is preserved unless intentionally changed.
- Validation path exists.
- Each acceptance criterion maps to implementation or validation evidence.
- Important context is not left only in chat.

## Common risks

- Overengineering.
- Creating parallel patterns.
- Silent error handling.
- Unbounded loops or retries.
- Adding dependency for a small problem.
- Editing shared files without handoff notes.
- Inventing architecture during implementation.
- Treating failed tests as a human review problem before the reflection loop runs.

## Checklist

- [ ] Structured task specification read.
- [ ] Preconditions verified.
- [ ] Relevant files inspected.
- [ ] Required architecture/UX artifacts respected.
- [ ] Existing pattern followed.
- [ ] Minimal change made.
- [ ] Errors considered.
- [ ] Shared files coordinated.
- [ ] Acceptance criteria mapped to changes/validation.
- [ ] Tests or manual validation updated.
- [ ] Quality loop handoff prepared.
- [ ] Handoff notes updated if needed.
