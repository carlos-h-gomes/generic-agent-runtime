# Project Conventions

Status: template. Fill during Project Profiling.


## Product and architecture pipeline order

For any new feature or meaningful behavior change, agents must follow this order before implementation:

```text
task-triage → UX/Product when user-facing → Software Architecture/UML when architecture/data/integration/deployment is affected → implementation → code-quality-testing → validation/handoff
```

Rules:

- User-facing features must pass through `specialists/ux-product` before implementation.
- Features that affect database behavior, schemas, integrations, n8n flows, Caddy/reverse-proxy behavior, deployment topology, external contracts, queues, jobs, or cross-cutting workflows must pass through `specialists/software-architecture-uml` before implementation.
- The architecture specialist must produce a Markdown artifact in the active task file or architecture docs, using Mermaid/C4/UML when useful.
- Implementation is prohibited from inventing architecture for new features. Its job is to code the architecture and contracts that were defined by the architecture artifact.
- If the implementation agent finds the architecture missing, ambiguous, or incompatible with the codebase, it must return the task to `task-triage` or `software-architecture-uml` instead of guessing.
- For small local changes with no architecture, data, integration, deployment, or user-facing impact, mark these gates as not applicable with a short reason.

## Architecture conventions

- Style: layered / clean architecture / MVC / feature folders / service-oriented / event-driven / other
- Module boundaries:
- Dependency direction:
- Shared utilities:
- External service abstraction:
- Error boundary strategy:

## UML / modeling conventions

Use lightweight text diagrams when they clarify implementation.

- C4 context/container view for boundaries.
- UML component diagram for modules/services.
- UML sequence diagram for workflows and integrations.
- UML class/domain model for entities and contracts.
- UML state diagram for statuses and lifecycle transitions.
- Deployment diagram for infra and runtime topology.

Do not create diagrams that do not help the task.

## Code style

- Language conventions:
- Formatting:
- Naming:
- Error handling:
- Logging:
- Comments:
- Dependency policy:

## Frontend conventions

- Component structure:
- Styling:
- State management:
- Forms:
- Validation:
- Accessibility:
- Responsiveness:

## Backend conventions

- API style:
- DTO/schema validation:
- Service boundaries:
- Error responses:
- Auth/authorization:
- Rate limiting:

## Data conventions

- Schema naming:
- Migrations:
- Idempotency:
- Reprocessing:
- Retention:
- Auditability:

## Testing conventions

- Unit:
- Integration:
- E2E:
- Contract tests:
- Manual validation:

## Documentation conventions

- Update docs only for durable decisions, contracts, operations, risks, architecture changes, or cross-tool handoffs.
- Put task-specific context in `docs/ai/tasks/`.
- Put durable decisions in `docs/ai/decision-log.md`.
