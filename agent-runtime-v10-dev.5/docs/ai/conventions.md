# Project Conventions

Status: initialize from repository evidence and the user's recorded choices.

## Architecture selection

- Brownfield work preserves the verified language, frameworks, topology, package/runtime, commands, and deployment model unless a separate migration is authorized.
- Greenfield work reuses any choice the user already made. If a material choice is missing, recommend relevant options with concise reasons and tradeoffs, then wait for the user's decision before generating application code.
- Record the selected or observed architecture in `docs/ai/architecture-policy.json` using the open architecture profile. Declare roots, modules, responsibilities, permitted dependencies, composition roots, contracts, tests, and extensions.
- Do not infer a language or framework from the Harness implementation language. The bundled Python/FastAPI and React/TypeScript template is optional.
- Prefer the smallest structure that expresses real ownership boundaries. Avoid both one-file feature containers and speculative layers with no current responsibility.

## Reuse before creation

- Inventory existing modules, contracts, tests, utilities, dependencies, documentation, and generated clients before proposing new code.
- Classify relevant assets as `reuse`, `extend`, `adapt`, `replace`, or `new`, with evidence and compatibility notes.
- Prefer reuse or a narrow extension when behavior, ownership, security, license, and support constraints remain compatible.
- Replacement requires an explicit reason, migration and rollback treatment, and characterization tests where existing behavior matters.
- Never duplicate an existing responsibility merely because a new implementation is easier to generate.

## Open solution placement

- Material integrations and automations use `schemas/solution-decision.schema.json`; categories and tool names are open.
- The user owns technology choice. Recommend options from requirements and verified project context, not from a fixed code/workflow/hybrid menu.
- Every component declares responsibility, authority, system of record, interfaces, reliability, security, cost, operations, rollback, and kill switch.
- Connectors, visual workflows, managed services, agents, database features, and generated code gain no business authority by convenience.
- Tool-specific profiles apply only after selection. The retained n8n policy is one optional compatibility profile.

## Topology and dependency rules

The architecture profile is the machine-readable minimum, not a universal directory tree. Every declared root and required path must exist; every module must have one coherent responsibility, explicit permitted dependencies, and owned tests. Additional directories are allowed when their responsibility and direction are recorded.

Dependency direction must point toward stable contracts and owned domain behavior. Transport, UI, persistence, workflow, provider, and framework adapters must not become accidental authorities. Cross-boundary communication uses declared, versioned contracts with authentication, authorization, validation, stable errors, timeouts, volume limits, observability, and compatibility behavior where applicable.

When the optional Python/React template is selected, its version-1 profile retains the detailed `backend/app/controllers -> services -> models/repositories` direction and the frontend `api`, `services`, `pages`, `components`, `hooks`, `context`, `data`, and `utils` responsibilities documented in `docs/harness/HYBRID-ARCHITECTURE.md`.

## Entrypoints and anti-monolith rule

Application entrypoints such as `App.jsx`, `App.tsx`, `main.py`, `server.py`, `index.ts`, and ecosystem equivalents may exist only as thin composition roots. They may construct the application, register routes or handlers, middleware, providers, layouts, and process startup. They may not own route implementations, persistence queries, direct external transport, business rules, large state machines, feature datasets, reusable UI implementations, or undeclared feature symbols.

When asked to create a single-file monolith, explain the violated ownership rule and propose a compliant decomposition. Do not reject a valid thin entrypoint merely because of its filename, and do not force a layer-oriented tree when feature-oriented or ecosystem-native modules express the chosen architecture better.

## Source of truth and documentation

- Read `SOURCE-OF-TRUTH.md` after `AGENTS.md` and before an active task. It identifies which detailed source owns each material project fact.
- A missing material fact is unverified, not permission to delete or rebuild verified work. Reconcile code, schemas, tests, tasks, and decisions first.
- Every task classifies documentation impact as `none`, `technical`, `user_manual`, or `both` with a reason.
- Update technical documentation on material architecture, API, data, configuration, security, deployment, operations, or migration changes.
- Update the user manual on user-visible features, workflows, navigation, permissions, feedback, recovery, accessibility, or support changes.
- `docs/TECHNICAL-DOCUMENTATION.md` and `docs/USER-MANUAL.md` must be current, reviewed, placeholder-free, and version-aligned before an official release.

## Project-specific extensions

| Path or rule | Responsibility | Permitted dependencies | Owner/evidence |
|---|---|---|---|

## Formatting, testing, and evidence

- Record verified install, lint, typecheck, test, build, security, architecture, documentation, and release commands in `docs/ai/commands.md`.
- Prefer focused unit tests within each boundary plus contract, integration, accessibility, and end-to-end coverage where risk requires it.
- Never store credentials, customer data, private prompts, full logs, or unredacted production evidence in project memory or documentation.
