# Qualification 8.0

Status: v8-dev.1 corrective candidate locally validated on 2026-08-28; promotion to v8-rc.1 and public release recommendation remain withheld pending affected-case and full behavioral requalification.

## Qualified scope

Harness 8.0 adds reuse-first implementation intake, user-owned language and stack selection, open user-named solution components, profile-driven modular architecture checks, and optional GPT-5.6 Sol and Daybreak Blue capability profiles. Qualification covers portable policies, schemas, local validators, compatibility behavior, synthetic fixtures, migration guidance, and deterministic packaging. It does not certify a downstream application, tool, model account, workflow, host, network, deployment, or production environment.

## Lineage

- Canonical maintainer source: public tag `v7.0.0`, commit `51d1e3b915de0d8c207905e1c7c8ea55c6126120`.
- Canonical public v7 runtime asset SHA-256: `89C0F481006FF85E787BB2F939C46B11C1B7C3BE207FE05B39D05437CC51DF3B`; 184 files, 183 manifest payload entries, with path, link, resource, and manifest checks passed.
- The older local v7 archive SHA-256 `986C061F6EDD6D022030FC62866C6068F0C1977A1D5D35FF4206D455CA2E7B2E` and local v7 directory were inspected read-only and left unchanged.

## Evidence

- `python -B scripts/test_runtime.py` passed 48 tests. One optional third-party `jsonschema` meta-schema test was skipped because that package was unavailable; the bundled standard-library contract validator remained active.
- Positive and negative tests cover open feature-oriented profiles, thin and behavior-bearing composition roots, declared dependency direction, manual-adapter incomplete behavior, user-named tools, unresolved authority, v7 compatibility, brownfield preservation, non-overwriting adoption, package safety, security, UI release behavior, fixture-context materialization, typo-artifact presence, and enforced integrity of the behavioral control plane.
- `python -B scripts/runtime_check.py --strict` passed 240 checks with one optional `jsonschema` skip.
- Two consecutive `python -B scripts/package_runtime.py --check` runs produced identical file counts, byte counts, and SHA-256 values before this qualification document was added. Final deterministic checks are repeated after the document is included.
- `python -B scripts/security_assurance.py --profile release` passed policy freshness, restricted-file, credential-pattern, and unsafe-source checks. npm, container, and external advisory scans were correctly not applicable to this standard-library source.
- `python -B scripts/ui_quality.py --profile release` returned not applicable because v8 adds no executable web UI.
- `python -B scripts/adversarial_lab.py plan --plan security/examples/loopback-plan.json` validated two passive synthetic loopback scenarios and made no network request.
- `powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .\scripts\run.ps1 validate --full` completed successfully and composed functional, structural, architecture, documentation, bridge, package, security, and UI-policy checks.
- The final local archive is additionally verified for deterministic rebuild, safe paths and resource bounds, exact manifest coverage, secret classes, SBOM/provenance agreement, and strict validation from a clean extraction. Its SHA-256 belongs in external task/release evidence to avoid a self-referential archive digest.

## Policy outcomes

- Brownfield stacks are preserved unless migration is separately authorized.
- Greenfield code generation reuses an explicit user choice; when a material choice is missing, the agent presents relevant options and reasons and waits for the user.
- Existing modules, contracts, tests, dependencies, and platform capabilities are inventoried before substantial new implementation. Replacement and new responsibilities require evidence.
- Layer-oriented, feature-oriented, mixed, and ecosystem-native structures are valid when ownership and dependency direction are declared. Entrypoints remain thin composition roots.
- Material solution decisions accept user-named tools and require authority, system-of-record, reliability, security, cost, operations, rollback, and kill-switch evidence.
- Python/FastAPI plus React and n8n remain optional compatibility profiles, not universal defaults.
- GPT-5.6 Sol and Daybreak Blue are optional, capability-detected profiles. Availability or model capability never expands authorization.
- Review-only work remains read-only even when production or high risk increases review depth. It reuses existing governance and may cite a formal task, decision, or GateResult only after canonical schema validation.

## Release blocker and residual conditions

- The completed 40-case by three-repeat desktop qualification compared the digest-pinned v8 candidate with canonical v7 across 240 runs. V8 had eight failing families versus twelve for v7, won H5-18, H7-32, H8-34, and H8-35, tied the other 36 families, and showed no comparative regression. Release remained blocked by H4-04, H4-06, H4-10, H5-19, and H5-22 behavior gaps plus evaluator defects in H4-04, H4-05, H4-16, and H7-28.
- V8-dev.1 corrects those response contracts and evaluator defects. The runner now measures H4-04 against an allowed-path reducer, makes H7-28 explicitly plan-only, authorizes bounded read-only subagents only in H4-05, and uses a deterministic file-backed mock with one event and receipt for H4-16. Fresh affected-case qualification remains required before promotion to v8-rc.1; a fresh 40-case by three-repeat qualification is then required before any release recommendation.
- Behavioral quality metrics are required for qualification. Host latency, input tokens, output tokens, and estimated cost are independent economic telemetry. Unavailable Codex Desktop values remain `not_verified`, are never estimated or converted to zero, and prohibit token, latency, or cost-advantage claims without erasing an otherwise decidable behavioral verdict. An accepted same-suite cost baseline is required only for a separate cost comparison.
- No paid OpenAI API benchmark was authorized or executed. API-host measurements may not be substituted for Codex Desktop economic evidence.
- Daybreak Blue access is separately approved and provisioned; this local qualification did not attempt or establish account access.
- GPT-5.6 Sol/high received the completed comparative desktop behavioral qualification, but reliable Desktop token, latency, and cost telemetry was unavailable and remains `not_verified`.
- The optional third-party `jsonschema` meta-schema validator was unavailable. This is a recorded skip, not a pass; the bundled validator passed.
- Deterministic provenance is unsigned. Publish the final digest through a separate trusted channel if a release is approved.
- Every downstream project must still qualify its chosen stack, tools, dependencies, data, security, cost, accessibility, operations, deployment, and rollback.

## Claim boundary

Harness 8.0 supplies governance contracts and bounded local checks. It cannot prove that a downstream application, model, tool, service, credential store, host, network, workflow, or production environment is secure, correct, affordable, observable, accessible, or recoverable.
