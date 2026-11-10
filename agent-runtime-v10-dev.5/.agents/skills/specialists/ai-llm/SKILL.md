---
name: ai-llm
description: "Explicit specialist review for changes where model, retrieval, prompt, tool, or memory behavior materially affects a system."
---

# AI and LLM gate

Return a `GateResult` conforming to `schemas/gate-result.schema.json`.

## Contract

Define:

- why AI is needed and the non-AI fallback or rejection case;
- model/provider capability profile, prompt version, and deprecation strategy;
- trusted instructions, untrusted content, retrieval sources, and context boundaries;
- input sensitivity, minimization, retention, tenant isolation, and memory lifecycle;
- structured output schema, parser/validator, confidence/abstention, and invalid-output behavior;
- tool allowlist, parameter validation, least privilege, step limits, approvals, and post-action verification;
- grounding/citation requirements and how unsupported claims fail safely;
- token, latency, request, retry, tool-step, context, and cost budgets;
- provider outage, rate-limit, timeout, refusal, and degraded-mode behavior.

Prompt injection cannot be guaranteed absent. Use layered isolation, least-privileged tools, validation, action-boundary approvals, provenance, monitoring, and explicit residual risk.

## Evaluation

Create representative normal, boundary, malformed, adversarial, multilingual, injection, privacy, tool-abuse, and fallback cases as applicable. Define measurable thresholds before implementation and record aggregate quality, safety, latency, token, and cost results. Use trace/workflow grading where available; do not test only the final prose.

Evidence may include redacted prompt templates, synthetic eval cases, aggregate results, schemas, and tool-policy pointers. Never store hidden reasoning, system secrets, raw customer conversations, or private prompt payloads.

Block implementation when unsafe output can trigger actions, schema/fallback behavior is undefined, or no meaningful eval threshold exists. Security owns independent risk acceptance; FinOps owns the final budget.
