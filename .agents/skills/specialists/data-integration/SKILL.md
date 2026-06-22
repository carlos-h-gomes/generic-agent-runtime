---
name: data-integration
description: "Make integrations, automations, data flows, schemas and pipelines reliable, traceable, idempotent and reprocessable. Use for APIs, webhooks, n8n/workflow automations, ETL/ELT, databases, migrations, queues, events, spreadsheets, dashboards or any external-system boundary. Defines contracts/schemas, idempotency keys, retry/timeout/rate-limit behavior, error handling, reprocessing and correlation logging."
---

# Data and Integration Specialist

## Objective

Ensure integrations, automations, data flows, schemas and pipelines are reliable, traceable, idempotent and maintainable.

## When to use

- APIs.
- Webhooks.
- n8n workflows.
- ETL/ELT.
- Databases.
- Migrations.
- Queues.
- Events.
- Spreadsheets.
- Dashboards.
- External systems.

## Process

1. Map source, destination and transformation.
2. Define contract/schema.
3. Identify idempotency key.
4. Define retry, timeout and rate-limit behavior.
5. Define error handling and fallback.
6. Define reprocessing strategy.
7. Define data quality checks.
8. Define logging and correlation ID.
9. Consider volume and performance.
10. Consider retention and access.

## Deliverables

- Data/integration contract.
- Failure-mode plan.
- Reprocessing plan.
- Validation checklist.

## Quality criteria

- No ambiguous payloads.
- No duplicate processing risk left unaddressed.
- Failures are observable.
- Reprocessing is possible for important flows.


## Written memory rule

For Level 2/3 work, record durable findings, assumptions, risks, and handoff notes in the active task file or the appropriate `docs/ai` file. Do not rely on mental notes.

## Checklist

- [ ] Source/destination mapped.
- [ ] Schema/contract defined.
- [ ] Idempotency considered.
- [ ] Retries/timeouts considered.
- [ ] Rate limits considered.
- [ ] Error handling considered.
- [ ] Reprocessing considered.
- [ ] Data quality considered.
- [ ] Logs/correlation considered.
