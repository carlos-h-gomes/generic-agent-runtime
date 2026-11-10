# GAR 10 release qualification plan

Date: 2026-11-10. Owner: workspace owner. Contract: `2026-11-10-gar10-release-qualification.task.json`.

## Baselines and current facts

- Public GitHub `main` is still the GAR 8.1.0 line; the connected repository history reports latest commit `1d6a4b372bb6db81fa774039d05d967de863743d` (`Update SECURITY.md`, 2026-09-03).
- Local GAR 8.1 release archive SHA-256: `5d7f083a4ccd8bed2a3df6c4023be41606a41611175facd33478c6fdfb7932f6`; 215 ZIP entries, 309757 bytes. Its maintainer directory has 278 files and a distinct tree fingerprint; it is not a byte-for-byte extraction of the ZIP.
- Local GAR 9 baseline archive SHA-256: `9c90c56c89ab53a223d04cab242b94bef7125e8c56bbfb8a6fc1e24d55b7ec49`.
- The immutable dev.4 archive was safely inspected and extracted to the new `agent-runtime-v10-dev.5/` successor. dev.5 corrects candidate/release dates, package metadata and changelog mapping, fills technical/user documentation, and refreshes current supported-runtime/security references.
- Current dev.5 source tree has 276 files and fingerprint `03128031ae3cfeb3c2bbd75da82bed371e93d35a9e77c2cc19366eb6041d0e51`. Candidate ZIP SHA-256 `ba330e5376808f820d34fbb82171f7552117030fed0aed18966efae8bc4d386e`; 248 files, 370777 bytes. Candidate release date is null; deterministic build date is 2026-11-10.
- The original workspace and version directories have no Git metadata. An isolated shallow checkout of public `main` now exists at `gar-github-main-checkout/`; the candidate's archive-derived relationship to the public source is recorded, not represented as native Git ancestry.
- `harness.json` now uses `release_status: candidate`, `build_date: 2026-11-10`, and `released: null` until a qualified official release.

## Execution sequence

1. Completed read-only baseline/source reconciliation; use the internally manifested dev.4 ZIP as the immutable candidate snapshot. Prior versions and evidence remain unchanged.
2. Review architecture, security, UX, quality, AI, data, FinOps and release constraints. Keep external-tool/skill integration out of GAR10 unless exact artifacts pass admission; maintain a separate evidence-backed shortlist for post-release evolution.
3. Completed the dev.5 successor and current user/maintainer documentation. Updated candidate/release metadata and the dated security-policy snapshot.
4. Completed local regression, source, security-assurance, package, archive and fresh-extraction checks. Skips and unknowns remain incomplete; they do not override blocked independent gates.
5. Prepare a draft GitHub feature branch/PR containing the reviewed v10 candidate source while preserving `main` and the v8.1 release. Do not merge, tag or publish while security, human-comprehension, behavioral qualification or authenticated provenance gates remain blocked.
6. After v10 is qualified, start the planned GAR evolution: external skill/tool admission, integration adapters, comparative behavioral evaluation and representative comprehension work.

## Skill scope

The local GAR10 candidate contains 19 skills: four differ from v8.1/GitHub `main` (`context-memory`, `task-triage`, `validation`, `observability-release`) and `grill-me` is new. A tree comparison at `main` commit `1d6a4b372bb6db81fa774039d05d967de863743d` found 32 identical skill files, these four local updates, one new skill and no remote-only skills. The three game skills installed in the user's Codex scope are separately recorded and excluded. Playwright, axe-core, OSV-Scanner, Gitleaks and Agent Skills conformance remain candidates; no external skill/tool artifact is currently qualified for bundling. See `2026-11-10-gar10-release-qualification-report.md`.

## Current release blockers to close

- Independent contextual review of the exact final source's SAST findings, the failed loopback/network-boundary result, and publisher provenance.
- The WSL/Codex network-disabled profile connected to a loopback listener; determine whether this is a product claim, host limitation or release-blocking boundary, using independent security review and no weakened controls.
- Final-archive behavioral suite/repeats, independent grading, representative human-comprehension evidence, and publisher provenance attestations remain incomplete.

No files in prior release/candidate directories are to be edited. No direct write to GitHub `main` is planned; synchronization uses a reviewed branch/PR. Publication remains conditional on all mandatory gates.
