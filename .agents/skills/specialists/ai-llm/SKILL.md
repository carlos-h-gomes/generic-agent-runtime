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
