# Quality Gate Contract

Version: 1.1. Machine shape: `schemas/gate-result.schema.json`.

| Gate ID | Unique responsibility |
|---|---|
| `ux_product` | User outcome, information hierarchy, design system, full state matrix, responsive behavior, accessibility, and reviewed visual evidence. |
| `architecture_uml` | Python API/React boundaries, minimum extensible topology, dependency direction, thin entrypoints, contracts, failure isolation, and trade-offs. |
| `data_integration` | Data semantics, trust boundaries, validation, replay, migration, and recovery. |
| `ai_llm` | Model/context/output/tool contracts, evaluations, budgets, and agentic threats. |
| `security_compliance` | Threat model, authentication/authorization, secret handling, dependency/SAST evidence, adversarial scope, privacy, and residual risk. |
| `finops` | Quantified exposure, quotas, alerts, degradation, and kill switch. |
| `code_quality_testing` | Diff quality, deterministic tests, regression coverage, and bounded corrective loop. |
| `observability_release` | Artifact identity, rollout, rollback, containment, monitoring, and incident readiness. |

`blocked` means a required check failed, is unavailable, has no evidence, or has an open critical/high finding. `passed_with_conditions` requires a named owner and due point for every non-blocking condition. `passed` requires current evidence. `not_applicable` requires a concrete absent trigger.

Skipped and unavailable checks are incomplete, never passed. An agent cannot accept critical/high risk. Human acceptance cannot override the constitution or external authorization.

Gate results contain bounded, redacted summaries and evidence pointers—not credentials, raw customer data, private prompts, full response bodies, or exploit payloads.

For material UI, `ux_product` requires an approved `docs/ai/ui-review.json`. For internet-facing web work, `security_compliance` requires an in-date policy, a threat model, incident response, supported pinned runtime/framework versions, and applicable scanner evidence.

Validation uses at most two corrective retries after the initial attempt. Repeated failure without new evidence pauses the task for review.

For application work, `architecture_uml` cannot pass without a valid `docs/ai/architecture-policy.json`, the required minimum directories, compliant dependency direction, a versioned API boundary, and evidence that entrypoints are composition-only. Additional directories are allowed when responsibility and permitted dependencies are recorded.

For official project releases, `observability_release` cannot pass while `SOURCE-OF-TRUTH.md`, `docs/TECHNICAL-DOCUMENTATION.md`, or `docs/USER-MANUAL.md` is uninitialized, stale, version-mismatched, placeholder-filled, or missing required coverage. Every active task must classify documentation impact; `none` is valid only with a concrete no-impact reason.
