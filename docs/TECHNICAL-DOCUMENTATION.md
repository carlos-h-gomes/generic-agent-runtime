# Generic Agent Runtime 8.1 — Technical Documentation

Status: released 2026-08-31.
Documented product version: 8.1.0
Owner: ProcessSurge Harness maintainer
Last reviewed: 2026-08-31

## Scope and architecture

GAR is a standard-library-only governance and validation distribution. Version 8.1 adds a dormant workspace-lifecycle boundary to the v8.0 authority kernel. It consists of `workspace-hygiene-policy.json`, three v1 JSON Schema contracts, `core/workspace-hygiene`, and `scripts/workspace_hygiene.py`. Existing workspaces receive no archive directory during installation or adoption.

The helper separates read-only inventory and plan generation from authorized apply and restore. Archive bundles remain within the declared workspace, use the nearest parent ownership boundary, and preserve original relative paths beneath immutable archive IDs. Active discovery ignores payload content while indexes and manifests remain queryable.

## Data and recovery contracts

The plan records owner, reason, confidence, positive classification evidence, references checked, per-file hashes, strategic destination, exclusions, rollback, and restore consequences. Its ID is derived from canonical plan content and apply rechecks the workspace fingerprint.

The manifest records the plan digest, authorization reference, exact moves, verification result, and restore state. The append-only move journal supports ordered reversal. The bounded archive index uses atomic replacement to prevent partial records. Apply and restore preflight all paths, hashes, references, links, collisions, and manifest location before mutation.

See `docs/harness/WORKSPACE-HYGIENE.md` for commands and failure states. `schemas/archive-plan.schema.json`, `schemas/archive-manifest.schema.json`, and `schemas/workspace-hygiene-policy.schema.json` are the machine contracts.

## Security and compatibility

The default policy protects authority, active tasks, source/build paths, schemas, scripts, tests, release/dependency artifacts, links/reparse points, secrets, captures, databases, logs, and ambiguous material. Unknown state never becomes automatic archival. The feature performs no network operation and implements no purge.

The downstream product baseline in `docs/harness/PRODUCT-SECURITY-PRIVACY.md` operationalizes the security and privacy gate across identity and session handling, resource/tenant authorization, request and cost budgets, sensitive business-flow abuse, browser and API boundaries, supply chain, runtime containment, recovery, and LGPD. It is a requirements and evidence guide, not enforcement or certification.

GAR 8.0 task, GateResult, bridge, architecture, solution, reuse, model, and adoption contracts remain readable. Adoption treats the hygiene policy as Harness-owned and non-overwriting. Archive application to an existing workspace remains a separate explicit action.

## Validation and release boundary

The source must pass focused round-trip and negative tests, the full runtime suite, strict validation, full PowerShell validation, deterministic packaging, and fresh-extraction verification before promotion. Public release, Git operations, deployment, production mutation, current-workspace archival, and external communication require separate authorization.

GAR governs process and evidence; it does not secure an application, host, VPS, network, model, tool, or deployment by itself.
