# Dated Standards Registry

Living references must be rechecked for every Harness release. Policy floors are recorded in `security-policy.json` and expire.

## Mandatory hybrid engineering standard

Application generation uses an isolated Python HTTP API backend and React frontend. The repository must preserve the minimum topology and dependency rules in `docs/ai/conventions.md` and the machine contract in `docs/ai/architecture-policy.json`. Entry files are composition roots, never feature containers. Additional directories are permitted when their responsibility and dependency direction are documented.

The API boundary must define ownership, versioning, authentication, authorization, input/output schemas, stable errors, pagination where applicable, timeout/cancellation behavior, CORS policy, rate/volume limits, observability, and compatibility. OpenAPI is the default machine contract. The frontend never gains authority merely because it hides a control or validates an input.

`SOURCE-OF-TRUTH.md` is the root index of verified project facts and authoritative pointers. Tasks, decisions, schemas, code, tests, technical documentation, and the user manual retain their specialized authority. Official releases require current technical and user documentation.

| Domain | Reference | Version/date | Checked | Harness use |
|---|---|---:|---:|---|
| Application security | [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) | 5.0.0 | 2026-07-30 | Verification-control vocabulary and security test planning. |
| Agentic security | [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) | 2026 | 2026-07-30 | Tool, identity, supply-chain, execution, memory, communication, cascading-failure, trust, and rogue-agent threats. |
| Secure development | [NIST SSDF](https://csrc.nist.gov/pubs/sp/800/218/final) | SP 800-218 v1.1 | 2026-07-30 | Secure preparation, protection, production, and response practices. |
| Secure by design | [CISA Secure by Design](https://www.cisa.gov/securebydesign) | Living guidance | 2026-07-30 | Safe defaults, ownership, transparency, and reduction of systemic classes of defect. |
| Web framework | [Next.js support policy](https://nextjs.org/support-policy) and [July 2026 security release](https://nextjs.org/blog/july-2026-security-release) | 16.2.11 active LTS; 15.5.21 maintenance LTS | 2026-07-30 | Dated supported-major and minimum-patch gate. |
| Runtime | [Node.js releases](https://nodejs.org/en/about/previous-releases) | LTS majors 24 and 22 | 2026-07-30 | Deployment pin gate. |
| Python runtime | [CPython supported versions](https://devguide.python.org/versions/) | 3.14 and 3.13 bugfix lines | 2026-08-03 | Default backend runtime lines; production pins require the latest supported patch. |
| React | [React versions](https://react.dev/versions) and [versioning policy](https://react.dev/community/versioning-policy) | Latest stable 19.2 line | 2026-08-03 | Default frontend library; prerelease channels are blocked unless explicitly approved and pinned. |
| Frontend build | [Vite releases](https://vite.dev/releases) | 8.1 current; 8.0/7.3 important fixes; 6.4 security-only | 2026-08-03 | Default TypeScript/React build tool; use a supported stable line and compatible LTS Node pin. |
| Accessibility | [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) | 2.2 | 2026-07-30 | Default AA target for applicable web UI. |
| Supply chain | [SLSA specification](https://slsa.dev/spec/v1.2/) | 1.2 | 2026-07-30 | Provenance shape and explicit authenticity boundary. |
| SBOM | [CycloneDX](https://cyclonedx.org/specification/overview/) | 1.7 | 2026-07-30 | Release component inventory. |
| Contracts | [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/json-schema-core) | 2020-12 | 2026-07-30 | Machine-readable contracts. |

References scope review; they do not prove compliance. Recheck before relying on these versions after the policy expiry date.
