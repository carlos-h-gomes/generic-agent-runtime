# Security Model

The Harness reduces accidental authority and makes missing evidence visible. It is not a sandbox, an EDR, a vulnerability scanner, or proof that an application is secure.

## Trust boundaries

1. Harness source and signed/verified release inputs.
2. Project repository content, including package scripts and test configuration.
3. Child processes and their environment.
4. Build and deployment artifacts.
5. Network targets used for defensive testing.
6. Human approvals and risk acceptance.

Project repository content is untrusted until the operator passes `--trust-project-code`. The command runner uses argument arrays, timeouts, bounded output, a minimized environment, and process-tree cleanup. This reduces exposure but cannot make arbitrary code safe; high-risk execution belongs in a disposable VM or container with no credentials and constrained network access.

## Release invariants

- No implicit external attack traffic.
- No credentials embedded in test plans, logs, gate results, or packages.
- No release claim while a required check is unavailable or incomplete.
- No supported-web release on an expired policy or blocked runtime/framework version.
- No internet-facing release without applying `PRODUCT-SECURITY-PRIVACY.md` and recording every applicable unknown as incomplete.
- No material UI release without machine-readable review evidence.
- No package containing links, reparse points, sensitive file classes, live tasks, or live bridge history.
- No critical/high finding is silently downgraded.

## Supply-chain evidence

The archive includes `MANIFEST.sha256`, a CycloneDX SBOM, and deterministic SLSA-shaped provenance. The provenance is unsigned metadata: it records the local build shape and baseline, but does not authenticate the publisher. Authenticity requires an external signing and verification system.

## Residual risks

Language-level scanners are heuristic; dependency tools may be unavailable; a trusted project command can still exploit the OS or toolchain; DNS can change between checks; and UI evidence can be stale or fraudulent. Use isolated CI runners, pinned tools, short-lived credentials, egress controls, artifact signing, and independent review for production releases.
