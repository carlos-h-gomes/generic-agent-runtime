# CLAUDE.md — Agent Entry Point

Read `AGENTS.md` first and follow it as the source of truth. This is Generic Agent Runtime v3.1.

Important behavior:

- Keep context lean, but never rely on mental notes.
- Load only the relevant skill files.
- Use Bootstrap mode when project memory is missing or incomplete.
- Use Harness mode after project memory exists.
- Use adaptive task levels.
- Write durable context to `docs/ai` before it can be lost.
- For Level 2/3 work, create or update a task file under `docs/ai/tasks/`.
- For UX work, load `.agents/skills/specialists/ux-product/SKILL.md`.
- For architecture or cross-file work, load `.agents/skills/specialists/software-architecture-uml/SKILL.md`.
- For critical work, use the required gates from `AGENTS.md` and complete the Level 3 checklist.
- If a gate is skipped, mark it as not applicable with a reason.
- Do not remove gates, approval boundaries, or memory requirements without a documented decision.
- Do not produce long final reports for small tasks.

Project-specific memory should live in:

```text
docs/ai/project-profile.md
docs/ai/commands.md
docs/ai/conventions.md
docs/ai/risks.md
docs/ai/shared-context.md
docs/ai/decision-log.md
```

Do not duplicate project details here unless they are essential for every session.
