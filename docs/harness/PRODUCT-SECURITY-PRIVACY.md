# Product Security and Privacy Baseline

Use this baseline for every internet-facing product, API, automation, or agentic system. It turns broad security and privacy goals into review questions. It is not legal advice, a penetration test, or proof of compliance. A missing answer or unavailable check is incomplete evidence, not a pass.

## Start with the product, data, and abuse model

Before implementation, record the users, administrators, service identities, public and internal entrypoints, protected assets, personal-data categories, trust boundaries, third parties, and the worst credible misuse of each important business flow. Include mistakes by legitimate users, abusive automation, compromised accounts, malicious inputs, dependency compromise, insider access, and operational failure.

The threat model must name the owner and evidence for every applicable control below. High or critical findings block release. The Harness governs decisions and evidence; enforcement belongs in the application, identity provider, database, runtime, network, cloud account, and operational process.

## Identity, session, and authorization

- Use a maintained identity implementation or provider. Do not invent password storage, token formats, OAuth/OIDC flows, or account recovery.
- Protect privileged and high-impact accounts with phishing-resistant MFA where practical. Bound enrollment, recovery, factor replacement, and support overrides.
- Use secure session identifiers; rotate them after authentication and privilege changes; define idle and absolute expiry, logout invalidation, revocation, device/session visibility, and safe recovery.
- Configure browser cookies deliberately: `Secure`, `HttpOnly`, and the narrowest applicable `SameSite`, domain, path, and lifetime. Protect state-changing browser requests against CSRF.
- Prevent account and credential enumeration through responses, timing, logs, and recovery flows. Rate-limit login, recovery, verification, invitation, and factor challenges without creating an easy account-lockout denial of service.
- Enforce authorization on the server at the owned resource and action boundary. Test other users, tenants, roles, identifiers, batch endpoints, exports, background jobs, webhooks, alternate protocols, and administrative paths. A hidden button or middleware-only check is not authorization.
- Default deny. Separate customer, support, operator, automation, and deployment identities; grant minimum scope and record privileged actions in tamper-resistant audit evidence.

## Requests, APIs, and abuse resistance

- Validate type, shape, range, size, encoding, and semantic invariants at every trust boundary. Parameterize database access and apply context-correct output encoding.
- Define maximum body, file, field, collection, query, pagination, batch, response, processing-time, concurrency, retry, and queue limits. Reject or degrade safely before expensive work.
- Apply rate and volume controls by the dimensions that matter: source, account, tenant, credential, operation, destination, and cost. Document burst, sustained, daily, and exceptional limits; monitor both allowed and denied traffic.
- Identify sensitive business flows such as signup, trial creation, search/scraping, reservations, purchases, coupons, invitations, messaging, password reset, exports, AI generation, and paid third-party calls. Add business-level quotas, anti-automation signals, idempotency, replay protection, reconciliation, fraud review, and a kill switch where applicable.
- Treat caller-supplied URLs and callbacks as SSRF boundaries. Allowlist destinations or resolve and recheck scheme, host, address, redirects, DNS changes, credentials, ports, and response budgets; restrict egress from the runtime.
- Treat uploads and parsers as hostile. Bound size and expansion, verify actual type, randomize storage names, keep files outside executable/public paths, scan or transform when appropriate, and isolate complex media, document, archive, and template processing.
- Inventory every API version, route, webhook, job, and integration. Authenticate webhooks, verify signatures over raw bounded bodies, enforce freshness and replay protection, rotate secrets, and make side effects idempotent.
- Use stable, non-sensitive errors. Do not expose stack traces, SQL, filesystem paths, secrets, internal topology, or authorization distinctions that help enumeration.

## Browser, transport, and configuration

- Require HTTPS and safe transport settings in every non-local environment. Terminate and redirect deliberately; protect service-to-service traffic according to its trust boundary.
- Set an explicit CORS policy. Never combine credentialed requests with a reflected or unrestricted origin.
- Define security headers appropriate to the product, including a restrictive Content Security Policy, framing policy, content-type protection, referrer policy, and HSTS after deployment readiness is verified.
- Keep secrets outside source, images, client bundles, prompts, logs, screenshots, test fixtures, and archives. Use scoped, short-lived, rotatable values; document revocation order and eliminate inherited secrets from untrusted builds.
- Separate development, test, staging, and production identities, data, networks, and control planes. Production runs with least privilege, non-root identity, constrained filesystem/process/network access, quotas, and no interactive debug mode.

## Dependencies, build, and release

- Use supported pinned runtimes and frameworks, a lockfile, reproducible installation, reviewed package scripts, and an owner for patching.
- Run applicable secret, dependency, SAST, infrastructure/container, and artifact-integrity checks. Produce an SBOM and provenance evidence. An absent scanner is `not_verified`.
- Test negative authorization, injection, SSRF, upload/parser, secret exposure, resource exhaustion, replay, rate-limit, recovery, and rollback cases in synthetic or explicitly authorized environments.
- Monitor authentication anomalies, authorization denials, rate-limit pressure, cost/resource growth, queue saturation, dependency changes, unknown processes, egress, and destructive/privileged actions. Redact personal and secret data and bound retention and cardinality.
- Provide containment, credential revocation, immutable rebuild, validated restore, rollback, communication, escalation, and post-incident ownership. Prevention without recovery evidence is incomplete.

## LGPD and privacy by design

For processing subject to Brazilian law, involve the privacy/legal owner when scope or interpretation is uncertain. The project record must cover:

- the controller, operator, suboperators, data owner, security owner, privacy contact or encarregado where applicable, and contractual instructions;
- each processing purpose, data category, source, recipient, system of record, jurisdiction, and applicable legal-basis input; do not use consent as a universal default;
- purpose compatibility, necessity and data minimization before collection, including telemetry, logs, prompts, model context, analytics, backups, and test data;
- a documented legitimate-interest balancing test when that hypothesis is considered; sensitive data uses the specific legal hypotheses and children or adolescents require priority treatment of their best interests;
- a clear privacy notice and a usable process for access, confirmation, correction, portability where regulated, information about sharing, consent withdrawal, opposition, review of relevant automated decisions, anonymization/blocking, and deletion subject to lawful retention exceptions;
- a retention schedule with trigger, duration, legal or operational reason, backup behavior, deletion/anonymization method, verification, holds, and owner. “Keep forever” and “delete on request” are not complete policies;
- vendor and international-transfer review covering necessity, access, suboperators, security, deletion/return, incident duties, audit evidence, jurisdiction, and a valid LGPD transfer mechanism;
- a proportional privacy impact assessment or RIPD decision for high-risk, large-scale, sensitive, child, surveillance, profiling, novel, or materially automated processing;
- security measures from product conception through operation, records that demonstrate the measures work, and a data-subject and regulator communication path.

Under ANPD Resolution CD/ANPD 15/2024, the controller must assess personal-data incidents for relevant risk or harm and, when communication is required, observe the applicable three-business-day notification rules counted from knowledge that personal data was affected, subject to specific-law and small-agent provisions. Keep the incident decision and required records without placing personal data or unrestricted forensic material in Harness artifacts. Recheck the current regulation and obtain qualified legal/privacy review for the actual incident.

International transfers must be mapped and supported by an applicable LGPD mechanism and the current ANPD rules. Cloud hosting, analytics, support access, model providers, CDNs, backups, and subprocessors can create a transfer even when the application team did not design one explicitly.

## Evidence expected before release

At minimum, link the completed threat model, data/processing inventory, privacy and retention decisions, authorization matrix and negative tests, abuse/resource budgets, scanner summaries, runtime and dependency versions, incident and rollback exercises, monitoring owners, residual risks, and required human approvals. Never store credentials, raw customer records, unrestricted logs, exploit payloads, or unnecessary personal data as evidence.

Current reference dates belong in `docs/ai/standards.md` and `security-policy.json`. Use OWASP ASVS for verification requirements, the OWASP API Security Top 10 for API-specific abuse and authorization risks, the OWASP Agentic Top 10 for tool-using systems, and official LGPD/ANPD sources for Brazilian privacy obligations.
