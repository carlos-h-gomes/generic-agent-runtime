# Profile-Driven Release Checklist

Owned by `specialists/observability-release`. Copy an evidence index into the active Level 3 task; do not check boxes without proof.

`[B]` blocks an applicable release. `[R]` may be deferred with reason, owner, and due point. Every `Not applicable` entry needs a project-specific reason. Project-defined SLO, RTO/RPO, backup, rollback, and monitoring targets replace generic fixed numbers.

## Part A — Launch or major-change readiness

### Delivery and recovery

- [ ] [B] Build/release identity and provenance are reproducible.
- [ ] [B] Environments, credentials, and data stores are appropriately isolated.
- [ ] [B] Forward and rollback/restore procedures were tested against the declared objectives.
- [ ] [B] Configuration, schema, and compatibility order are documented.
- [ ] [R] Staged/canary or feature-flag rollout limits blast radius where useful.

### Security, privacy, and supply chain

- [ ] [B] Fresh `security_compliance` result has no blocker; auth/resource isolation and public entrypoints were tested when applicable.
- [ ] [B] Secrets are outside code/build output/logs and have scoped rotation/revocation procedures.
- [ ] [B] Dependencies, tools, skills, and deployment inputs have recorded provenance and applicable scan evidence.
- [ ] [B] Personal/customer data purpose, minimization, access, retention, deletion, and third-party transfers are recorded when applicable.
- [ ] [R] Legal/compliance owner reviewed jurisdiction-specific obligations when triggered.

### Data, integrations, payments, and AI

- [ ] [B] Fresh `data_integration` result covers contracts, validation, idempotency/retries/replay, migrations, and recovery where applicable.
- [ ] [B] Inbound authenticity and replay protection are tested with synthetic or provider-sanitized fixtures.
- [ ] [B] Payment/money flows verify authenticity, idempotency, auditability, and failure handling.
- [ ] [B] A production financial smoke transaction is used only when the provider permits it and an authorized human explicitly approves scope; reversal/refund/void and sanitized evidence are recorded.
- [ ] [B] Fresh `ai_llm` result covers schema validation, grounding/fallback, tool policy, eval thresholds, memory, budgets, and residual injection risk when applicable.

### Operations and cost

- [ ] [B] Success/failure SLIs and applicable SLO/RTO/RPO targets are defined.
- [ ] [B] Safe logs, metrics, traces/correlation, alerts, owners, escalation, and runbook exist.
- [ ] [B] Fresh `finops` result defines worst-case exposure, hard caps, alert actions, degradation, and kill switch for variable-cost paths.
- [ ] [B] Incident criteria, containment, communication, and post-incident ownership are known.
- [ ] [R] Restore, rollback, and incident exercises are repeated at the project-defined cadence.

## Part B — Every production release

- [ ] [B] Target revision/artifact and change summary are identified.
- [ ] [B] Relevant validation and required gate results passed on that state; skips and residual risks are accepted by the proper owner.
- [ ] [B] Migrations/config/secrets and compatibility order were reviewed without exposing values.
- [ ] [B] Scoped production approval is recorded before execution.
- [ ] [B] Rollback trigger, procedure, and operator are named before deploy.
- [ ] [B] Synthetic/sanitized smoke checks and restored-state checks are selected.
- [ ] [R] Staging/canary/flag plan is ready.
- [ ] [R] Monitoring window, signals, owner, and stakeholder communication are set.

## Evidence index

```text
Release/artifact:
Target environment:
Approved action and approver reference:
Required GateResult paths/revisions:
Validation evidence pointers:
Rollback/restore evidence:
Monitoring window and owner:
Not applicable items and reasons:
Deferred recommended items, owner, due point:
Residual risks:
```
