# Research candidates and attribution

Research snapshot last refreshed 2026-10-10; reconfirm upstream releases, licenses, vulnerabilities, and provenance before selecting any component. No code or binary from these projects is bundled by GAR 10. Project licenses below describe reviewed research candidates, not permission to redistribute arbitrary subdirectories or releases. Exact component artifacts remain unqualified.

| Project / upstream | License scope reviewed | Intended option / condition |
|---|---|---|
| [Playwright, Microsoft and contributors](https://github.com/microsoft/playwright) | Apache-2.0 | Browser journey/visual reports; do not enable experimental page-defined agent tools automatically |
| [axe-core, Deque and contributors](https://github.com/dequelabs/axe-core) | MPL-2.0 | Accessibility report; preserve notices and applicable source obligations on modification; keyboard/manual review still required |
| [OSV-Scanner, Google and contributors](https://github.com/google/osv-scanner) | Apache-2.0 | Dependency reports; scoped advisory egress or reviewed offline database; no automatic fix execution |
| [Gitleaks contributors](https://github.com/gitleaks/gitleaks) | MIT | Redacted secret finding reports; scan scope and successful command exit need separate proof |
| [Agent Skills specification contributors](https://github.com/agentskills/agentskills) | Code Apache-2.0; documentation CC-BY-4.0 | Progressive skill-loading reference; individual installed skills require separate review |

Maintainer register at `docs/ai/tasks/2026-10-10-gar-vibecoder-evolution-repositories.md` covers the broader candidate set. No inferred trust from stars, organization name or an empty advisory page. Do not bulk-install hook bundles. Review licenses of each skill; source-available document skills are not automatically open source.

Trivy is deferred after its upstream documented 2026 supply-chain incident; no claim that an unreviewed current artifact is safe. New engines (Deep Agents) and policy engines (OPA) remain architectural options, not mandatory runtime dependencies. Promptfoo evaluation can involve provider/network cost and requires explicit approved scope.

The risk-review reference is [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/). GAR's review covers goal manipulation, tool misuse, privilege, supply chain, execution, context, inter-agent communication, cascading failures, human trust and rogue-agent behavior. This mapping does not establish conformance or complete protection.
