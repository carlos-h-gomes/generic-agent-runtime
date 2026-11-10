# Threat Model

Status: uninitialized. Required for a production web or agentic release.

Use `docs/harness/PRODUCT-SECURITY-PRIVACY.md` as the baseline. Record assets, actors, identities, entrypoints, trust/data boundaries, personal-data flows, third parties, threats, misuse and abuse cases, controls, evidence, owner, and residual risk.

Cover authentication and recovery; server-side resource, tenant, role, and function authorization; sessions, CSRF, CORS and browser headers; input/output, injection, SSRF, upload, parser, template and command boundaries; secrets and dependency/tool supply chain; API inventory, webhooks, replay and idempotency; request, response, pagination, batch, concurrency, rate, volume and cost limits; sensitive business-flow automation; logging and privacy; execution and egress; monitoring, containment, rebuild and recovery.

For personal data, record purpose, legal-basis input, minimization, controller/operator roles, recipients and jurisdictions, retention/deletion, data-subject rights, sensitive or child data, international transfers, incident obligations, and the RIPD/privacy-review decision. For tool-using agents also map the current OWASP Agentic Top 10. Use synthetic evidence and current authoritative sources. Unknown or unavailable coverage is incomplete, not passed.
