# Changelog

## 3.1

- Added explicit Bootstrap / Project Profiling mode and Harness mode.
- Added legacy specialist coverage map so the old multiagent AGENTS responsibilities remain covered by the consolidated v3 gates.
- Added preservation rule: gates, policies, approval boundaries and written-memory rules cannot be removed silently.
- Added Level 3 critical completion checklist covering security, compliance, cost, operations, observability, rollback, incident path and approval.
- Updated Claude entrypoint and task template to require not-applicable/deferred gate reasons.
- Kept the runtime generic, with no company/product identity.

## 3.0

- Removed company/product identity from runtime wording.
- Added strict written-memory rule: no mental notes for durable context.
- Added context ingress protocol for Level 2/3 tasks.
- Added shared-file and cross-tool handoff coordination.
- Added `docs/ai/shared-context.md`.
- Added Architecture/UML gate and specialist.
- Added Code Quality/Testing specialist.
- Expanded Project Profiling inputs and outputs.
- Strengthened software engineering rules: Clean Code, SOLID, boundaries, secure-by-design, validation.
- Strengthened FinOps/token rules with progressive disclosure and context compaction.
- Added revised prompt templates for new projects, running projects, tasks, and application context.
