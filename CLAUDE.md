# CLAUDE.md — Agent Entry Point

Read `AGENTS.md` first and follow it as the source of truth. This is Generic Agent Runtime v3.7.

Important behavior:

- Keep context lean, but never rely on mental notes.
- Load only the relevant skill files. Skills are discovered via their `SKILL.md` YAML frontmatter (`name`, `description`).
- Respect `docs/ai/constitution.md` (durable project principles) when it exists.
- Use Bootstrap mode when project memory is missing or incomplete.
- Use Harness mode after project memory exists.
- Use adaptive task levels.
- Apply the minimalism ladder (`core/minimalism`) when writing code: the smallest solution that meets the acceptance criteria, never cutting validation, security, accessibility or data-loss handling, and never used to skip a gate or approval boundary.
- When an output-compressing command proxy (e.g. rtk) is configured, prefer it for validation, git and test commands, and diagnose failures from its full tee'd output rather than the compact summary. It is optional: fall back to plain commands when absent.
- Start implementation only after `core/task-triage` produces a structured task specification with acceptance criteria and affected files/discovery plan.
- Clarify ambiguities before planning Level 2/3 work; if acceptance criteria or safe file discovery cannot be defined, return `needs_clarification`.
- For user-facing features, use UX/Product before implementation.
- For architecture/data/integration/deployment changes, use Software Architecture/UML before implementation.
- Before implementing Level 2/3 work, run the read-only cross-artifact consistency check (analyze) across the task spec, UX artifact and architecture artifact.
- After implementation, use the code-quality/testing reflection loop with `./scripts/test.sh` and `./scripts/lint.sh` when available, up to 3 attempts before human review.
- For security-sensitive or agent/tool/LLM features, apply the OWASP ASI Top 10 (2026) review in `specialists/risk-security-compliance`.
- Write durable context to `docs/ai` before it can be lost. Capture reusable lessons in `docs/ai/decision-log.md`.
- For Level 2/3 work, create or update a task file under `docs/ai/tasks/`.
- For UX work, load `.agents/skills/specialists/ux-product/SKILL.md`.
- For architecture or cross-file work, load `.agents/skills/specialists/software-architecture-uml/SKILL.md`.
- For critical work, use the required gates from `AGENTS.md` and complete the Level 3 checklist.
- If a gate is skipped, mark it as not applicable with a reason.
- Do not remove gates, approval boundaries, or memory requirements without a documented decision.
- Do not produce long final reports for small tasks.

Project-specific memory should live in:

```text
docs/ai/constitution.md
docs/ai/project-profile.md
docs/ai/commands.md
docs/ai/conventions.md
docs/ai/risks.md
docs/ai/shared-context.md
docs/ai/decision-log.md
```

Do not duplicate project details here unless they are essential for every session.
