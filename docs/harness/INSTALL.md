# Safe Installation

Harness files intentionally share names with project governance, scripts, schemas, and memory. Do not extract this archive directly over an active repository.

1. Copy `agent-runtime-v6.0.zip` to an empty staging directory.
2. Verify the separately published archive SHA-256.
3. Extract with a tool that rejects traversal and links, then verify every entry in `MANIFEST.sha256`.
4. Inspect `SBOM.cdx.json` and `PROVENANCE.intoto.json`. The included provenance is deterministic but unsigned.
5. Run `python scripts/runtime_check.py --strict` in staging.
6. Inventory collisions against the target repository, including `AGENTS.md`, adapters, `.agents/`, `scripts/`, `schemas/`, `prompt-templates/`, `security-policy.json`, and `docs/ai/`.
7. Merge deliberately. Preserve nearer project instructions, verified commands, decisions, risks, active tasks, incident records, and the live bridge ledger.
8. Run Harness validation without trusting project code. Review discovered commands before using `--trust-project-code`.
9. Initialize the bridge only after preserving or reconciling existing bridge history.
10. Read `SOURCE-OF-TRUTH.md`, `docs/ai/architecture-policy.json`, and `docs/harness/MIGRATION-5.0-6.0.md` before application migration.
11. Run `python scripts/bootstrap_project.py plan --target <project-root>`. Review every collision before `apply`; never extract `project-templates/` directly over product code.

Release notes are placed in `docs/harness/` so the archive does not overwrite a project root README or changelog. Read both the v5 and v6 migration guides when upgrading across multiple major versions.
