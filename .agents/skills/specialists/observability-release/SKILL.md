---
name: observability-release
description: "Ensure production-impacting changes can be deployed, monitored, diagnosed and rolled back safely. Use for production changes, public/internal endpoints, jobs, automations, customer-impacting flows, SLAs, deployments and incident-prone systems. Defines success/error signals, safe logs, metrics, alert paths, deployment and rollback plans, post-release monitoring window and incident response path."
---

# Observability and Release Specialist

## Objective

Ensure production-impacting changes can be deployed, monitored, diagnosed and rolled back safely.

## When to use

- Production changes.
- Public/internal endpoints.
- Jobs.
- Automations.
- Customer-impacting flows.
- SLAs.
- Deployments.
- Rollbacks.
- Incident-prone systems.

## Process

1. Identify success and failure signals.
2. Define logs needed to debug without leaking sensitive data.
3. Define metrics and thresholds.
4. Define alert path.
5. Define deployment plan.
6. Define rollback plan.
7. Define post-release monitoring window.
8. Define incident response owner/path when relevant.

## Deliverables

- Observability checklist.
- Release checklist: this gate owns `docs/ai/release-checklist.md`. Run Part A (launch readiness) before the first production launch and re-audit on major changes; run Part B (per-release) on every production deploy. Record how each Blocker was verified; mark inapplicable items `Not applicable — reason: ...`.
- Rollback plan.
- Incident notes when relevant.

## Quality criteria

- A human can detect failure.
- A human can diagnose failure.
- A human can roll back or mitigate.
- Logs are useful and safe.


## Written memory rule

For Level 2/3 work, record durable findings, assumptions, risks, and handoff notes in the active task file or the appropriate `docs/ai` file. Do not rely on mental notes.

## Checklist

- [ ] Success signal defined.
- [ ] Error signal defined.
- [ ] Logs defined.
- [ ] Metrics considered.
- [ ] Alerts considered.
- [ ] Rollback defined.
- [ ] Post-release monitoring considered.
- [ ] `docs/ai/release-checklist.md` Part A/B applied when this is a production launch or deploy.
