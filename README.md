# Generic Agent Runtime

Version: 3.5

A reusable, token-efficient governance runtime for Codex, Claude Code, and other coding agents.

It is intentionally generic and contains no product/company identity.

## Design principle

The runtime uses adaptive governance:

- Small tasks stay fast.
- Medium tasks get written context, planning, and validation.
- Critical tasks get full risk gates, architecture review, validation, release, rollback and incident planning.
- UX work receives a stronger dedicated process.
- Architecture-sensitive work receives UML/C4 modeling when useful.
- Durable memory is written to files, never kept mentally.
- Expensive reports and documentation are created only when they add value.
- Legacy multiagent responsibilities are covered through consolidated gates to reduce token usage.
- Triage produces a strict structured task specification before implementation.
- Implementation follows spec-driven development instead of vague chat intent.
- Ambiguities are clarified before planning; artifacts are cross-checked (analyze) before implementation.
- Testing/linting run in an autonomous reflection loop before human review when possible.
- UX/Product and Architecture/UML gates run before implementation when triggered.
- Skills are auto-discoverable: each `SKILL.md` carries YAML frontmatter (`name`, `description`) so modern agents load only the relevant skill on demand.
- Security review covers the OWASP Top 10 for Agentic Applications (2026) when agents, tools, retrieval or memory are involved.

## Install

Copy the contents of this folder into the root of a project.

Then start the agent with:

```text
Before implementing anything, read AGENTS.md and CLAUDE.md.
If docs/ai/project-profile.md is incomplete, run project profiling first.
Use the smallest safe workflow for the task.
Do not rely on mental notes; write durable context to docs/ai.
```

## First run recommendation

The first run is **Bootstrap / Project Profiling**. It should create or update project memory and stop before product implementation unless explicitly requested.

Ask the agent:

```text
Run Project Profiling only. Detect the stack, commands, conventions, architecture, important paths and risks. Update docs/ai/project-profile.md, docs/ai/commands.md, docs/ai/conventions.md, docs/ai/shared-context.md and docs/ai/risks.md. Capture any durable principles in docs/ai/constitution.md. Do not implement features yet.
```

## Main files

```text
AGENTS.md                         Runtime rules
CLAUDE.md                         Claude Code entry point
docs/ai/constitution.md           Durable project principles and hard constraints
docs/ai/project-profile.md        Project-specific memory
docs/ai/commands.md               Trusted commands
docs/ai/conventions.md            Coding, architecture and design conventions
docs/ai/shared-context.md         Cross-tool/cross-session written memory
docs/ai/risks.md                  Known risks and gates
docs/ai/quality-gates.md          Gate criteria
docs/ai/decision-log.md           Durable decisions and reusable lessons
docs/ai/tasks/                    Task plans and handoffs
.agents/skills/                   On-demand skills (YAML-frontmatter discoverable)
scripts/                          Validation helpers
prompt-templates/                 Reusable prompts for new/running/tasks/context
```
