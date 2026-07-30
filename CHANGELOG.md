# Changelog

## 5.0.0 - 2026-07-30

### Security assurance

- Added an expiring, official-source-backed security policy with Node and Next.js lifecycle floors.
- Project-owned test, lint, and build scripts require explicit trust and receive a minimized environment by default.
- Added self-contained source, secret-pattern, sensitive-file, runtime/framework, and deployment-boundary checks plus optional dependency advisory scanning.
- Added bounded archive entry, name, member, aggregate, type, and compression-ratio checks before ZIP content is read.
- Added Windows Job Object and POSIX process-group cleanup for command descendants.
- Added CycloneDX 1.7 SBOM, deterministic SLSA-shaped provenance, and explicit integrity-versus-authenticity guidance.

### Controlled adversarial testing

- Added versioned authorized-target and security-test-plan schemas.
- Added a dry-run-first HTTP contract runner with loopback defaults, exact-origin scope, expiry, safe methods, request/response budgets, redirect blocking, and inert fixtures.
- Explicitly excludes destructive payloads, persistence, cryptominers, credential attacks, unrestricted shells, flooding, evasion, and ambiguous targets.

### UI quality

- Added a versioned UI review contract and static quality gate.
- Requires user outcome, critical journeys, complete states, design-system fit, WCAG 2.2 AA evidence, responsive/content stress, deterministic visual regression, keyboard/manual review, and reviewed diffs.
- Strengthened the UX specialist and release checklist so compile/lint success cannot substitute for UI approval.

### Qualification and compatibility

- Added a bundled JSON Schema keyword-subset validator for required contracts when the optional `jsonschema` package is absent.
- Preserved task v1, GateResult v1, and bridge event v2 compatibility.
- Added v5 migration, incident, VPS/web isolation, security testing, and UI quality documentation.
- Expanded functional and synthetic behavioral regression cases.
