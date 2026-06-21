# Quality Gates

Use gates only when triggered by task scope or risk.

## Universal minimum

- The change matches the user's request.
- The smallest safe change was made.
- Existing patterns were respected.
- Durable context was written when needed.
- No important detail was kept only as a mental note.
- Validation was run or a clear reason was given.
- Known risks and limitations were disclosed.

## Architecture / UML gate

Required for Level 2/3 tasks that affect module boundaries, workflows, data models, contracts, integrations, deployment, or cross-cutting concerns.

Pass conditions:

- System boundary is clear.
- Responsibilities are assigned to the right modules/services.
- Dependencies point in the intended direction.
- Contracts and data ownership are clear.
- Error and failure paths are modeled.
- Appropriate C4/UML view was created or explicitly deemed unnecessary.
- Backward compatibility was considered.

## Code quality / testing gate

Required for meaningful business logic, shared utilities, refactors, or edge-case-heavy changes.

Pass conditions:

- SOLID/Clean Code concerns reviewed.
- Complexity is justified.
- Edge cases identified.
- Tests added or updated where practical.
- No new dependency without justification.
- No hidden side effects.

## UX gate

Required for user-facing screens, forms, flows, dashboards, onboarding, guided tours, pricing, empty states, error states, or copy.

Pass conditions:

- Primary user goal is obvious.
- Main action is visually clear.
- Layout works across target screen sizes.
- States exist: loading, empty, error, success, disabled where applicable.
- User can recover from mistakes.
- Copy uses user language, not internal jargon.
- Accessibility basics are respected.
- Visual hierarchy is intentional.
- Design is consistent with the product identity.

## Security/compliance gate

Required for auth, external input, public endpoints, secrets, customer data, personal data, logs, files, or third-party data transfer.

Pass conditions:

- Trust boundaries mapped.
- Inputs validated.
- Authorization checked.
- Secrets not exposed.
- Sensitive logs avoided.
- Data minimized.
- Retention considered.
- Third-party transfer identified.
- Abuse cases considered.

## Data/integration gate

Required for APIs, webhooks, databases, ETL/ELT, queues, events, spreadsheets, dashboards.

Pass conditions:

- Source and destination clear.
- Contract/schema clear.
- Idempotency considered.
- Retries/timeouts considered.
- Rate limits considered.
- Reprocessing path considered.
- Correlation/logging considered.

## FinOps gate

Required for LLMs, paid APIs, cloud resources, storage, recurring jobs, high volume, OCR, embeddings, scraping, dashboards, logs.

Pass conditions:

- Unit of cost known or marked unknown.
- Volume estimate recorded when relevant.
- Limit or guardrail exists.
- Risk of loops/explosive calls considered.
- Cache/batching/deduplication considered.
- Fallback/degradation considered.

## Observability/release gate

Required for production, endpoints, jobs, automations, customer impact, deploys, rollback, SLAs.

Pass conditions:

- Logs are useful and safe.
- Correlation ID considered where useful.
- Success/error metrics considered.
- Alert path considered.
- Rollback path clear for risky changes.
- Post-release monitoring considered.
