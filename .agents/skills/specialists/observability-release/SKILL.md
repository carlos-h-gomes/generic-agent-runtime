---
name: observability-release
description: "Explicit specialist review for production rollout, telemetry, alerts, rollback, incident response, or operational readiness."
---

# Observability and release gate

Return a pre-release `GateResult` conforming to `schemas/gate-result.schema.json`. Consume required specialist conclusions; never override another gate's blocker.

## Operational contract

Define applicable:

- success/failure SLIs, SLOs, error budgets, latency, throughput, freshness, and correctness;
- RTO/RPO and restore objectives;
- structured safe logs, metrics, traces, correlation propagation, sampling, retention, and cardinality controls;
- alert threshold, duration, route, owner, escalation, and runbook;
- deployment strategy, compatibility order, feature flag/canary, and blast-radius limit;
- smoke checks, rollback trigger, rollback command/procedure, and restored-state verification;
- monitoring window, named owner, incident criteria, containment, and communication path.

Use `docs/ai/release-checklist.md` as a profile-driven evidence index. Mark a blocker `Not applicable` only with a project-specific reason. Production, destructive, customer-impacting, or release-process execution still requires the approval defined by `AGENTS.md`.

Evidence may point to dashboards/queries, sanitized sample logs, deployment identifiers, runbooks, smoke/rollback/restore summaries, and monitoring timestamps. Use synthetic/sanitized transactions; a real financial transaction requires explicit scoped approval plus reversal/refund/void evidence.

Block release when required gates are stale/blocked, rollback is not credible, required alerts have no owner, or the production action lacks approval.

For n8n or hybrid workflows require correlation propagation, bounded execution retention, error workflow/dead-letter behavior, alert ownership, protected promotion, reviewed workflow identity, rollback export, instance/database restore evidence, and an activation kill switch. Workflow history alone is not durable business audit evidence.
