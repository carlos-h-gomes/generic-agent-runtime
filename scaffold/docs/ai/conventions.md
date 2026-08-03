# Project Conventions

Status: initialize project-specific extensions while preserving this mandatory minimum.

## Hybrid architecture floor

- Application projects use two isolated boundaries: a Python HTTP API under `backend/` and a React client under `frontend/`.
- FastAPI is the default backend framework. Flask is compatible only with modular Blueprints and the same controllers/services/models separation.
- React uses TypeScript and Vite by default. A different React toolchain needs an architecture decision and supported dependency evidence.
- Frontend and backend do not import or execute each other's source. Integration uses a versioned HTTP contract, normally OpenAPI.
- Authoritative business rules, resource authorization, and persistence remain in the backend. The frontend owns presentation, interaction state, navigation, and browser-side orchestration.

## Required minimum topology

Backend required paths:

```text
backend/app/main.py
backend/app/controllers/
backend/app/services/
backend/app/models/
backend/app/schemas/
backend/app/repositories/
backend/tests/
```

Frontend required paths:

```text
frontend/src/api/
frontend/src/assets/
frontend/src/components/layout/
frontend/src/components/ui/
frontend/src/context/
frontend/src/data/
frontend/src/hooks/
frontend/src/pages/
frontend/src/services/
frontend/src/utils/
frontend/tests/
```

These paths are a minimum required subset, not an allowlist. Additional feature, provider, route, type, configuration, domain, adapter, job, or integration directories are allowed when they have a distinct responsibility. Record every new top-level architectural layer, its owner, and permitted dependencies in this file or `docs/architecture/DIRECTORY-MAP.md`.

## Dependency and responsibility rules

- Backend direction is `controllers -> services -> models/repositories`; DTO validation belongs in `schemas`.
- Controllers map HTTP input/output and transport errors. They do not contain business rules, database queries, or third-party workflows.
- Services own use cases and business rules. Repositories own persistence adapters. Models do not depend on controllers or services.
- Frontend `api` owns HTTP transport and generated clients. Frontend `services` own presentation-side orchestration, not authoritative server rules.
- Pages compose routes; components are reusable UI; hooks own reusable React behavior; context is reserved for genuine cross-tree state; data contains static or synthetic content; utils remain pure.
- Utilities cannot import React, pages, context, services, or API transport. Components cannot depend on pages. API transport cannot depend on UI.

## Entrypoints and anti-monolith rule

`App.jsx`, `App.tsx`, `main.py`, and `server.py` may exist only as thin composition roots. They may construct the application, register routes, middleware, providers, layouts, and process startup. They may not contain route implementations, persistence, direct HTTP clients, business rules, large state machines, feature datasets, or reusable UI implementations.

When asked to create a single-file monolith, refuse that constraint, explain the violated ownership rule, and propose a compliant decomposition. Do not refuse a valid thin entrypoint merely because of its filename.

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
- Prefer focused unit tests within each boundary plus API contract, integration, accessibility, and end-to-end coverage where the risk requires it.
- Never store credentials, customer data, private prompts, full logs, or unredacted production evidence in project memory or documentation.
