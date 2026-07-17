# Model Baseline — 2026-07-15

Harness 4.1 is model-neutral. This file records the frontier-runtime context used for the release and must be re-checked later.

## GPT-5.6 Sol Ultra interpretation

OpenAI announced GPT-5.6 on 2026-07-09. `gpt-5.6-sol` is the Sol model ID; `gpt-5.6` is an alias. “Ultra” is a high-capability execution setting combining maximum reasoning and proactive multi-agent work, not another model slug. Supported product surfaces may use four agents by default, while the Responses Multi-agent beta recommends three concurrent subagents as a starting point.

Harness therefore keeps a portable default of one root agent, depth 1, and no more than three concurrent workers unless a runtime-specific evaluation supports another limit. Provider availability, betas, prices, and agent counts never expand authorization.

## Prompt and orchestration implications

- State outcome, context, constraints, evidence, and success criteria once; avoid duplicated procedural prompting.
- Delegate independent bounded work, especially read-heavy exploration/review. Do not parallelize ordered chains or contended shared state.
- Use programmatic tool orchestration for predictable filtering, joins, sorting, deduplication, aggregation, and validation; keep semantic judgment, citations, approvals, and writes as direct actions.
- Evaluate whole workflows and traces, not only final prose. Track quality, evidence completeness, latency, tokens, cost, side effects, and approval behavior.
- Keep stable prompt prefixes before variable context when a provider's prompt caching applies.

## Official sources checked 2026-07-15

- [GPT-5.6 launch](https://openai.com/index/gpt-5-6/)
- [Latest-model guidance](https://developers.openai.com/api/docs/guides/latest-model)
- [GPT-5.6 Sol reference](https://developers.openai.com/api/docs/models/gpt-5.6-sol)
- [Responses Multi-agent](https://developers.openai.com/api/docs/guides/responses-multi-agent)
- [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Codex AGENTS.md discovery and limits](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Programmatic Tool Calling](https://developers.openai.com/api/docs/guides/tools-programmatic-tool-calling)
- [Agent workflow evaluation](https://developers.openai.com/api/docs/guides/agent-evals)

These are living documents. Revalidate claims and dates during the next Harness release.
