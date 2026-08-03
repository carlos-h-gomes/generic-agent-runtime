# Profile-Driven Release Checklist

`[B]` blocks an applicable release. `[R]` may be deferred only with reason, owner, and due point. Every `not applicable` entry needs a project-specific reason.

## Identity and recovery

- [ ] [B] `SOURCE-OF-TRUTH.md` identifies the current product version, architecture profile, authoritative sources, active work, material risks, and last qualified evidence.
- [ ] [B] Revision, artifact digest, SBOM, provenance, environment, and owner are identified.
- [ ] [B] Reproducible build/install mode and lockfile are evidenced.
- [ ] [B] Rollback or restore was exercised against declared objectives.
- [ ] [B] Configuration and migration compatibility order is documented.

## Security and containment

- [ ] [B] Security policy is current; runtime/framework pins satisfy it.
- [ ] [B] Fresh dependency, secret, and SAST results have no unresolved high/critical finding.
- [ ] [B] Threat model covers public entrypoints, trust boundaries, authorization, upload/render paths, SSRF/RCE, dependency scripts, and agent tools where applicable.
- [ ] [B] Secrets are absent from source/build/logs and have scoped rotation/revocation procedures.
- [ ] [B] Production runs as non-root with minimum filesystem/process/network authority and resource quotas.
- [ ] [B] Incident response names containment, credential rotation, rebuild, evidence, communication, and owner.
- [ ] [B] Adversarial traffic, if any, used an exact, bounded, unexpired authorized target contract.

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
