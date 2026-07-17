# Dated Standards Registry

Living references must be re-checked for each Harness release. A URL alone is not a frozen requirement.

| Domain | Reference | Version/date | Checked | Harness use |
|---|---|---|---|---|
| Agentic security | [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) | 2026 edition, published 2025-12 | 2026-07-15 | Canonical ASI01–ASI10 mapping for tool, retrieval, memory, and multi-agent threat reviews. |
| Web accessibility | [W3C Web Content Accessibility Guidelines](https://www.w3.org/TR/WCAG22/) | WCAG 2.2 | 2026-07-15 | Default AA target only when a web project has no stricter/different declared policy. |
| JSON Schema | [JSON Schema specification](https://json-schema.org/draft/2020-12/json-schema-core) | Draft 2020-12 | 2026-07-15 | Machine contracts in `schemas/`. |

OWASP 2026 canonical categories used by the security skill:

1. ASI01 Agent Goal Hijack
2. ASI02 Tool Misuse and Exploitation
3. ASI03 Identity and Privilege Abuse
4. ASI04 Agentic Supply Chain Vulnerabilities
5. ASI05 Unexpected Code Execution
6. ASI06 Memory and Context Poisoning
7. ASI07 Insecure Inter-Agent Communication
8. ASI08 Cascading Failures
9. ASI09 Human-Agent Trust Exploitation
10. ASI10 Rogue Agents

Check the authoritative page before relying on names in a later release. Standards identify review scope; they do not prove compliance or eliminate residual risk.
