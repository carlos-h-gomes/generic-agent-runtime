# Qualification 9.0

Status: v9-dev.2 local correction validated on 2026-09-05. Public release, behavioral qualification and live-environment claims remain withheld. Final artifact evidence is tracked in the maintainer task `2026-09-05-harness-v9-promotion-correction`.

## Qualified scope

GAR 9 adds explicit read-only decision interviews, adaptive communication, and vendor-neutral environment/promotion contracts. This correction covers v2 schemas, local semantic checks, negative tests, mechanical regression, documentation and archive integrity. It does not certify a downstream application, provider, account, credential store, environment, deployment, network, production system, model, or tool. Local test coverage is not complete behavioral compatibility.

## Lineage

- Immutable baseline archive: `agent-runtime-v8.1.zip`.
- Baseline SHA-256: `5D7F083A4CCD8BED2A3DF6C4023BE41606A41611175FACD33478C6FDFB7932F6`.
- The baseline archive contained 215 file entries and was deterministically reproduced from reviewed v8.1 maintainer source before v9 changes.
- The immediate reviewed predecessor is v9-dev.1, archive SHA-256 `7B4891AFF7056016139040973DA2FC63D0AF47CD2C1F0C9E235291E7FBB3DAFC`. Its source/archive and three Sol/high H9-46 results remain preserved historical evidence.

## Evidence and policy outcomes

- The full local validation invoked `python -B scripts/test_runtime.py`: 91 tests ran, 89 passed and 2 were skipped. Optional third-party `jsonschema` was unavailable, and ordinary Windows symlink creation lacked host privilege; the bundled schema validator and Windows junction boundary test passed.
- `.\scripts\run.ps1 validate --full` exited `0`, including structural, functional, architecture, documentation, bridge, package-plan, security, and UI-applicability checks. Project lint/test/build were correctly not applicable because no downstream application exists in the Harness source.
- The focused v9 suite covers interview/communication contracts and environment/promotion pass, incomplete, shared-boundary, production-data exception, drift, reused approval, concurrency, smoke, monitoring, stable exit-code, and read-only behavior.
- The correction focused suite passed 26 tests with no skips. It independently covers failed production checks, predeployment monitoring/recovery, causal order and validity, policy/staging evidence binding, structural parity, v1 rejection, and legitimate intermediate and rollback states. A separate read-only Astra review ran 21 synthetic checks with expected outcomes and reported no new blocker within that scope; this was not model behavioral qualification.
- Strict structural validation covers every schema, manifest, skill, governed task/gate, example, policy, package requirement, instruction budget, and digest-pinned behavioral specification.
- Full regression, security, UI applicability, documentation, architecture, bridge, deterministic package, archive safety, manifest, SBOM/provenance, and clean-extraction evidence is recorded in the governing v9 task.
- Normal production promotion requires verified staging, the same identity-bound artifact/configuration/migration/policy, passed tests/gates, rehearsed rollback, exact approval, no concurrency conflict, smoke checks, monitoring, and recoverable rollback.
- Planned defaults are intentionally incomplete. Adoption does not invent live environment evidence or provision anything.
- Communication depth cannot suppress mandatory safety/release facts. Completing an interview does not authorize implementation.

## Residual conditions

- The twelve new v9 behavioral cases are digest-pinned specifications and require three-repeat execution before any behavioral release claim. The full legacy behavioral suite remains trigger-based under the approved impact analysis.
- ASTRA-01–04 on the reviewed predecessor motivated environment/promotion contracts 2.0. Earlier H9-46 Sol/high passes cannot qualify this new archive; final selected runs must use the final digest and a declared host/model/effort. Historical deliberately incomplete v1 input snippets in behavioral fixtures are invalid evidence scenarios, not v2 contract examples.
- Optional scanners or host telemetry unavailable during local qualification remain `not_verified`, never passed or inferred.
- Deterministic provenance is unsigned. Publish the final archive digest through a separate trusted channel if release is approved.
- Provider prices, live isolation, credentials, deployments, rollback objectives and monitoring must be verified per downstream project.
- No Git, public publication, cloud provisioning, credential operation, deployment, production mutation, paid benchmark, or external communication is part of this qualification.

## Claim boundary

GAR 9 supplies governance contracts and bounded local checks. It cannot prove that a downstream application, provider, environment, deployment, host, network, model, tool, security posture, availability, affordability, accessibility, or recovery is correct or safe.
