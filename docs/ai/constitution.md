# Project Constitution

Status: template. Fill during Project Profiling or first Level 2/3 task. Keep it short.

This file holds the small set of durable, rarely-changing principles and hard constraints that **every** task must respect. It is the most stable layer of project memory and bounds all other artifacts (conventions, decisions, task plans). If a task would violate a principle here, stop and ask before proceeding.

Principles are the "what we always do / never do", not implementation detail. Implementation detail belongs in `conventions.md`; specific decisions belong in `decision-log.md`.

## Core principles

List 5–12 non-negotiable principles. Examples (replace with the real ones):

- All external/user input is validated before use; model and tool output is treated as untrusted.
- Human approval is required before production, destructive, or cost-increasing actions.
- Prefer the smallest safe change and existing patterns over new abstractions.
- Secure-by-design defaults; least-privilege credentials; no secrets in code or logs.
- Durable context is written to `docs/ai`, never kept as mental notes.
- (Add project-specific principles, e.g. preferred stack, self-hosted vs managed, no per-client forks, accessibility baseline, data-residency rules.)

## Hard constraints

Things that are simply not allowed in this project, regardless of task:

| Constraint | Reason | Source |
|---|---|---|
|  |  |  |

## Quality bar

What "done" means at minimum here (tests, lint, accessibility, performance budgets, etc.):

-

## Change policy

This file changes rarely. When it must change, record the reason in `decision-log.md` and mark the superseded principle. Do not edit it for one-off task convenience.
