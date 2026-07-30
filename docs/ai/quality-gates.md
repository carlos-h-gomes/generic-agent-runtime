# Quality Gate Contract

Version: 1.1. Machine shape: `schemas/gate-result.schema.json`.

| Gate ID | Unique responsibility |
|---|---|
| `ux_product` | User outcome, information hierarchy, design system, full state matrix, responsive behavior, accessibility, and reviewed visual evidence. |
| `architecture_uml` | Boundaries, responsibilities, contracts, failure isolation, and trade-offs. |
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
