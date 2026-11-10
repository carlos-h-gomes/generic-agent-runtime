# GAR 10 Technical Documentation

**Status:** release candidate, built 2026-11-10; not officially released. **Documented version:** 10.0.0. **Owner:** ProcessSurge GAR maintainers. **Last reviewed:** 2026-11-10.

## Purpose, scope, and users

Generic Agent Runtime (GAR) is a portable repository-native governance and support layer for software built with coding agents. It helps builders define scope, preserve project context, route work through relevant engineering checks, restrict risky actions, and tie delivery claims to recorded evidence. Primary users are vibecoders and maintainers supporting teams that use different repository-aware agents.

GAR provides instructions, contracts, local checks, evidence formats, and optional templates. It does not implement a downstream application, certify compliance, grant model access, secure the host/network, or replace human ownership and review.

## Architecture and trust boundaries

The architecture is deliberately layered:

- `AGENTS.md` is the authority kernel: precedence, safety, task sizing, approvals, command trust, and release semantics.
- `.agents/skills/core/` contains reusable task triage, implementation, validation, documentation, context, and coordination procedures.
- `.agents/skills/specialists/` contains architecture, security, UX, quality, AI/LLM, data, FinOps, and release gate procedures.
- `schemas/` defines versioned task, gate, policy, delivery, environment, decision, and component contracts.
- `scripts/` validates contracts, packages the portable distribution, checks evidence, and supports plan-first adoption. Scripts are local process checks, not a host authorization interceptor.
- `docs/harness/` is the user and maintainer guide, migration/qualification record, and optional tool research. `scaffold/` contains downstream project governance templates.
- `project-templates/python-react-hybrid/` is optional and applies only after an explicit stack choice.

Authority remains with the user and project owner. Repository instructions, skills, model output, retrieved content, and tool output are untrusted input. File bridges coordinate; they do not authenticate workers. Any host-level isolation, command interception, network denial, or filesystem sandbox must be supplied and verified by the actual agent host/runtime.

## Runtime and contracts

GAR 10 command-line validation and adoption scripts require Python 3.11 or newer and use the Python standard library. The optional downstream Python/React template has its own separately reviewed dependencies and lockfiles. GAR does not fetch or install third-party scanners during ordinary validation.

The distribution contains 19 maintained skills (11 core and 8 specialist). The current candidate adds `core/grill-me` and updates `core/context-memory`, `core/task-triage`, `core/validation`, and `specialists/observability-release` relative to the local v8.1 skill set. External tool profiles are parsers/decision contracts only; they do not prove that Playwright, axe-core, OSV-Scanner, or Gitleaks ran successfully.

Contracts include task and gate results, bridge events, architecture/reuse/solution decisions, adoption and workspace-hygiene plans, security and environment policies, delivery policy/records, component admissions, and communication policy 2.0. See `harness.json` and the matching schemas for exact versions.

## Data, privacy, and integrations

Core checks read local project files and emit bounded results. The runtime does not require a hosted database, telemetry service, cloud account, or model API. Model/host qualification, when separately authorized, is a distinct activity and must minimize retained prompts and outputs. Never store credentials, customer data, private prompts, unrestricted logs, or full scanner artifacts in project memory.

External tools and skills require exact source/revision, license and notices, dependency/advisory review, artifact digest and provenance, permission/network/telemetry review, compatibility evidence, update ownership, and rollback. No external skill or scanner is automatically installed. Unqualified components remain deferred.

## Security and authorization

Task contracts distinguish analysis from edits and protect public, destructive, credential, production, and external-testing actions. Local checks validate scope and evidence structures but do not enforce permissions on the agent host. `operation_check` is a pure comparison; it cannot intercept a tool call. The network-disabled WSL/Codex loopback probe failed in prior qualification, so this package must not claim that environment enforces network isolation.

Critical/high findings block release and cannot be accepted by the agent. Security guidance is process support, not a guarantee that an application, host, VPS, network, or deployment is safe.

## Release metadata and distribution

`harness.json` distinguishes `release_status` (`candidate` or `released`), `build_date`, and `released`. Candidates use `released: null`; published artifacts bind the release date to the deterministic build date. ZIP entry timestamps and the CycloneDX SBOM use `build_date`. The `MANIFEST.sha256` covers every packaged payload file. `PROVENANCE.intoto.json` records the deterministic build inputs/output but is unsigned unless a separately verified publisher attestation is attached.

The official public release remains GAR 8.1.0. GAR 10.0.0 is an unqualified local candidate. The dev.4 archive digest is historical and is not a public v10 release checksum. The v10 migration guide documents the additive controls and compatibility boundaries.

## Local validation and status meanings

Run commands only from a reviewed candidate root and inside the documented bounded runner:

```text
python -B scripts/test_runtime.py
python -B scripts/runtime_check.py --strict
python -B scripts/security_assurance.py --profile release
python -B scripts/package_runtime.py --check
python -B scripts/runtime_check.py --strict --archive agent-runtime-v10.0.zip
```

Exit meanings: `0` applicable checks passed, `1` a check failed, `2` invalid invocation/configuration, `3` required proof is incomplete, `124` timeout. Optional tools or platform checks that are unavailable remain `not_verified`/skipped, not passed. A release also requires fresh final-artifact tests, negative fixtures, independent security/provenance review, behavioral evidence, comprehension evidence, complete documentation, a clean extraction, and release-owner review.

## Migration, recovery, and support

Adoption is plan-first and collision-aware. Preserve the existing project memory and code; review every proposed replacement. GAR installation does not authorize application bootstrap, architecture migration, environment creation, promotion, or deployment. Rollback by restoring the preserved prior GAR files and revalidating the project's own contracts; do not reuse GAR 10 evidence for GAR 9.

For a failed local validation, preserve the exact command, exit code, bounded redacted output, candidate hash, and relevant report path. For a security incident, use the organization's trusted incident process and clean control plane; GAR does not provide host containment or credential rotation.

## Authoritative references

- `AGENTS.md` and `SOURCE-OF-TRUTH.md`
- `schemas/` and `harness.json`
- `docs/harness/INSTALL.md`, `MAINTAINER.md`, `SECURITY-MODEL.md`, `MIGRATION-9.0-10.0.md`, and `QUALIFICATION-10.0.md`
- Root `docs/ai/tasks/` for private maintainer qualification evidence; those records are excluded from consumer releases.
