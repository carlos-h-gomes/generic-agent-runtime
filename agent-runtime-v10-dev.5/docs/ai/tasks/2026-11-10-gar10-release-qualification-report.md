# GAR 10 dev.5 qualification report

Date: 2026-11-10. Status: **release blocked**. Candidate source: `agent-runtime-v10-dev.5/`.

## Provenance and baselines

- Public `main` remains v8.1-era commit `1d6a4b372bb6db81fa774039d05d967de863743d` (2026-09-03). A shallow clone was created in `gar-github-main-checkout/` for isolated review; no remote refs were changed.
- Immutable v8.1 archive SHA-256: `5d7f083a4ccd8bed2a3df6c4023be41606a41611175facd33478c6fdfb7932f6`.
- Immutable v9-dev.2 archive SHA-256: `9c90c56c89ab53a223d04cab242b94bef7125e8c56bbfb8a6fc1e24d55b7ec49`.
- Source candidate derived from the verified v10-dev.4 distribution; dev.1–dev.4 and all historical evidence remain unchanged. dev.4 archive SHA-256: `d04811ab071b0618e9e0c0473604f25411bb18d753b4d80e8b669f7d2a7913b0`.
- dev.5 maintainer source tree (excluding the active qualification task bundle, archive and temporary extraction): 276 files; deterministic fingerprint `fc0bcc02fe5449d0932b11a6ce7c7455bacad68de15633eb562ede83e682ad15`.
- Final dev.5 package candidate: `agent-runtime-v10-dev.5/agent-runtime-v10.0.zip`, 248 files, 370777 bytes; SHA-256 `ba330e5376808f820d34fbb82171f7552117030fed0aed18966efae8bc4d386e`.
- `harness.json`: version `10.0.0`, `release_status: candidate`, build date `2026-11-10`, release date `null`. It is not an official release.

## Corrections and validation

- Fixed the release/build date mismatch and deterministic package SBOM, provenance fields and timestamps.
- Restored the missing maintainer scaffold and README in the successor; fixed the package builder's duplicate changelog path; filled previously placeholder technical and user manuals.
- Refreshed the expiring security policy from official Node.js, CPython, Next.js, React and Vite sources and aligned the positive Next.js test fixture. Policy checked 2026-11-10; expires 2026-12-10.
- Full regression suite: `python -B scripts/safe_exec.py --timeout 180 --tail-lines 100 -- python -B scripts/test_runtime.py` — exit 0; 112 tests, 110 passed, 2 expected skips (optional `jsonschema` dependency and ordinary Windows symlink privilege).
- Source strict validation: `python -B scripts/runtime_check.py --strict` — exit 0; 64 pass, 1 optional skip (`jsonschema` meta-schema validator unavailable). All eight current gate records and the task contract validate.
- Security assurance: `python -B scripts/security_assurance.py --profile release` — exit 0; 4 pass, 3 not applicable (no Node project, Dockerfile or applicable dependency advisory scan).
- UI quality: no GAR UI detected; UI review is not applicable. This does not substitute for human-comprehension evidence about GAR's communication behavior.
- Package plan and archive were deterministic; final package plan SHA-256 is the same as the archive above. Archive strict validation — exit 0; 78 pass, 1 optional skip (`jsonschema` meta-schema validator unavailable; final rerun 2026-11-10).
- Fresh extraction `gar-v10-dev5-clean-extract-20261110-final/`: strict validation exit 0; 17 pass, 2 skips (fresh distribution has no active task contract; optional `jsonschema` meta-schema validator unavailable).
- No fresh exact-dev.5 external SAST scan was produced: Bandit is not installed in the active Windows Python environment, and `wsl.exe --status` returned access denied. No unpinned install was attempted. No publisher signature/attestation or independent security review was produced in this phase.

## Skills inventory

GAR contains 19 first-party skills: 11 core and 8 specialist. Against the local v8.1 tree and public GitHub `main`, 32 skill files are byte-for-byte the same; four local skill texts have evolved (`core/context-memory`, `core/task-triage`, `core/validation`, `specialists/observability-release`) and `core/grill-me` is new. No remote-first-party skill update was discovered in the exact current `main` tree. The three user-installed game skills belong to another project and remain excluded. Playwright, axe-core, OSV-Scanner, Gitleaks, and third-party skills remain research candidates pending exact artifact, license, provenance, permissions and maintenance review.

## GitHub synchronization

Created draft PR [#1](https://github.com/carlos-h-gomes/generic-agent-runtime/pull/1) from `codex/gar10-dev5-review-20261110` to `main`. It adds 288 files under the versioned candidate directory, preserves main and the v8.1 release, and excludes the unqualified ZIP and generated temp/extraction folders. Git committed bytes were compared to all 288 local candidate files with zero mismatches. No GitHub checks/workflow runs are configured for this commit. The PR remains draft and unmerged.

## Release blockers

1. Security gate remains blocked: the prior network-disabled WSL/Codex profile reached a loopback listener; Bandit 1.9.4 exited 1 with 49 low findings, including 13 runtime findings still awaiting contextual independent disposition; publisher provenance is unsigned and unverified. Local checks in this report do not clear those findings.
2. UX gate remains blocked: representative human-comprehension evidence is missing.
3. AI/LLM gate remains blocked: required final-artifact behavior and independent grading/repetition remain incomplete; no additional account spend or reset was used.
4. Release gate remains blocked until the exact candidate commit/archive has authenticated publisher provenance, a clean review and all gates have fresh evidence.
5. GitHub synchronization is a **draft review PR only**. Do not merge, tag or publish v10.0.0 until blockers 1–4 are resolved and the release contract is revalidated.

## Next steps

1. Obtain an independent security reviewer to disposition the loopback boundary and exact SAST findings; fix actionable issues and rerun scanners on the final source.
2. Capture representative comprehension results for Portuguese compact/normal/failure outputs, or revise and retest the communication contract.
3. Complete permitted final-artifact behavior qualification and independent grading without exceeding the existing account/cost limits.
4. Rebuild from the reviewed commit, regenerate signed provenance using the repository's approved publisher, then repeat all gates and clean-extraction checks.
5. Only then convert the draft PR to review-ready, merge, tag and attach the exact verified archive; preserve the current v8.1 release and rollback path.
6. Begin the separate GAR evolution track: review newer skills and exact external tool artifacts individually, then implement only selected integrations with source, license, provenance, permission and maintenance evidence.
