# Installation and Adoption

**GAR 10.0.0 is a local release candidate, built 2026-11-10. It is not an official release.** The security, behavioral, independent-review, and user-comprehension gates remain open. Do not treat this candidate as production-qualified or install it over an active project.

GAR is repository governance and validation guidance. It does not install application dependencies, change the application's stack, provision infrastructure, deploy, or enforce host/network permissions by itself. See `USER-MANUAL.md` and `HARNESS-ADOPTION-POLICY.md` before adoption.

## Requirements

- Python 3.11 or newer for GAR command-line validation and adoption scripts.
- A clean staging directory separate from the target application repository.
- A separately verified archive SHA-256 before extraction. The archive's own manifest checks integrity but does not authenticate its publisher.

## Safe installation after official release

1. Obtain the exact v10.0.0 archive and release tag from the official repository.
2. Verify the archive SHA-256 against the release page and confirm the tag points to the reviewed source commit.
3. Inspect the ZIP for path traversal, duplicate names, links, oversized entries, and suspicious compression ratios before extraction.
4. Extract into a new empty staging directory. Never extract directly over an active repository.
5. Verify every entry in `MANIFEST.sha256`, inspect `SBOM.cdx.json` and `PROVENANCE.intoto.json`, and read `SECURITY.md` plus the release notes. The deterministic local provenance document is not, by itself, an authenticated publisher attestation.
6. Run `python -B scripts/runtime_check.py --static --strict` in staging. Review any skip or incomplete result.
7. Read `docs/harness/HARNESS-ADOPTION-POLICY.md`, inventory the target read-only, and create an adoption plan:

   ```text
   python -B scripts/adopt_harness.py plan --target <project-root> --out plan.json
   ```

8. Review every ownership, preservation, replacement, skip, and conflict decision. Resolve conflicts and regenerate the plan; do not edit a reviewed plan.
9. Apply only the exact reviewed plan. Use `--approve-replace` only when upgrading a verified prior GAR installation and a tested rollback location exists.
10. Run `verify`, then validate the target without trusting project code. Review every discovered command before using `--trust-project-code`.
11. Initialize or reconcile the bridge only after preserving existing bridge history. Workspace hygiene is dormant; inventory and plan first, and require separate authorization for apply or restore.
12. Treat application bootstrap, architecture migration, environment provisioning, production promotion, and deployment as separate decisions and authorizations.

## During qualification

The current local candidate is not distributed as a public release. Its latest recorded archive is dev.4, SHA-256 `d04811ab071b0618e9e0c0473604f25411bb18d753b4d80e8b669f7d2a7913b0`; this hash is historical candidate evidence, not a v10.0.0 release digest. Do not use it as a published release checksum.

Read `MIGRATION-9.0-10.0.md`, `QUALIFICATION-10.0.md`, `VIBECODER-10.md`, and the root task contract before adopting any later candidate. Missing release-gate evidence remains incomplete.
