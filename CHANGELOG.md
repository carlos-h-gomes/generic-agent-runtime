# Changelog

## 3.5

Focus: make skills auto-discoverable by modern agents, align with spec-driven development standards, and modernize the security model for the agentic era. Backed by 2026 research and tooling review; no gate, approval boundary, or written-memory rule was removed.

- Added YAML frontmatter (`name`, `description`) to all 14 `SKILL.md` files so Claude Code, Codex, Cursor and other agents auto-discover and model-invoke them. Without frontmatter the "load only relevant skills" design could not fire automatically. Descriptions state both what each skill does and when to use it.
- Documented the skill format/discovery rule and an optional subagent/context-fork isolation pattern (read-only research/review subagent, parent performs edits) in `AGENTS.md`.
- Added the spec-driven `clarify` step (resolve ambiguities before planning) and a read-only cross-artifact `analyze` step (consistency check across task spec, UX and architecture artifacts) before implementation. Aligns with the standard specify → clarify → plan → tasks → analyze → implement sequence.
- Added `docs/ai/constitution.md`: durable, rarely-changing project principles and hard constraints, placed high in the source-of-truth hierarchy.
- Added a "Lessons learned" capture in `docs/ai/decision-log.md` and the task template, so non-obvious failures and reusable fixes inform future runs.
- Upgraded `specialists/risk-security-compliance` with an OWASP Top 10 for Agentic Applications (2026) mapping (ASI01–ASI10) and baseline mitigations: untrusted external content, least-privilege tools, scoped/JIT credentials, sandboxed code execution, memory-poisoning guards, loop/attempt caps with a stop path, human-in-the-loop on state-mutating actions, and shadow-mode rollout.
- Strengthened `specialists/ai-llm` with concrete 2026 injection and output-handling defenses (separate trusted instructions from untrusted data, treat model output as untrusted before it acts, bound autonomy, guard durable memory).
- Upgraded `scripts/security-check.sh` to a layered scan: SAST (Semgrep), secrets (Gitleaks/TruffleHog with regex fallback), SCA/dependency CVEs (Trivy / pip-audit / npm audit), and IaC/container misconfig (Trivy config). Graceful degradation preserved.
- Added empirical guidance in `core/project-profiling` and `AGENTS.md`: agent-context files should favor commands, constraints and non-standard patterns; generic architecture overviews and directory-map dumps do not improve delivery and inflate cost (Chatlatanagulchai et al. 2025; Lulla et al. 2026).
- Updated `CLAUDE.md`, `README.md`, the task template, `commands.md` (SCA slot) and `quality-gates.md` (supply-chain + agentic pass conditions) to match.

## 3.4

- Added strict `core/task-triage` JSON/YAML task specification before implementation.
- Added Plan-Act routing: vague tasks are returned as `needs_clarification` or `blocked` instead of being sent to implementation.
- Added spec-driven implementation preconditions and architecture boundary rules.
- Added autonomous implementation/testing reflection loop using `./scripts/test.sh` and `./scripts/lint.sh` when available.
- Added 3-attempt maximum for failed validation loops before pausing for human review.
- Strengthened `core/context-memory` as a context curator with memory pruning and durable decision logging.
- Added product/architecture pipeline ordering so UX/Product and Software Architecture/UML gates run before implementation when triggered.
- Updated prompt templates to require fixed output blocks and final `## Critérios de Validação Técnica` for task creation.

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
