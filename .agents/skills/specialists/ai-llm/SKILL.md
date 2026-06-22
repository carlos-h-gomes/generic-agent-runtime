---
name: ai-llm
description: "Design and review AI/LLM features for reliability, safety, cost control, privacy and evaluation. Use whenever a feature sends content to a model, uses model output in a system, uses tools/retrieval/RAG, stores prompts, handles user/customer context, does AI classification/extraction, or can be prompt-injected. Defines task fit, prompt/context boundaries, injection and tool-abuse defenses, output schema/validation, evaluation cases, cost controls and fallback behavior."
---

# AI and LLM Specialist

## Objective

Design and review AI/LLM features for reliability, safety, cost control, privacy and evaluation.

## When to use

- Prompting.
- Chatbots.
- RAG/vector search.
- Tool-using agents.
- Model outputs used by systems.
- User/customer context sent to a model.
- Embeddings.
- Prompt storage.
- AI-based classification/extraction.

## Process

1. Define the AI task and whether AI is actually needed.
2. Identify input data and sensitivity.
3. Define prompt/context boundaries.
4. Identify prompt-injection and tool-abuse risks.
5. Define output schema and validation.
6. Define fallback behavior.
7. Define evaluation cases.
8. Define cost controls.
9. Define logging without sensitive leakage.
10. Define human review needs when decisions affect users/customers.

## Deliverables

- AI task definition.
- Prompt/context strategy.
- Output validation strategy.
- Evaluation checklist.
- Risk and cost controls.

## Injection and output-handling defenses (2026 baseline)

Treat these as the default posture for any model that touches external or user content:

- Separate trusted instructions from untrusted data. System/developer intent must not be overridable by content arriving in user input, retrieved documents, files, tool results, or web pages. Frame external content as data to analyze, never as commands to follow.
- Treat all model output as untrusted before it acts on a system. Never `eval`/exec it, never pass it unchecked into shells, SQL, file paths, or downstream tool calls. Validate against a strict output schema first.
- Least-privilege tools: expose only the tools and scopes the task needs. Validate tool arguments and results.
- Human-in-the-loop on state-mutating or high-impact actions; prefer plan-then-confirm for those.
- Bound autonomy: cap loops/retries/steps, and provide a stop path, so a hijacked plan cannot run away (cascading failure).
- Guard durable memory: validate anything written to persistent context to prevent memory poisoning across runs.
- Minimize sensitive data sent to the model; scrub/mask PII and secrets from both prompts and logs.

For deeper coverage when the feature is a full agent (multiple tools, retrieval, memory, multi-agent), defer to `specialists/risk-security-compliance` and its OWASP ASI Top 10 mapping.

## Quality criteria

- Model output is not blindly trusted.
- Sensitive data is minimized.
- Prompt injection is considered.
- Cost is bounded.
- Evaluation cases exist.
- Fallback behavior exists.


## Written memory rule

For Level 2/3 work, record durable findings, assumptions, risks, and handoff notes in the active task file or the appropriate `docs/ai` file. Do not rely on mental notes.

## Checklist

- [ ] AI need justified.
- [ ] Data sensitivity reviewed.
- [ ] Prompt boundaries defined.
- [ ] Injection risks considered.
- [ ] Output schema/validation defined.
- [ ] Evaluation cases defined.
- [ ] Cost controls defined.
- [ ] Fallback defined.
- [ ] Human review considered.
