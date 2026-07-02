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


## Autonomous reflection loop

For spec-driven implementation work, validation must be attempted before the task is sent to human review when safe validation commands exist.

Default loop:

```text
core/implementation
→ specialists/code-quality-testing runs ./scripts/test.sh and ./scripts/lint.sh
→ failing stdout/stderr is returned to core/implementation
→ core/implementation corrects the issue
→ specialists/code-quality-testing reruns validation
```

Maximum attempts: **3 implementation/testing loops**.

Stop conditions:

- Stop as `passed` when the required validation commands pass.
- Stop as `blocked` when validation cannot run because commands, dependencies, environment, secrets, or approval are missing.
- Stop as `paused_for_human_review` after 3 failed loops.

When paused for human review, the task handoff must include:

- attempts used;
- changed files;
- commands run;
- last failing command;
- exit code;
- actionable stderr/failure output;
- what the human should inspect first.

Agents must not ask the human to review code that is known to be broken until this loop has run or a clear reason is documented for why it cannot run.

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

Required for auth, external input, public endpoints, secrets, customer data, personal data, logs, files, third-party data transfer, or dependency/supply-chain changes.

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
- Dependency/supply-chain risk considered (SCA run or pinned versions) when dependencies change.
- For agent/tool/RAG/memory features: OWASP ASI Top 10 (2026) reviewed — external content treated as untrusted, tools least-privilege, code execution sandboxed, human-in-the-loop on state-mutating actions, loop/attempt caps and a stop path present.

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
- For production launches/deploys: applicable items of `docs/ai/release-checklist.md` completed (Blockers) or marked not applicable with a reason; deferred Recommended items have an owner.
