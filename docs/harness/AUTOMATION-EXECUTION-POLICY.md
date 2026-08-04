# Automation execution-plane policy

Version: 1.0  
Applies to: Harness 7 application and integration work

## Decision rule

Code is the authoritative execution plane. n8n is a bounded edge-orchestration plane. Use `hybrid` when visual orchestration calls versioned code services that retain business authority.

Every material automation records a decision conforming to `schemas/automation-decision.schema.json`. Unknown ownership, reliability, security, cost, or production controls keeps the decision in `draft`; it does not default to n8n.

## Hard blockers

An automation cannot be `n8n` when it owns any of the following:

- authorization, tenant isolation, entitlements, or permissions;
- financial, ledger, inventory, or other transactional invariants;
- strict latency/throughput or complex concurrency/state requirements;
- intensive computation, large data movement, or unbounded loops/fan-out;
- controls that the selected n8n edition or deployment cannot provide;
- unbounded cost, replay, retention, or failure amplification.

Route the whole workload to `code`, or select `hybrid` and extract every blocked responsibility behind a versioned API. The n8n Code node, Execute Command, SSH, filesystem nodes, community nodes, or custom nodes are not an acceptable way to bypass a hard blocker.

## n8n eligibility

n8n is eligible only when the workflow is bounded edge orchestration of webhooks, schedules, events, queues, files, or external APIs; authoritative rules remain in code or an external system of record; side effects are idempotent; and visual operation has clear value.

Before production activation require:

1. A sanitized workflow export in version control. Never commit credentials or credential values.
2. A development-to-production promotion path with a protected production instance or equivalent external controls. Do not edit production directly.
3. Versioned input/output contracts and rejection without side effects on invalid data.
4. Authentication, least-privilege credentials, tenant/resource checks at the authoritative service, request limits, SSRF/egress controls, and safe errors.
5. Bounded timeouts, attempts, backoff, concurrency, replay, and retention; an idempotency key and reconciliation owner.
6. An error workflow or equivalent dead-letter path, correlation propagation, safe logs/metrics, alert owner, rollback, and kill switch.
7. A reviewed inventory of risky, community, custom, Code, command, file, and network-capable nodes.
8. Dated edition/version capability evidence, backup of the n8n database and encryption material, and a tested restore procedure.
9. Expected, burst, and worst-case billing units; hard caps, alerts, degradation, and failure-amplification limits. Do not guess unknown prices.

n8n execution history is operational evidence, not the product system of record or a regulatory ledger. Deleting workflows or applying retention may remove it; authoritative audit records belong in an owned durable system.

## Outcome semantics

- `code`: code owns orchestration and authority; n8n is absent.
- `n8n`: all hard blockers are absent, the authoritative state is external, and every n8n production control is evidenced.
- `hybrid`: n8n owns bounded coordination only; code APIs own blocked or authoritative behavior.
- `undecided`: required facts or approvals are missing. No production workflow may be activated.

The security, data, FinOps, architecture, code-quality, and release gates remain independent. Passing this decision schema does not prove a workflow or deployment is secure or reliable.

## Current official capability references

- n8n source control and environments: <https://docs.n8n.io/source-control-environments/create-environments/> (checked 2026-08-04).
- n8n security audit: <https://docs.n8n.io/hosting/securing/security-audit/> (checked 2026-08-04).
- n8n execution history and retry behavior: <https://docs.n8n.io/workflows/executions/all-executions/> (checked 2026-08-04).
- n8n workflow sharing and credential implications: <https://docs.n8n.io/workflows/sharing/> (checked 2026-08-04).

Recheck living capabilities, editions, supported versions, security guidance, and pricing before every downstream release.
