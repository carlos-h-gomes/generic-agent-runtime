# Generic Agent Runtime

Version: 3.1

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
Run Project Profiling only. Detect the stack, commands, conventions, architecture, important paths and risks. Update docs/ai/project-profile.md, docs/ai/commands.md, docs/ai/conventions.md, docs/ai/shared-context.md and docs/ai/risks.md. Do not implement features yet.
```

## Main files

```text
AGENTS.md                         Runtime rules
CLAUDE.md                         Claude Code entry point
docs/ai/project-profile.md        Project-specific memory
docs/ai/commands.md               Trusted commands
docs/ai/conventions.md            Coding, architecture and design conventions
docs/ai/shared-context.md         Cross-tool/cross-session written memory
docs/ai/risks.md                  Known risks and gates
docs/ai/quality-gates.md          Gate criteria
docs/ai/tasks/                    Task plans and handoffs
.agents/skills/                   On-demand skills
scripts/                          Validation helpers
prompt-templates/                 Reusable prompts for new/running/tasks/context
```
