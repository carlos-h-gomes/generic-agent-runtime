# Safe Installation and Adoption

Harness files intentionally share names with project governance, scripts, schemas, and memory. Do not extract this archive directly over an active repository.

1. Copy `agent-runtime-v7.0.zip` to an empty staging directory.
2. Verify the separately published archive SHA-256.
3. Extract with a tool that rejects traversal and links, then verify every entry in `MANIFEST.sha256`.
4. Inspect `SBOM.cdx.json` and `PROVENANCE.intoto.json`. The included provenance is deterministic but unsigned.
5. Run `python scripts/runtime_check.py --strict` in staging.
6. Read `docs/harness/HARNESS-ADOPTION-POLICY.md` and run `python scripts/adopt_harness.py plan --target <project-root> --out <plan.json>` from staging.
7. Review every ownership decision, preservation, replacement, skip, and conflict. Reconcile shared conflicts and generate a new plan; do not edit a signed-off plan.
8. Run `apply` only with the exact reviewed plan. Use `--approve-replace` only for a verified prior-Harness upgrade with an acceptable rollback location.
9. Run `verify`, then Harness validation without trusting project code. Review discovered commands before using `--trust-project-code`.
10. Initialize the bridge only after preserving or reconciling existing bridge history.
11. Read every required migration guide. Governance adoption does not authorize application architecture migration.
12. For an explicitly authorized greenfield application, run `python scripts/bootstrap_project.py plan --target <project-root>`. Review every collision before `apply`; never extract `project-templates/` directly over product code.

Release notes are placed in `docs/harness/` so the archive does not overwrite a project root README or changelog. Read the v5, v6, and v7 migration guides when upgrading across multiple major versions.
