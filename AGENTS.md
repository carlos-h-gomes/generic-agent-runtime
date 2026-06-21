# AGENTS.md — Generic Agent Runtime

Version: 3.1
Runtime language: English, to maximize compatibility with coding agents.
User-facing responses may use the user's language.

## 0. Prime directive

This repository uses an adaptive governance runtime for Codex, Claude Code, and other coding agents.

Before changing product code, the agent must:

1. Read `AGENTS.md`.
2. Read `CLAUDE.md` when available.
3. Read the active project memory files in `docs/ai/` that are relevant to the task.
4. Classify the task level by scope, risk, and reversibility.
5. Build a compact written context packet before implementation.
6. Use the smallest workflow that can safely deliver high quality.
7. Load only the skills relevant to the current task.
8. Run available validation commands when practical.
9. Stop before destructive, production, security-sensitive, privacy-sensitive, customer-impacting, or cost-increasing actions unless explicitly approved.

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
docs/ai/project-profile.md       Project identity, stack, architecture, paths, environments
docs/ai/commands.md              Verified commands only
docs/ai/conventions.md           Code, architecture, UX, testing, docs conventions
docs/ai/risks.md                 Security, privacy, cost, operational, UX/product risks
docs/ai/decision-log.md          Durable architecture/product/technical decisions
docs/ai/shared-context.md        Cross-session and cross-tool context that must not be lost
docs/ai/tasks/                   Task-specific context, plan, gates, validation and handoff
```

If a detail matters but no existing file fits, create or update the smallest appropriate `docs/ai` file and explain why.

---

## 2. Source-of-truth hierarchy

When sources conflict, use this order:

1. User's latest explicit instruction.
2. Safety/security constraints and explicit approval boundaries.
3. Repository files and current code.
4. `docs/ai` project memory.
5. Existing tests and CI configuration.
6. Previous task files and decision log.
7. General best practices.

Never invent commands, architecture, or business rules. Mark unknowns explicitly.

---

## 3. Context ingress protocol

For every non-trivial task, create a compact written context packet before making changes.

For Level 0 and Level 1, this can be a short internal note in the response or task scratchpad.
For Level 2 and Level 3, create or update a task file:

```text
docs/ai/tasks/YYYY-MM-DD-short-task-name.md
```

The context packet must include, as applicable:

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
→ Context packet
→ Requirements / Mini PRD
→ Architecture/UML review when triggered
→ Specialist gates when triggered
→ Implementation
→ Tests / validation
→ Release / rollback / monitoring when triggered
→ Handoff notes
```

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
Intent → Relevant context → Implement → Validate → Short summary
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
Intent → Written context packet → Mini PRD → Technical plan → Implement → Tests → Validation summary → Handoff notes
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
→ Written context packet
→ PRD
→ Architecture/UML review
→ Required specialist gates
→ Implementation plan
→ Human approval when required
→ Implementation
→ Tests
→ Validation
→ Release, monitoring and rollback plan
→ Handoff notes
```

Human approval is required before destructive, production, security-sensitive, privacy-sensitive, customer-impacting, or cost-increasing execution.

---

## 9. Software engineering and architecture standards

Use robust software engineering standards, proportional to task level.

Default principles:

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

---

## 10. Skill loading policy

Load skills only when needed.

Core skills:

```text
.agents/skills/core/project-profiling/SKILL.md
.agents/skills/core/task-triage/SKILL.md
.agents/skills/core/context-memory/SKILL.md
.agents/skills/core/implementation/SKILL.md
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

### UX/Product gate

Use when there is any interface, workflow, product flow, onboarding, dashboard, form, empty state, error state, pricing page, guided tour, notification, or user-facing copy.

### Security/Compliance gate

Use when there are credentials, auth, permissions, external input, public endpoints, file uploads, customer data, personal data, logs, third-party transfer, or production impact.

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

If commands cannot run, explain why and provide a manual validation checklist.

Do not claim validation passed unless it actually ran successfully.

Validation depth by level:

- Level 0: targeted local/manual validation is acceptable.
- Level 1: relevant lint/test/manual check.
- Level 2: tests plus integration/edge-case validation where relevant.
- Level 3: full relevant validation, rollback plan, monitoring plan, and residual risk statement.

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

| Legacy responsibility | Covered by v3.1 gate/skill | Notes |
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
