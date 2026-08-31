# Dated Standards Registry

Living references must be rechecked for every Harness release. Policy floors are recorded in `security-policy.json` and expire.

## Open architecture engineering standard

Application generation follows the user's recorded language, framework, tool, and topology choices. If a material greenfield choice is missing, present relevant options with concise reasons and wait for the user to choose; do not silently default to the bundled template. Brownfield work preserves the evidence-backed stack unless a separate migration is authorized. The repository must record roots, modules, responsibilities, dependency direction, composition roots, contracts, tests, and extension rules in `docs/ai/architecture-policy.json`. Entry files are composition roots, never feature containers.

The API boundary must define ownership, versioning, authentication, authorization, input/output schemas, stable errors, pagination where applicable, timeout/cancellation behavior, CORS policy, rate/volume limits, observability, and compatibility. OpenAPI is the default machine contract. The frontend never gains authority merely because it hides a control or validates an input.

`SOURCE-OF-TRUTH.md` is the root index of verified project facts and authoritative pointers. Tasks, decisions, schemas, code, tests, technical documentation, and the user manual retain their specialized authority. Official releases require current technical and user documentation.

Harness adoption follows `docs/harness/HARNESS-ADOPTION-POLICY.md`; installing governance never implies application bootstrap or migration. Material integrations and automations follow `docs/harness/SOLUTION-DECISION-POLICY.md` and the open solution contract. Tool-specific policies, including the retained n8n compatibility profile, apply only after that tool is selected. Recheck capabilities, supported versions, security guidance, retention, and pricing before downstream reliance.

| Domain | Reference | Version/date | Checked | Harness use |
|---|---|---:|---:|---|
| Application security | [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) | 5.0.0 | 2026-07-30 | Verification-control vocabulary and security test planning. |
| API security and abuse | [OWASP API Security Top 10](https://owasp.org/API-Security/) | 2023 | 2026-08-31 | Object/function authorization, authentication, resource consumption, sensitive business flows, SSRF, inventory, configuration, and unsafe upstream APIs. |
| Agentic security | [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) | 2026 | 2026-07-30 | Tool, identity, supply-chain, execution, memory, communication, cascading-failure, trust, and rogue-agent threats. |
| Secure development | [NIST SSDF](https://csrc.nist.gov/pubs/sp/800/218/final) | SP 800-218 v1.1 | 2026-07-30 | Secure preparation, protection, production, and response practices. |
| Secure by design | [CISA Secure by Design](https://www.cisa.gov/securebydesign) | Living guidance | 2026-07-30 | Safe defaults, ownership, transparency, and reduction of systemic classes of defect. |
| Web framework | [Next.js support policy](https://nextjs.org/support-policy) and [August 2026 security release](https://nextjs.org/blog/august-2026-security-release) | 16.3.3 active LTS; 15.5.24 maintenance LTS | 2026-08-28 | Dated supported-major and minimum-patch gate. |
| Runtime | [Node.js releases](https://nodejs.org/en/about/previous-releases) | LTS majors 24 and 22 | 2026-07-30 | Deployment pin gate. |
| Python runtime | [CPython supported versions](https://devguide.python.org/versions/) | 3.14 and 3.13 bugfix lines | 2026-08-03 | Optional Python profile; production pins require the latest supported patch. |
| React | [React versions](https://react.dev/versions) and [versioning policy](https://react.dev/community/versioning-policy) | Latest stable 19.2 line | 2026-08-03 | Optional React profile; prerelease channels are blocked unless explicitly approved and pinned. |
| Frontend build | [Vite releases](https://vite.dev/releases) | 8.2 current; 8.1/8.0/7.3 important fixes; 6.4 security-only | 2026-08-28 | Optional TypeScript/React build profile; use a supported stable line and compatible LTS Node pin when selected. |
| Accessibility | [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) | 2.2 | 2026-07-30 | Default AA target for applicable web UI. |
| Supply chain | [SLSA specification](https://slsa.dev/spec/v1.2/) | 1.2 | 2026-07-30 | Provenance shape and explicit authenticity boundary. |
| SBOM | [CycloneDX](https://cyclonedx.org/specification/overview/) | 1.7 | 2026-07-30 | Release component inventory. |
| Contracts | [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/json-schema-core) | 2020-12 | 2026-07-30 | Machine-readable contracts. |
| Brazilian data protection | [LGPD, Law 13.709/2018](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm) and [ANPD guidance](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/documentos-tecnicos-orientativos) | Current consolidated law and guidance | 2026-08-31 | Purpose, legal basis, necessity, rights, governance, security, prevention, accountability, and privacy by design. |
| Personal-data incidents | [ANPD Resolution CD/ANPD 15/2024](https://www.gov.br/anpd/pt-br/acesso-a-informacao/institucional/atos-normativos/regulamentacoes_anpd/documentos/rcis___anonimizado_final_ocultado_2_parte3.pdf) | 15/2024 | 2026-08-31 | Relevant-risk assessment, controller notification duties, three-business-day rules, required content, and incident records. |
| International data transfer | [ANPD Resolution CD/ANPD 19/2024](https://www.gov.br/anpd/pt-br/acesso-a-informacao/institucional/atos-normativos/regulamentacoes_anpd/resolucao-cd-anpd-no-19-de-23-de-agosto-de-2024) | 19/2024, including later official corrections | 2026-08-31 | Transfer mapping, safeguards, transparency, accountability, clauses, and current adequacy mechanisms. |
| Workflow automation | [n8n source control and environments](https://docs.n8n.io/source-control-environments/create-environments/) and [security audit](https://docs.n8n.io/hosting/securing/security-audit/) | Living guidance | 2026-08-04 | Optional n8n profile: environment promotion, protected production, risky-node, webhook, credential, and instance controls. |

References scope review; they do not prove compliance. Recheck before relying on these versions after the policy expiry date.
