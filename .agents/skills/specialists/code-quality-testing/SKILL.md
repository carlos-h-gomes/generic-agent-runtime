# Code Quality and Testing Specialist

## Objective

Improve correctness, maintainability, and regression safety while avoiding unnecessary complexity.

## When to use

- Business logic changes.
- Shared utilities.
- Refactors.
- Edge-case-heavy code.
- New validation rules.
- Bug fixes that need regression coverage.

## Inputs expected

- Acceptance criteria.
- Existing test patterns.
- Changed files.
- Edge cases.
- Validation commands.

## Process

1. Identify behavior under change.
2. Identify edge cases and failure modes.
3. Check existing abstractions and patterns.
4. Keep functions/classes focused.
5. Avoid hidden mutable state where practical.
6. Add or update tests at the lowest useful level.
7. Add integration or contract tests when boundaries are involved.
8. Confirm validation commands.

## Deliverables

- Code quality review notes.
- Test plan.
- Edge-case list.
- Validation outcome.

## Quality criteria

- Code is readable and localized.
- Tests protect important behavior.
- Edge cases are covered or documented.
- No unnecessary dependency or abstraction.


## Written memory rule

For Level 2/3 work, record durable findings, assumptions, risks, and handoff notes in the active task file or the appropriate `docs/ai` file. Do not rely on mental notes.

## Checklist

- [ ] Behavior identified.
- [ ] Edge cases identified.
- [ ] Existing patterns respected.
- [ ] Tests considered/updated.
- [ ] Validation command identified.
