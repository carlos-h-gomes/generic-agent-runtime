# Implementation

## Objective

Implement the requested change with the smallest safe modification while respecting project conventions and written context.

## When to use

- Any code/config/docs change.

## Inputs expected

- User request.
- Task level.
- Relevant project memory.
- Existing patterns.
- Acceptance criteria.
- File coordination notes for shared files.
- Validation plan.

## Process

1. Read relevant files first.
2. Confirm no shared-file conflict exists.
3. Prefer existing patterns over new abstractions.
4. Make the smallest coherent change.
5. Keep boundaries clear: UI, application, domain, infrastructure, integrations.
6. Handle errors explicitly.
7. Avoid hidden side effects.
8. Avoid new dependencies unless clearly justified.
9. Do not introduce secrets.
10. Preserve backward compatibility unless the task requires otherwise.
11. Update tests or validation checklist.
12. Update task/handoff notes for Level 2/3.

## Quality criteria

- Change is scoped.
- Code is readable.
- Failure modes are handled.
- Existing behavior is preserved unless intentionally changed.
- Validation path exists.
- Important context is not left only in chat.

## Common risks

- Overengineering.
- Creating parallel patterns.
- Silent error handling.
- Unbounded loops or retries.
- Adding dependency for a small problem.
- Editing shared files without handoff notes.

## Checklist

- [ ] Relevant files inspected.
- [ ] Existing pattern followed.
- [ ] Minimal change made.
- [ ] Errors considered.
- [ ] Shared files coordinated.
- [ ] Tests or manual validation updated.
- [ ] Handoff notes updated if needed.
