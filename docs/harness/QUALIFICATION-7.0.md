# Qualification 7.0

Status: locally qualified release candidate on 2026-08-04.

## Qualified scope

Harness 7.0 adds two governed capabilities: a machine-readable decision for choosing code, n8n, or hybrid automation, and a plan/apply/verify adoption workflow for greenfield, brownfield, and prior-Harness projects. Qualification covers the portable policy, schemas, local scripts, synthetic fixtures, migration behavior, and deterministic release process. It does not certify a downstream application, n8n instance, host, deployment, or production workflow.

## Evidence

- The immutable v6.0 baseline archive SHA-256 is `3857C989F99AA7FBDEFA70627706F445FF05B4EC86D206FB6E85B04C70F04122`. Its 167 manifest payload entries matched the archive and the overlapping extracted source content.
- `python -B scripts/test_runtime.py` passed 41 tests; one optional third-party `jsonschema` test was skipped because that package was unavailable. The bundled validator remained active. Negative cases cover unsafe paths, maintainer-source adoption, conflicting shared files, target drift, partial-write prevention, replacement approvals, n8n authority blockers, and missing n8n controls.
- `python -B scripts/runtime_check.py --strict` passed the bundled structural, schema, policy, task, gate, fixture, documentation, and release-contract checks.
- `python -B scripts/package_runtime.py --check` produced a deterministic in-memory package plan and verified explicit adoption ownership for every included path.
- `python -B scripts/security_assurance.py --profile release` passed applicable policy-freshness, restricted-file, credential-pattern, and unsafe-source checks; dependency, container, and external-advisory checks were not applicable to this standard-library Harness source.
- `python -B scripts/ui_quality.py --profile release` correctly returned not applicable because this release adds no executable web UI.
- `python -B scripts/adversarial_lab.py plan --plan security/examples/loopback-plan.json` validated a passive synthetic loopback plan without a network request.
- `powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .\scripts\run.ps1 validate --full` is the release gate that composes structural, functional, bridge, architecture, documentation, security, UI-policy, and package-plan checks.
- The final archive is additionally checked for safe paths, resource bounds, exact manifest coverage, SBOM/provenance agreement, deterministic rebuild, and strict validation from a fresh extraction. Its SHA-256 is recorded in the workspace task evidence outside the archive, avoiding a self-referential digest.

## Policy outcomes

- Code is the authoritative plane for business invariants, authorization, transactions, complex state, and other hard-blocker cases.
- n8n is eligible for bounded edge orchestration only when required production controls and evidence exist.
- Hybrid is preferred when n8n coordinates integrations while versioned code APIs retain authoritative behavior.
- Brownfield governance adoption preserves the detected application stack and does not generate application directories.
- Prior-Harness upgrades preserve project-owned memory, require explicit replacement approval for Harness-owned content, and retain rollback material.

## Residual conditions

- The behavioral suite must still be run on every intended model, reasoning setting, and tool host before broad rollout.
- A real n8n deployment must supply its own environment-separation, credential, webhook, risky-node, retention, backup/restore, observability, cost-cap, and kill-switch evidence.
- Each downstream repository must review the generated plan, reconcile shared files explicitly, test application behavior, and qualify deployment and rollback in its own environment.
- The bundled provenance is deterministic but unsigned; publish the final archive digest through a separate trusted channel.

## Claim boundary

Harness 7.0 supplies governance contracts and bounded local checks. It cannot prove that a downstream application, workflow, host, model, credential store, network, or production environment is secure, correct, affordable, observable, or recoverable.
