---
name: project-profiling
description: "Build a concise, accurate written profile of an unfamiliar or under-documented repository: stack, verified commands, architecture boundaries, important paths, integrations and risks. Use this FIRST on a new project, when docs/ai/project-profile.md is missing/empty/stale, or whenever the agent is unsure how to build, test, run or validate the project. Does not implement features."
---

# Project Profiling

## Objective

Create a compact, accurate written profile of the repository so future agent work is cheaper, safer, and more consistent.

## When to use

- First run in a new project.
- Existing `docs/ai/project-profile.md` is missing, empty, or stale.
- The agent is unsure how to run, test, build, validate, or understand the project.

## When not to use

- The task is small and project conventions are already clear.
- The user explicitly asked for a direct small edit.

## Inputs to collect

- Product purpose and users.
- Stack and runtime.
- Important paths and modules.
- Verified commands.
- Architecture boundaries and data flows.
- External integrations and contracts.
- Security/privacy/cost/operational risks.
- Existing code conventions.
- Files likely to be shared across tools.

## Process

1. Inspect root files: README, package manager files, Python files, Docker files, CI files, scripts.
2. Inspect targeted source folders only as needed.
3. Identify stack, commands, architecture, important paths, integrations, and risk areas.
4. Do not implement features.
5. Update only:
   - `docs/ai/constitution.md` (only the durable principles/hard constraints; leave as template if none are clear yet)
   - `docs/ai/project-profile.md`
   - `docs/ai/commands.md`
   - `docs/ai/conventions.md`
   - `docs/ai/shared-context.md`
   - `docs/ai/risks.md`
6. Keep all documents concise and factual.
7. Mark unknowns explicitly instead of guessing.

## Orientation, not a directory dump

Empirical studies of agent-context files (Chatlatanagulchai et al. 2025; Lulla et al. 2026) find that verified commands, constraints and non-standard patterns improve agent behavior and lower cost, while generic architecture overviews and file-tree maps do not measurably help delivery and can inflate token use. Therefore:

- Favor commands, constraints, conventions, and the few non-obvious patterns a new agent could not infer.
- Keep the architecture map high-level (boundaries and data flow), not a file-by-file inventory the agent can discover itself.
- Do not copy README prose or directory trees into project memory.

## Quality criteria

- Commands are copied from real project files, not invented.
- Risk notes are specific.
- The profile is short enough to be loaded every session.
- No generic boilerplate.
- Enough context exists to resume after a context reset.

## Checklist

- [ ] Stack identified.
- [ ] Commands identified.
- [ ] Important paths identified.
- [ ] Architecture/data flow summarized.
- [ ] Known risks identified.
- [ ] Shared files identified.
- [ ] Unknowns marked.
- [ ] No feature implementation performed.
