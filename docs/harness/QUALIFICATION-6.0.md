# Qualification 6.0

Status: locally qualified release candidate on 2026-08-03.

## Qualified scope

Harness 6.0 introduces an isolated Python API and React TypeScript/Vite application profile, minimum but extensible topology, thin composition roots, a non-overwriting bootstrap, `SOURCE-OF-TRUTH.md`, technical documentation, and a user manual. Qualification covers the Harness source, generated distribution contract, synthetic fixtures, and local release process. It does not certify a downstream application or deployment.

## Evidence

- `python -B scripts/runtime_check.py --root . --static --strict`: passed 127 bundled structural and contract checks; the optional third-party `jsonschema` package was unavailable, while the bundled JSON Schema validator passed all 10 schemas and their instances.
- `python -B scripts/test_runtime.py`: passed 34 tests with one optional `jsonschema`-dependent test skipped. Negative cases cover traversal, collision, non-overwrite, unsafe template paths, single-file monolith signals, release-document placeholders, archive traversal, compression bounds, and untrusted project-code execution.
- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\run.ps1 validate --full`: passed structural lint, functional tests, bridge doctor, architecture, documentation, security, UI-policy, and deterministic package-plan checks. Project build, lint, and test commands were not applicable because this repository is the Harness distribution, not an application.
- `python -B scripts/security_assurance.py --root . --profile release`: passed policy freshness, restricted-file, credential-pattern, and unsafe-source checks. npm, container, and external advisory checks were not applicable to the dependency-free Harness source.
- `python -B scripts/ui_quality.py --root . --profile release`: correctly not applicable because the Harness source contains no executable web UI and its UI review declares that scope.
- `python -B scripts/adversarial_lab.py plan --root . --plan security/examples/loopback-plan.json`: passed the schema-valid, passive loopback plan without making a network request.
- Two consecutive in-memory package builds produced identical bytes before release writing. The release process separately verifies path safety, resource limits, exact `MANIFEST.sha256` coverage, SBOM, provenance, timestamps, and a fresh extraction.

## Residual conditions

- The behavioral evaluation suite is specification-only until executed on each intended model and host. Broad rollout owners must retain this as an explicit condition.
- Downstream projects must establish their own cost, quota, observability, accessibility, security, deployment, and rollback evidence.
- The bundled provenance is deterministic but unsigned. Publish the final archive SHA-256 through a separate trusted channel.

## Claim boundary

The Harness enforces structure and evidence rules but cannot prove semantic architecture quality or certify a downstream application, host, model, tool, network, data set, or production environment. A skipped or not-applicable check proves only that its trigger was absent from this candidate.
