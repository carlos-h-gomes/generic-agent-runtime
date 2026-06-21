# Project Conventions

Status: template. Fill during Project Profiling.

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
