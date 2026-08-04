---
name: data-integration
description: "Explicit specialist review for APIs, webhooks, schemas, migrations, queues, ETL, spreadsheets, or external-system boundaries."
---

# Data and integration gate

Return a `GateResult` conforming to `schemas/gate-result.schema.json`.

## Define the contract

- source, destination, system of record, owner, and trust boundary;
- schema, required fields, types, nullability, constraints, examples, and versioning;
- validation and rejection behavior at every boundary;
- compatibility policy and consumer migration order;
- identifiers, timestamps/time zones, units/currency, retention, and deletion inputs;
- delivery semantics, ordering, deduplication, and idempotency key/window when applicable.

## Define reliability

- timeout, bounded retry/backoff/jitter, rate limit, and backpressure;
- transaction, outbox/saga, dead-letter, poison-event, and partial-failure behavior where relevant;
- replay/reprocessing safety, checkpoints, and audit/correlation propagation;
- data quality checks, reconciliation, ownership, and alert handoff;
- forward/rollback migration and restore evidence.

Use synthetic or sanitized payloads. Evidence may point to schemas, migrations, contract/idempotency/replay tests, and aggregate counts; never persist real tokens, customer records, webhook payloads, or unrestricted database exports.

Block implementation when source of truth, schema compatibility, failure/replay semantics, or data-loss behavior is unresolved. Architecture owns system-wide boundaries; Security owns retention/access decisions; Observability owns alerts; FinOps owns cost budgets.

For n8n or hybrid workflows, require the automation decision contract, sanitized versioned export, explicit system of record, idempotency key/window, bounded retry, poison-event/error path, replay safety, reconciliation owner, and versioned API boundary. n8n execution history is not an authoritative ledger.
