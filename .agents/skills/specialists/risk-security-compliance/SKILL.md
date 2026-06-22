---
name: risk-security-compliance
description: "Review security, privacy, compliance and abuse risk, including agentic-AI risks from the OWASP Top 10 for Agentic Applications (2026). Use whenever there is auth/authz, public endpoints/webhooks, external/untrusted input, file uploads, secrets/credentials, customer or personal data, third-party transfer, production impact, tool-using agents, or LLMs handling user/customer context. Produces specific risks, severities, required mitigations, approval requirements and residual risk."
---

# Risk, Security and Compliance Specialist

## Objective

Review security, privacy, compliance and abuse risks without splitting related concerns across too many agents.

## When to use

- Auth/authz.
- Public endpoints/webhooks.
- External input.
- File upload.
- Secrets or credentials.
- Customer or personal data.
- Logs containing identifiers.
- Third-party integrations.
- Production changes.
- LLMs handling user/customer context.
- Automated actions triggers (Scraping, external API calls).
- High-resource consumption endpoints (Rate limiting targets).

## Process

1. Identify assets and trust boundaries.
2. Identify data categories and sensitivity.
3. Validate auth/authz expectations.
4. Check input validation, output sanitization, and strict protection against SSRF and Prompt Injection.
5. Check secrets handling.
6. Check logs for sensitive data exposure.
7. Check third-party transfers.
8. Check retention/minimization.
9. Identify abuse cases (e.g., Rate Limiting exhaustion, DoS, logic flaws).
10. Define required mitigations.

## Agentic AI risk model (OWASP Top 10 for Agentic Applications, 2026)

When the change involves an autonomous agent, tool use, retrieval, memory, or multi-agent coordination, evaluate against the ASI Top 10. These risks are additive to the classic web/LLM risks above, not a replacement.

| ID | Risk | What to check | Baseline mitigation |
|---|---|---|---|
| ASI01 | Agent goal/instruction hijack | Can untrusted input (user text, RAG doc, file, web page, email) change the agent's task? | Treat all external content as untrusted data, never as instructions. Keep the original mandate bound to each step. Validate/segment untrusted input before it reaches the planner. |
| ASI02 | Tool misuse / insecure tool execution | Are tools over-scoped? Can a tool be invoked with attacker-controlled args? | Least-privilege tools. Allow-list arguments. Validate tool inputs/outputs. |
| ASI03 | Identity & privilege abuse | Does the agent run with broad/admin credentials? | Scoped, per-task identities. JIT/ephemeral tokens scoped to the exact resource+action. No standing admin scopes. |
| ASI04 | Supply chain | Are models, packages, MCP servers, or skills from untrusted sources? | Pin dependencies (ideally by hash). Run SCA. Vet third-party MCP servers/skills before enabling. |
| ASI05 | Unexpected code execution | Can the agent generate and run code that exfiltrates data or opens a shell? | Sandbox/isolate all code execution. No network/secret access by default. Treat generated code as hostile. |
| ASI06 | Memory poisoning | Can persisted memory/context be poisoned to influence later runs? | Validate what is written to durable memory. Separate trusted project memory from untrusted captured content. |
| ASI07 | Insecure inter-agent / handoff comms | Are messages between agents/tools authenticated and bounded? | Authenticate handoffs. Validate payloads. Do not trust another agent's undocumented output. |
| ASI08 | Cascading failures | Can one bad step trigger runaway multi-step actions? | Circuit breakers, attempt/loop caps, kill-switch for autonomous loops. |
| ASI09 | Human-agent trust exploitation | Could output manipulate a human into unsafe approval? | Human-in-the-loop on state-mutating/high-impact actions. Show what will execute before it runs. |
| ASI10 | Rogue/uncontrolled agent | Is there a way to detect and stop a misbehaving agent? | Monitoring, audit log of actions, and an enforced stop/kill path. |

Shadow-mode rule: for new autonomous or high-impact agent behavior, prefer a phase where the agent plans actions but cannot execute state-mutating ones without human review, until trust is established.

## Deliverables

- Risk summary.
- Agentic risk findings mapped to ASI IDs when an agent/tool/retrieval is involved.
- Required mitigations.
- Approval requirements.
- Residual risks.

## Quality criteria

- Specific risks, not generic warnings.
- Clear severity.
- Practical mitigations.
- No hidden privacy assumptions.

## Written memory rule

For Level 2/3 work, record durable findings, assumptions, risks, and handoff notes in the active task file or the appropriate `docs/ai` file. Do not rely on mental notes.

## Checklist

- [ ] Trust boundaries mapped.
- [ ] Data sensitivity identified.
- [ ] Auth/authz checked.
- [ ] Inputs validated.
- [ ] Secrets protected.
- [ ] Logs safe.
- [ ] Retention considered.
- [ ] Third-party transfer considered.
- [ ] Human approval identified if needed.
- [ ] SSRF mitigated on external data fetching.
- [ ] LLM inputs sanitized (Prompt Injection prevented).
- [ ] Rate limits applied to public or heavy endpoints.
- [ ] IDOR/BOLA tested on resource access (Does User A own this ID?).
- [ ] Dependency/supply-chain scan considered (SCA / pinned versions) when dependencies change.
- [ ] For agent/tool/RAG features: ASI Top 10 reviewed; external content treated as untrusted; tools least-privilege; code execution sandboxed; human-in-the-loop on state-mutating actions; loop/attempt caps and a stop path exist.