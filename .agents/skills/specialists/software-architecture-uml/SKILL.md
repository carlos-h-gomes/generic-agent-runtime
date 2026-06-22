---
name: software-architecture-uml
description: "Define sound architecture and produce lightweight C4/UML models BEFORE implementation for Level 2/3 work that changes module boundaries, data models, public contracts, integrations, workflows, queues, jobs, deployment topology or other cross-cutting concerns. Use when a refactor touches multiple modules or a new API/event/schema/business workflow is introduced. Implementation must wait for this artifact; it must not invent architecture itself."
---

# Software Architecture and UML Specialist

## Objective

Ensure medium and critical changes are architecturally sound, maintainable, secure by design, and understandable through lightweight UML/C4 models when useful.

## When to use

- Level 2/3 tasks affecting architecture, modules, shared services, data models, public contracts, integrations, workflows, deployment, or cross-cutting concerns.
- Refactors touching multiple modules.
- New APIs, jobs, events, queues, schemas, or business workflows.

## When not to use

- Pure copy changes.
- Small isolated bug fixes with no design impact.

## Inputs expected

- User request and acceptance criteria.
- Project profile and conventions.
- Existing architecture/code paths.
- Data and integration contracts.
- Security/privacy/cost constraints.
- Files likely to be modified.

## Process

1. Identify system boundaries and actors.
2. Identify modules/components and responsibilities.
3. Identify data ownership and lifecycle.
4. Identify synchronous/asynchronous flows.
5. Identify state transitions and failure modes.
6. Identify trust boundaries and external dependencies.
7. Choose the smallest useful model:
   - C4 context/container for boundaries.
   - UML component for module structure.
   - UML sequence for workflow/integration behavior.
   - UML class/domain model for entities/contracts.
   - UML state for lifecycle/status behavior.
   - Deployment diagram for runtime topology.
8. Check SOLID, cohesion/coupling, dependency direction, and testability.
9. Record the model or decision in the task file or architecture docs.

## Deliverables

- Architecture summary.
- Selected UML/C4 view or reason no diagram is needed.
- Boundary and dependency notes.
- Risks and mitigations.
- Implementation constraints.

## Quality criteria

- Design is simpler than the problem, not simpler than reality.
- Dependencies are intentional.
- Contracts are explicit.
- Failure paths are visible.
- The model helps implementation, review, or maintenance.


## Written memory rule

For Level 2/3 work, record durable findings, assumptions, risks, and handoff notes in the active task file or the appropriate `docs/ai` file. Do not rely on mental notes.

## Checklist

- [ ] Boundaries mapped.
- [ ] Responsibilities clear.
- [ ] Dependencies reviewed.
- [ ] Data ownership reviewed.
- [ ] Failure paths reviewed.
- [ ] Appropriate UML/C4 view used or skipped with reason.
- [ ] Testability considered.
