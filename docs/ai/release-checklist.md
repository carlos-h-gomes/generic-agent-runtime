# Profile-Driven Release Checklist

`[B]` blocks an applicable release. `[R]` may be deferred only with reason, owner, and due point. Every `not applicable` entry needs a project-specific reason.

## Identity and recovery

- [ ] [B] `SOURCE-OF-TRUTH.md` identifies the current product version, architecture profile, authoritative sources, active work, material risks, and last qualified evidence.
- [ ] [B] Revision, artifact digest, SBOM, provenance, environment, and owner are identified.
- [ ] [B] Reproducible build/install mode and lockfile are evidenced.
- [ ] [B] Rollback or restore was exercised against declared objectives.
- [ ] [B] Configuration and migration compatibility order is documented.

## Security and containment

- [ ] [B] `docs/harness/PRODUCT-SECURITY-PRIVACY.md` was applied; every unknown or unavailable applicable control remains incomplete rather than passed.
- [ ] [B] Security policy is current; runtime/framework pins satisfy it.
- [ ] [B] Fresh dependency, secret, and SAST results have no unresolved high/critical finding.
- [ ] [B] Threat model covers public entrypoints, trust boundaries, server-side resource/tenant/function authorization, sessions/recovery, upload/render paths, injection, SSRF/RCE, dependency scripts, API inventory/webhooks, and agent tools where applicable.
- [ ] [B] Authentication, account recovery, privileged MFA, session rotation/expiry/revocation, secure cookies, CSRF, CORS, browser headers, and anti-enumeration controls are evidenced where applicable.
- [ ] [B] Request/body/file/query/pagination/batch/response/time/concurrency limits and rate/volume quotas cover source, account, tenant, operation, destination, and cost dimensions where applicable.
- [ ] [B] Sensitive business flows have explicit anti-automation, replay/idempotency, fraud/abuse monitoring, degradation, reconciliation, and kill-switch decisions.
- [ ] [B] Secrets are absent from source/build/logs and have scoped rotation/revocation procedures.
- [ ] [B] Production runs as non-root with minimum filesystem/process/network authority and resource quotas.
- [ ] [B] Incident response names containment, credential rotation, rebuild, evidence, communication, and owner.
- [ ] [B] Adversarial traffic, if any, used an exact, bounded, unexpired authorized target contract.

## Privacy and personal data

- [ ] [B] Personal-data categories, sources, purposes, systems of record, controller/operator/suboperator roles, recipients, jurisdictions, owners, and applicable legal-basis inputs are recorded.
- [ ] [B] Necessity and minimization cover product fields, telemetry, logs, prompts/model context, analytics, support, test data, backups, and exports.
- [ ] [B] Privacy notice and data-subject workflows cover applicable access, correction, sharing information, consent withdrawal, opposition, automated-decision review, deletion/anonymization, verification, and lawful exceptions.
- [ ] [B] Retention and deletion define triggers, periods, reasons, backups, holds, execution evidence, and owner; sensitive and child data receive applicable heightened review.
- [ ] [B] Vendors and international transfers have purpose, access, suboperator, security, deletion/return, incident, jurisdiction, and applicable transfer-mechanism evidence.
- [ ] [B] A privacy impact/RIPD decision and required privacy/legal approval exist for high-risk or uncertain processing.
- [ ] [B] Personal-data incident handling records the knowledge time, risk/harm assessment, current notification rules and owners without placing personal data in Harness evidence.

## Product and UI

- [ ] [B] `docs/USER-MANUAL.md` matches the released version, features, navigation, workflows, permissions, feedback, recovery, accessibility, troubleshooting, and support behavior.
- [ ] [B] Critical journeys and the full interaction-state matrix are evidenced.
- [ ] [B] Narrow and wide responsive evidence and content stress were reviewed.
- [ ] [B] Automated accessibility plus keyboard, focus, semantics, reflow/zoom, error, and motion checks are recorded.
- [ ] [B] Visual baselines/diffs were reviewed by someone authorized to approve the change.

## Data, AI, operations, and cost

- [ ] [B] The Python API/React boundary, minimum extensible directories, import direction, thin entrypoints, and versioned API contract passed architecture validation.
- [ ] [B] `docs/TECHNICAL-DOCUMENTATION.md` covers current architecture, modules, API, data, auth, configuration, build/test, deployment/rollback, observability, recovery, operations, support, and residual risks.
- [ ] [B] Data contracts, validation, migration, replay/idempotency, retention, and recovery are covered where applicable.
- [ ] [B] AI output/tool policies, injection resistance, eval thresholds, memory, and fallback are covered where applicable.
- [ ] [B] Logs are redacted; SLIs/SLOs, alerts, escalation, runbook, and monitoring window are defined.
- [ ] [B] Variable-cost paths have quotas, worst-case exposure, alerts, degradation, and a kill switch.
- [ ] [R] Staged/canary/feature-flag rollout limits blast radius.

## Evidence index

```text
Release/artifact/digest:
SOURCE-OF-TRUTH version/reconciliation:
Architecture policy/check evidence:
Technical documentation review:
User manual review:
Target environment:
Approver and scope:
GateResult paths:
Validation commands and exit codes:
Security scanner evidence:
UI/accessibility/visual evidence:
Rollback/restore evidence:
Monitoring window and owner:
Not-applicable reasons:
Deferred items, owner, due point:
Residual risks:
```
