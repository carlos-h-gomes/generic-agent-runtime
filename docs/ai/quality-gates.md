# Quality Gate Contract

Version: 1.0. Machine shape: `schemas/gate-result.schema.json`.

## Ownership and phases

| Gate ID | Unique owner | Usual phase |
|---|---|---|
| `ux_product` | User outcome, interaction, states, accessibility | design |
| `architecture_uml` | Boundaries, responsibilities, contracts, trade-offs | design |
| `data_integration` | Schema/flow semantics, reliability, replay/migration | design |
| `ai_llm` | Model/context/output/tool contract and AI evals | design |
| `security_compliance` | Independent security/privacy/compliance risk | design or implementation review |
| `finops` | Quantified cost, caps, alerts, degradation | design or pre-release |
| `code_quality_testing` | Diff quality, tests, corrective loop | implementation review |
| `observability_release` | Operations, rollout, rollback, incident readiness | pre-release |

The task contract declares applicable gates. Specialists return separate GateResult files so independent read-heavy reviews can run in parallel. The root/integrator maintains the compact gate index and verifies results.

## Result derivation

- `not_applicable`: the trigger is absent and a concrete reason is recorded.
- `blocked`: a required check failed or is unverified at its due phase, an open blocking finding exists, or required input/approval/evidence is missing.
- `passed_with_conditions`: no blocker remains; each non-blocking condition has an owner and due point.
- `passed`: all applicable required checks have evidence and no unresolved condition remains.

Severity describes impact, not workflow status:

- `critical`: catastrophic/irreversible; blocking by default.
- `high`: material security, customer, financial, privacy, integrity, or availability impact; blocking by default.
- `medium`: meaningful bounded impact; may pass with an owner and deadline.
- `low`: localized impact; normally non-blocking.
- `info`: observation without current material risk.

An agent cannot accept critical/high risk. `risk_accepted` requires an authorized human reference and cannot override the constitution or platform controls. Release cannot downgrade another gate's blocker.

## Evidence safety

GateResult stores pointers and bounded redacted summaries, not payloads. Never persist secrets, credentials, cookies, raw customer/production records, full logs, real webhook payloads, private model prompts/conversations, hidden reasoning, unredacted screenshots, or exploit detail beyond safe reproduction.

Controlled full artifacts may be referenced with access-controlled path, retention, hash, exit code, and a short actionable excerpt. Synthetic or sanitized fixtures are the default.

## Reflection loop

Two total validation attempts include the first run:

```text
implementation -> attempt 1 -> correction -> attempt 2 -> correction -> attempt 3
```

Stop earlier on repeated failure without new evidence, required protected action, or scope expansion. After the limit, use `paused_for_review` and report changed files, commands, exit codes, bounded failure evidence, residual risk, and review focus. A skipped or unavailable check is `not_verified`, never a pass.
