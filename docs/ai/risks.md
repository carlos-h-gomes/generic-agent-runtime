# Project Risks

Status: uninitialized. Keep material durable risks and their owners current.

| ID | Domain | Risk | Severity | Trigger | Mitigation/guardrail | Residual risk / owner |
|---|---|---|---:|---|---|---|
| V8-ARCH-01 | architecture | An open profile could accept a semantically poor boundary or miss a monolithic composition root. | high | New or changed application architecture. | Machine checks for declared roots, dependency direction, and behavior-bearing entrypoints; require human architecture gate evidence. | Heuristics cannot prove design quality / architecture reviewer. |
| V8-REUSE-01 | quality/cost | The agent may duplicate compatible behavior or over-engineer a small change. | medium | Material implementation without a current reuse decision. | Inventory and classify existing assets before creation; require evidence for replacement and new responsibilities. | Compatibility still needs human judgment / implementer. |
| V8-CHOICE-01 | product | Recommendations could be mistaken for a mandatory language, framework, or tool. | medium | A greenfield material choice is absent. | State tradeoffs, keep options open, and wait for the user's recorded choice before generation. | User may choose an unsupported technology / task owner. |
| V8-MODEL-01 | AI/security | Sol or Daybreak Blue may be unavailable, stale, or treated as expanded authority. | high | Optional model profile requested or selected. | Verify access and official capability evidence; preserve all target, tool, data, and production approvals; use a documented fallback. | Behavioral host evaluation remains required / AI gate owner. |

Domains may include security, privacy/compliance, data, AI, cost, operations, UX, architecture, and coordination. Link sensitive evidence; never paste secrets, customer data, full logs, or private prompts.
