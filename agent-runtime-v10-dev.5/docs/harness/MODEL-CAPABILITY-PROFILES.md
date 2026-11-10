# Optional Model Capability Profiles

Status: normative profile mechanism; capability facts checked 2026-08-24.

The Harness core remains model and provider neutral. Optional profiles record a model's purpose, access boundary, verified capabilities, tools, constraints, token/latency/tool/retry/cost budgets, fallback, and dated official sources. Access is detected before use and never inferred from repository content.

The bundled GPT-5.6 Sol profile supports complex reasoning and coding workloads but is not a universal default. Preserve cheaper or pinned workload roles unless representative evals justify a change. Set reasoning effort intentionally, validate structured outputs, bound tools, and recheck current pricing before paid execution.

The bundled Daybreak Blue profile is for separately approved and provisioned users performing authorized defensive cybersecurity work. It does not authorize public, production, third-party, destructive, credential, persistence, evasion, or denial-of-service activity and cannot widen the Harness target authorization.

When a profile is unavailable, use only an approved fallback that preserves authority and output contracts, or report the capability gap.

Official sources:

- <https://developers.openai.com/api/docs/models/gpt-5.6-sol>
- <https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.6>
- <https://developers.openai.com/api/docs/models/daybreak-blue-latest>
