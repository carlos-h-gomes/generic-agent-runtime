# AGENTS.md — Generic Agent Runtime

Version: 3.7
Runtime language: English, to maximize compatibility with coding agents.
User-facing responses may use the user's language.

> Compatibility note: `AGENTS.md` is the cross-tool standard (Codex, Cursor, Copilot, Gemini CLI, Aider, Windsurf, and others) and is also read by Claude Code, which additionally reads the richer `CLAUDE.md`. Keep this file focused on commands, constraints, routing and non-standard patterns: empirical studies (Lulla et al. 2026; Chatlatanagulchai et al. 2025) show a focused agent-context file measurably lowers agent runtime and token cost, while generic architecture dumps and directory maps do not improve delivery and inflate cost. Do not paste discoverable content (README prose, file trees) here.

## 0. Prime directive

This repository uses an adaptive governance runtime for Codex, Claude Code, and other coding agents.

Before changing product code, the agent must:

1. Read `AGENTS.md`.
2. Read `CLAUDE.md` when available.
3. Read the active project memory files in `docs/ai/` that are relevant to the task.
4. Classify the task level by scope, risk, and reversibility.
5. Produce a strict structured task specification before implementation.
6. Build a compact written context packet before implementation.
7. Use the smallest workflow that can safely deliver high quality.
8. Load only the skills relevant to the current task.
9. Run available validation commands when practical.
10. Use the implementation/testing reflection loop when validation commands are available.
11. Stop before destructive, production, security-sensitive, privacy-sensitive, customer-impacting, or cost-increasing actions unless explicitly approved.

Quality means the right amount of process, not maximum process.

---

## 1. Non-negotiable written-memory rule

Agents must not rely on “mental notes”, hidden memory, chat-only recollection, or unstored assumptions.

Every durable item required for later work must be written to repository files.

Durable items include:

- Project overview, stack, architecture, and important paths.
- Commands for build, test, lint, typecheck, deploy, and local execution.
- Conventions and patterns discovered in the codebase.
- Important business rules and edge cases.
- Integration contracts, payload examples, schemas, and data flow rules.
- Security, privacy, compliance, operational, and cost risks.
- Decisions, rejected alternatives, and reasons.
- Cross-tool handoff notes when more than one agent/tool may touch the same files.

Use these files as the written memory layer:

```text
docs/ai/constitution.md          Durable, rarely-changing project principles and hard constraints (optional but recommended)
docs/ai/project-profile.md       Project identity, stack, architecture, paths, environments
docs/ai/commands.md              Verified commands only
docs/ai/conventions.md           Code, architecture, UX, testing, docs conventions
docs/ai/risks.md                 Security, privacy, cost, operational, UX/product risks
docs/ai/decision-log.md          Decisions, rejected alternatives, and reasons
docs/ai/shared-context.md        Cross-session and cross-tool context that must not be lost
docs/ai/tasks/                   Task-specific context, plan, gates, validation and handoff
```

The `constitution.md` holds the small set of non-negotiable principles every task must respect (for example: "all user input is validated", "self-hosted/open-source preferred", "no per-client customization", "human approval before production changes"). It is the most stable layer and bounds every other artifact. Keep it short; it is principles, not implementation detail.

If a detail matters but no existing file fits, create or update the smallest appropriate `docs/ai` file and explain why.

---

## 2. Source-of-truth hierarchy

When sources conflict, use this order:

1. User's latest explicit instruction.
2. Safety/security constraints and explicit approval boundaries.
3. `docs/ai/constitution.md` durable project principles, when present.
4. Repository files and current code.
5. `docs/ai` project memory.
6. Existing tests and CI configuration.
7. Previous task files and decision log.
8. General best practices.

Never invent commands, architecture, or business rules. Mark unknowns explicitly.

---

## 2.1 Strict task specification rule

Before implementation, `core/task-triage` must convert the user's intent into structured data.

Implementation must not start from vague chat instructions. It must start from a task specification that includes, at minimum:

- clear description;
- acceptance criteria;
- affected files or a file discovery plan;
- owned/shared/do-not-touch file coordination;
- triggered gates;
- validation plan;
- human approval status.

Preferred format: JSON. YAML is acceptable only when the target agent cannot handle JSON well.

If description, acceptance criteria, or affected-file discovery are missing, the task is not ready for implementation. The triage result must be `needs_clarification` or `blocked`, with missing fields listed.

For Level 2/3 tasks, store the structured task specification in the active task file under `docs/ai/tasks/`.


---

## 3. Context ingress protocol

For every non-trivial task, create a compact written context packet before making changes.

For Level 0 and Level 1, this can be a short internal note in the response or task scratchpad.
For Level 2 and Level 3, create or update a task file:

```text
docs/ai/tasks/YYYY-MM-DD-short-task-name.md
```

The context packet must include, as applicable:

- Structured task specification from `core/task-triage`.
- User request and acceptance criteria.
- Task level and triggered gates.
- Files likely to change.
- Files that must not change.
- Relevant project docs read.
- Relevant code paths inspected.
- Existing patterns to preserve.
- Business rules discovered.
- External contracts and payloads.
- Security/privacy/cost/operational constraints.
- Open assumptions.
- Validation plan.

Before implementation, verify that enough context is written down to resume the task after a context reset.

---

## 4. Multi-tool and shared-file coordination

When Codex, Claude, a human, or another tool may manipulate the same files, agents must maintain a shared understanding through text files, not memory.

For Level 2 or Level 3 tasks, the task file must include:

- `Owned files`: files this agent intends to modify.
- `Shared files`: files that may be touched by another agent/tool.
- `Do-not-touch files`: files intentionally excluded.
- `Handoff notes`: what the next agent/tool must know.
- `Current status`: draft / in-progress / blocked / ready-for-review / done.

Before changing a shared file:

1. Read the latest task file and `docs/ai/shared-context.md`.
2. Check for conflicting instructions.
3. Preserve existing context and update the handoff notes after changes.
4. Do not overwrite another agent's undocumented work.

If a conflict appears, stop and ask for direction unless the correct resolution is explicitly documented.

---

## 5. Context budget rules

The runtime must reduce token use without sacrificing correctness.

- Do not load every skill by default.
- Do not scan the whole repository blindly if targeted inspection is enough.
- Do not create a PRD for Level 0 or Level 1 tasks.
- Do not produce long final reports unless the task is Level 3 or the user requested it.
- Do not update documentation for trivial changes.
- Prefer compact task files for Level 2/3 work.
- When context grows, summarize durable findings into the task file and continue from the summary.
- Use progressive disclosure: read summaries first, then source files only when needed.
- Quote or copy only the minimum needed code/context into planning docs.

Token efficiency is not permission to skip required context. It means moving important context into concise written project memory.

---

## 6. Required repository discovery

At the start of a new project or when project memory is incomplete, inspect only what is needed:

```text
README.md
AGENTS.md / CLAUDE.md
package.json / pnpm-lock.yaml / yarn.lock / package-lock.json
pyproject.toml / requirements.txt / uv.lock / poetry.lock
Dockerfile / docker-compose.yml / compose.yml
Makefile / Taskfile / justfile
.github/workflows/ or other CI config
src/ or app/ or pages/ or server/
docs/ai/
.agents/skills/
```

Project profiling must update written memory and must not implement features.

---

## 7. Bootstrap mode and harness mode

This runtime has two operating modes.

### 7.1 First run — Bootstrap / Project Profiling

Use Bootstrap mode when the repository does not yet have a usable governance memory layer, especially when one or more of these are missing or clearly incomplete:

```text
docs/ai/project-profile.md
docs/ai/commands.md
docs/ai/conventions.md
docs/ai/risks.md
docs/ai/shared-context.md
.agents/skills/
scripts/validate.sh
```

Bootstrap mode must:

1. Inspect the repository structure only as much as needed.
2. Identify stack, frameworks, runtime, package manager, test/lint/typecheck/build commands, infrastructure and important paths.
3. Create or update the core `docs/ai` memory files.
4. Create or preserve the `.agents/skills` runtime.
5. Create or adapt validation scripts when practical.
6. Register important initial decisions in `docs/ai/decision-log.md` when there is a real decision.
7. Stop and summarize findings, risks and next steps.

Bootstrap mode must not implement product features unless the user explicitly asks for both bootstrap and implementation.

### 7.2 Second run onward — Harness mode

Use Harness mode when project memory exists. Every task must be routed by level and by triggered gates.

The canonical full harness is:

```text
Intent
→ Strict task specification (specify)
→ Clarify ambiguities before planning
→ Context packet
→ Requirements / Mini PRD
→ UX/Product review when triggered
→ Architecture/UML review when triggered
→ Specialist gates when triggered
→ Cross-artifact consistency check (analyze) before implementation
→ Implementation
→ Code quality/testing reflection loop
→ Release / rollback / monitoring when triggered
→ Handoff notes
```

This mirrors the now-standard spec-driven sequence (specify → clarify → plan → tasks → analyze → implement) used by tools such as Spec Kit, while staying tool-agnostic.

**Clarify step:** before planning a Level 2/3 task, resolve ambiguities, edge cases and unstated assumptions. Record answers in the task file. If the agent cannot define acceptance criteria or safe affected-file discovery, triage returns `needs_clarification` instead of guessing. For an exploratory spike, the agent may explicitly skip clarification and say so.

**Analyze step:** before implementation on Level 2/3 work, run a quick cross-artifact consistency check across the task spec, the UX/Product artifact, and the Architecture/UML artifact. Confirm acceptance criteria are covered, the artifacts do not contradict each other or the codebase, and nothing required is missing. This is read-only; it produces a short list of gaps to fix, not code.

The harness may be shortened for Level 0/1 work, but a skipped gate must be either clearly not applicable or intentionally deferred with a reason.

---

## 8. Task levels

### Level 0 — Micro

Examples:

- Small text change.
- Small CSS/layout adjustment.
- Rename variable.
- Obvious local bug fix.
- Small documentation correction.

Workflow:

```text
Understand → Change → Validate minimally → Short summary
```

No PRD. No architecture review. No task document unless requested.

### Level 1 — Simple

Examples:

- Local component adjustment.
- Small function change.
- Local refactor.
- Non-critical UI improvement.

Workflow:

```text
Intent → Structured task spec → Relevant context → Implement → Validate → Short summary
```

Use `core/implementation` and `core/validation` when helpful.

### Level 2 — Medium

Examples:

- New endpoint.
- New page or screen.
- New internal integration.
- New table or schema addition.
- Business rule change.
- Internal automation.
- Refactor touching multiple files.

Workflow:

```text
Intent → Structured task spec → Written context packet → Mini PRD → UX/Architecture gates when triggered → Technical plan → Implement → Reflection loop → Validation summary → Handoff notes
```

Create a task file when the change affects architecture, data, integration, operations, or future maintenance.

### Level 3 — Critical

Examples:

- Production changes.
- Authentication or authorization.
- Personal/customer data.
- Billing or payments.
- Infrastructure.
- Destructive migration.
- Public webhook or public API.
- LLM/AI using user/customer context.
- High-volume automation.
- Meaningful variable cost increase.
- Security-sensitive configuration.

Workflow:

```text
Intent
→ Structured task specification
→ Written context packet
→ PRD
→ UX/Product review when triggered
→ Architecture/UML review
→ Required specialist gates
→ Implementation plan
→ Human approval when required
→ Implementation
→ Code quality/testing reflection loop
→ Validation
→ Release, monitoring and rollback plan
→ Handoff notes
```

Human approval is required before destructive, production, security-sensitive, privacy-sensitive, customer-impacting, or cost-increasing execution.

---

## 9. Software engineering and architecture standards

Use robust software engineering standards, proportional to task level.

Default principles:

- YAGNI and minimalism: prefer the smallest solution that meets the acceptance criteria; stop at the first rung that solves the need (skip it → stdlib → native platform → existing dependency → one line → minimum). Never cut validation, security, accessibility or data-loss handling to reduce code. See `.agents/skills/core/minimalism/SKILL.md`.
- Clean Code.
- SOLID.
- Separation of concerns.
- High cohesion and low coupling.
- Explicit boundaries between UI, application, domain, infrastructure, and external integrations.
- Dependency inversion for external services where practical.
- Explicit error handling and typed/validated boundaries.
- Secure-by-design defaults.
- Testable units and integration seams.
- Backward compatibility unless intentionally changed.

For Level 2/3 work, evaluate architecture with lightweight models before implementation:

- C4 Context or Container view when system boundaries matter.
- UML component diagram when module/service relationships matter.
- UML sequence diagram when workflows, APIs, events, or async behavior matter.
- UML class/domain model when entities, aggregates, or service contracts matter.
- UML state diagram when status transitions, lifecycle, retries, or approval flows matter.
- Deployment diagram when infrastructure, network, secrets, queues, or runtime topology matter.
- Threat model when trust boundaries, external input, auth, data, or public endpoints exist.

Text diagrams using Mermaid/PlantUML are acceptable. Do not create heavyweight diagrams for small tasks.


### Product and architecture pipeline order

For new features or meaningful behavior changes, use this order before implementation:

```text
task-triage → UX/Product when user-facing → Software Architecture/UML when architecture/data/integration/deployment is affected → implementation → code-quality-testing → validation/handoff
```

Implementation is not the architecture owner. If the task changes database behavior, schemas, integrations, n8n flows, Caddy/reverse-proxy behavior, deployment topology, external contracts, queues, jobs, or cross-cutting workflows, `specialists/software-architecture-uml` must produce a Markdown/Mermaid architecture artifact before implementation starts.

If the task is user-facing, `specialists/ux-product` must define the product/UX acceptance criteria before implementation starts.

Implementation must return the task to triage or the missing specialist when required artifacts are absent, ambiguous, or incompatible with the codebase.

---

## 10. Skill loading policy

Load skills only when needed.

Core skills:

```text
.agents/skills/core/project-profiling/SKILL.md
.agents/skills/core/task-triage/SKILL.md
.agents/skills/core/context-memory/SKILL.md
.agents/skills/core/implementation/SKILL.md
.agents/skills/core/minimalism/SKILL.md
.agents/skills/core/validation/SKILL.md
.agents/skills/core/documentation/SKILL.md
```

Specialist skills:

```text
.agents/skills/specialists/software-architecture-uml/SKILL.md
.agents/skills/specialists/code-quality-testing/SKILL.md
.agents/skills/specialists/ux-product/SKILL.md
.agents/skills/specialists/risk-security-compliance/SKILL.md
.agents/skills/specialists/data-integration/SKILL.md
.agents/skills/specialists/finops-cost/SKILL.md
.agents/skills/specialists/observability-release/SKILL.md
.agents/skills/specialists/ai-llm/SKILL.md
```

Use specialists as gates, not as theater. If a specialist is not relevant, do not load it.

### Skill format and discovery

Every skill is a folder containing `SKILL.md` with YAML frontmatter (`name`, `description`) followed by the markdown body. The `name` must match the folder name. The `description` states both what the skill does and when to use it; modern agents (Claude Code, Codex, Cursor, and others) auto-discover skills from this frontmatter at startup and load the full body only when a task matches. Keep `name` + `description` portable; any agent-specific frontmatter fields are safely ignored by agents that do not support them.

### Optional subagent / isolation pattern

When the host agent supports subagents (e.g. Claude Code `context: fork`, `skills:`, `allowed-tools`), heavy read-only work such as repository exploration, architecture analysis, or a security/red-team pass may run in an isolated subagent to keep the main context lean. Recommended pattern: give research/review subagents read-only tools and let the parent agent perform edits and run commands that need approval. This is optional and tool-specific; the runtime does not require it.

---

## 11. Mandatory gates by trigger

### Architecture/UML gate

Use for Level 2/3 tasks that change module boundaries, architecture, data model, integration flow, public contracts, workflow state, deployment, or cross-cutting concerns.

Must evaluate:

- System boundaries.
- Module/service responsibilities.
- Dependencies and coupling.
- Data ownership.
- Contract compatibility.
- Error/failure paths.
- Appropriate UML/C4 view when useful.

### Code quality/testing gate

Use when adding or changing meaningful business logic, shared utilities, refactors, test strategy, or code paths with edge cases.

When validation commands exist, this gate owns the autonomous reflection loop between implementation and testing.

### UX/Product gate

Use when there is any interface, workflow, product flow, onboarding, dashboard, form, empty state, error state, pricing page, guided tour, notification, or user-facing copy.

### Security/Compliance gate

Use when there are credentials, auth, permissions, external input, public endpoints, file uploads, customer data, personal data, logs, third-party transfer, dependency/supply-chain changes, or production impact.

For agent, tool-using, retrieval, or memory features, also evaluate against the OWASP Top 10 for Agentic Applications (2026) (ASI01–ASI10): goal hijack, tool misuse, identity/privilege abuse, supply chain, unexpected code execution, memory poisoning, insecure inter-agent comms, cascading failures, human-agent trust exploitation, and rogue agents. See `specialists/risk-security-compliance` for the mapping and baseline mitigations.

### Data/Integration gate

Use when there are APIs, webhooks, ETL/ELT, queues, databases, schemas, migrations, spreadsheets, events, dashboards, idempotency, retries, or reprocessing.

### FinOps gate

Use when there are paid APIs, LLMs, embeddings, OCR, scraping, recurring jobs, cloud resources, storage, queues, logs, high volume, or dashboards.

### Observability/Release gate

Use when the change affects production, jobs, endpoints, automations, customer impact, SLAs, deployment, rollback, monitoring, or alerts.

### AI/LLM gate

Use when the feature sends content to a model, receives model output used by a system, uses tools, uses retrieval, stores prompts, handles user/customer context, or can be prompt-injected.

---

## 12. Documentation policy

Update or create `docs/ai` documentation only when there is durable project knowledge:

- New architecture decision.
- New integration.
- New endpoint or contract.
- New table/schema/migration.
- New recurring job or operational workflow.
- New cost driver.
- New security/compliance risk.
- New release or rollback procedure.
- New cross-tool handoff requirement.
- New business rule that future agents must preserve.

For Level 2 or 3 tasks, use:

```text
docs/ai/tasks/YYYY-MM-DD-short-task-name.md
```

For decisions, append to:

```text
docs/ai/decision-log.md
```

Do not create generic filler. Good docs are short, factual, and useful for the next agent.

---

## 13. Validation policy

Prefer existing project commands. If available, run the relevant subset:

```bash
./scripts/validate.sh
./scripts/test.sh
./scripts/lint.sh
./scripts/security-check.sh
./scripts/cost-check.sh
```

Optionally, an output-compressing CLI proxy such as rtk (https://github.com/rtk-ai/rtk) can wrap these commands to cut tool-output tokens (e.g. `rtk test ./scripts/test.sh`, `rtk pytest`, `rtk cargo test`, `rtk git status`). This is a tooling-layer optimization, not a dependency: if it is absent, run the plain commands. When a wrapped command fails, diagnose from rtk's full tee'd output (saved on failure), never from the compact summary alone, and never report a pass off a filtered view.

If commands cannot run, explain why and provide a manual validation checklist.

Do not claim validation passed unless it actually ran successfully.

Validation depth by level:

- Level 0: targeted local/manual validation is acceptable.
- Level 1: relevant lint/test/manual check.
- Level 2: tests plus integration/edge-case validation where relevant.
- Level 3: full relevant validation, rollback plan, monitoring plan, and residual risk statement.

---


## 13.1 Autonomous reflection loop

For spec-driven implementation tasks, use a closed loop before human review when safe validation commands exist:

```text
core/implementation
→ specialists/code-quality-testing runs ./scripts/test.sh and ./scripts/lint.sh
→ failing stdout/stderr is returned to core/implementation
→ core/implementation corrects the issue
→ specialists/code-quality-testing reruns validation
```

Default maximum: **3 loops**.

After 3 failed loops, pause the task and produce a human review packet with the changed files, commands run, last failing command, exit code, actionable failure output, and suggested review focus.

Do not send known-broken code to human review before this loop runs unless validation cannot run or human approval is required before execution.

---

## 14. Human approval required

Ask for explicit approval before:

- Deleting data.
- Running destructive migrations.
- Changing production infrastructure.
- Exposing a public endpoint.
- Weakening authentication or authorization.
- Sending messages to customers.
- Running campaigns.
- Changing billing or pricing behavior.
- Storing or sending personal/customer data to third parties.
- Increasing variable cost materially.
- Executing irreversible scripts.
- Rotating or exposing secrets.
- Changing production deployment/release process.

---

## 15. Legacy specialist coverage map

This runtime intentionally consolidates many small specialists into fewer stronger gates to reduce token use and avoid theatrical agent switching. The old specialist responsibilities are still covered as follows:

| Legacy responsibility | Covered by v3.5 gate/skill | Notes |
|---|---|---|
| create-intent | `core/task-triage` | Converts the request into intent, level, scope and triggered gates. |
| create-prd / requirement-refiner | `core/task-triage` + task file | Level 2 uses a Mini PRD. Level 3 uses a fuller PRD section. |
| architecture-review | `specialists/software-architecture-uml` | Includes C4/UML, boundaries, contracts, risks and implementation plan. |
| generate-code | `core/implementation` | Uses project conventions and minimal safe change. |
| generate-tests / e2e-user-simulator | `specialists/code-quality-testing` | Covers unit, integration, contract, E2E, regression and manual validation fallback. |
| validate-delivery | `core/validation` + triggered gates | Confirms acceptance criteria, commands, residual risks and handoff. |
| release-delivery / release-manager | `specialists/observability-release` | Covers release checklist, rollback, monitoring and human approval. |
| security-review / red-teamer-agent | `specialists/risk-security-compliance` | Covers secrets, auth, input validation, threat model, abuse and secure defaults. |
| compliance-officer / legal-advisor | `specialists/risk-security-compliance` | Covers privacy, personal data, third-party transfer, retention and policy risk. |
| guardrail-policy-maker | `specialists/risk-security-compliance` + `specialists/ai-llm` | Use for product guardrails, model behavior, unsafe output, prompt injection and policy constraints. |
| session-guardian / context-manager | `core/context-memory` | Enforces written memory, context packets and cross-tool handoff. |
| ai-logic-engineer | `specialists/ai-llm` | Covers prompts, tools, retrieval, evaluation, cost, safety and model boundaries. |
| data-modeler | `specialists/data-integration` | Covers schemas, data ownership, migrations, lineage, quality and retention. |
| systems-integration | `specialists/data-integration` | Covers APIs, webhooks, queues, retries, idempotency and contracts. |
| backend-engineer | `core/implementation` + architecture/data gates | Covered by implementation standards and targeted gates. |
| frontend-engineer | `core/implementation` + `specialists/ux-product` | Covered by implementation and UX/product gate. |
| ux-architect | `specialists/ux-product` | Covers journey, layout, flows, copy, accessibility and states. |
| infra-orchestrator | `specialists/observability-release` + `specialists/finops-cost` | Covers deployment, runtime, rollback, cloud and cost impact. |
| finops-auditor | `specialists/finops-cost` | Covers variable cost, quotas, rate limits, caching, loops and alerts. |
| data-viz-engineer | `specialists/data-integration` + `specialists/ux-product` | Covers dashboard data correctness and user-facing presentation. |
| monitor-ops / incident-manager | `specialists/observability-release` | Covers logs, metrics, alerts, thresholds, runbooks, incidents and post-release checks. |
| market-strategy | `specialists/ux-product` when product/ICP/pricing is relevant | Keep product strategy lightweight unless requested. |

If a project needs the old one-specialist-per-role layout, it may add those skill folders as wrappers, but their responsibilities must map back to these gates to avoid duplication.

---

## 16. Preservation rule

Do not remove a workflow step, gate, validation policy, approval boundary, security rule, cost rule, compliance rule, or written-memory requirement unless the change is explicitly requested or justified in `docs/ai/decision-log.md`.

If a gate does not apply, mark it as:

```text
Not applicable — reason: ...
```

Never silently ignore an applicable gate.

For Level 2/3 tasks, the task file must show which gates were triggered, which were not applicable, and why.

---

## 17. Critical task completion checklist

For Level 3 tasks, the final validation must explicitly cover:

- Acceptance criteria status.
- Files changed and why.
- Tests, lint, typecheck, build and relevant manual checks.
- Architecture/UML impact.
- Security impact.
- Privacy/compliance impact.
- Data/integration impact.
- Cost/FinOps impact.
- Operational impact.
- Observability impact: logs, metrics, alerts, correlation IDs, dashboards or runbooks.
- Release plan.
- Rollback plan.
- Incident criteria and response path when production/customer impact exists.
- Human approval status.
- Residual risks and owner/handoff notes.

---

## 18. Final response formats

### Level 0 / Micro

```text
Done:
- ...

Validated:
- ...
```

### Level 1 / Simple

```text
Done:
- ...

Files changed:
- ...

Validated:
- ...

Notes:
- ...
```

### Level 2 / Medium

```text
Summary:
- ...

Files changed:
- ...

Validation:
- ...

Reflection loop:
- ...

Risks / pending items:
- ...

Handoff:
- ...
```

### Level 3 / Critical

```text
Summary:
- ...

Scope:
- ...

Files changed:
- ...

Validation:
- ...

Reflection loop:
- ...

Architecture / UML:
- ...

Security / Compliance / Cost:
- ...

Operational impact:
- ...

Rollback:
- ...

Human approval:
- Required / Not required, with reason.

Handoff:
- ...
```

Keep final reports proportional. Do not include unused gates.
