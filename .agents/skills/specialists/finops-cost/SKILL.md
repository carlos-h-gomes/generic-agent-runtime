---
name: finops-cost
description: "Explicit specialist review for paid APIs, models, compute, storage, network, recurring jobs, or high-volume variable cost."
---

# FinOps and cost gate

Return a `GateResult` conforming to `schemas/gate-result.schema.json`.

## Cost model

Record an authoritative pricing source, currency, region, version/date checked, and billing units. Estimate expected, burst, and worst-case volume with an explicit formula and uncertainty. Include applicable:

- input/output/cached tokens, requests, tool steps, retries, and parallel agents;
- compute duration, concurrency, storage, retention, egress, queues, and log cardinality;
- loops, fan-out, duplicate work, replay, and failure amplification;
- per-request/user/job cost plus daily/monthly exposure.

Do not guess current prices. Mark unknown pricing or volume and show the formula needed once known.

## Guardrails

Define hard caps separately from provider quotas and alert thresholds. Assign each alert an owner and automatic action. Prefer prevention: request and token limits, bounded concurrency/retries, cache with correct keys/expiry, batching, deduplication, sampling/cardinality controls, storage lifecycle, circuit breakers, degradation, and a kill switch.

For multi-agent work, estimate total root plus worker tokens and tool calls; parallelism must earn its additional cost through evaluated speed or coverage.

Evidence may include dated pricing links, formulas, aggregate usage, and cost regression results. Never record account IDs, invoices, billing credentials, or customer-level usage.

Block cost-increasing execution when worst-case exposure is unbounded, a material increase lacks approval, or no owner/kill switch exists. Security and product constraints take precedence over savings.

For every selected component include its license/edition, execution or request units, workers, concurrency, retries, replay, retention, storage, egress, and external API billing units. A solution cannot be approved while material pricing or volume remains unknown unless cost is demonstrably not applicable. Apply vendor-specific fields only through an optional profile.
