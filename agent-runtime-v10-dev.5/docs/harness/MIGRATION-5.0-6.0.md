# Migration from Harness 5.0 to 6.0

Version 6 is a breaking application-architecture policy release. Keep the v5 archive and its published SHA-256 as the rollback baseline. Never extract v6 directly over an active repository.

## New projects

1. Install the Harness through the safe staging and merge procedure.
2. Review `SOURCE-OF-TRUTH.md` and initialize project identity, version, authoritative pointers, risks, and current evidence.
3. Run `python scripts/bootstrap_project.py plan --target <project-root>`.
4. Review collisions and then run `apply`. Do not use `--skip-existing` unless a human has decided how every differing file will be reconciled.
5. Generate supported, pinned Python and React/Vite dependencies with lockfiles; the structural template intentionally does not install or guess dependency versions.
6. Complete the architecture, threat, UI, technical documentation, and user-manual contracts before release.

## Existing compliant hybrid projects

- Map existing roots and modules to the mandatory profile.
- If names differ, record a migration decision and move deliberately; the bootstrap does not overwrite or rename existing files.
- Run architecture and documentation checks before trusted project tests.
- Preserve existing decisions, tasks, commands, risks, incident records, and release evidence.

## Existing monoliths

- Do not mechanically split files by size alone.
- First identify routes, use cases, domain/data ownership, transport schemas, reusable UI, feature state, and external integrations.
- Establish the API contract and dependency direction.
- Move one coherent responsibility at a time with characterization and contract tests.
- Keep old entrypoints as temporary adapters only when a dated migration task owns their removal.

## Compatibility

Task v1, GateResult v1, and bridge event v2 remain readable. V6 adds optional task documentation-impact metadata and new architecture/template contracts. Official application release is blocked until the v6 structure, truth index, technical documentation, and user manual satisfy their release profiles.

## Rollback

Because v6 never mutates v5, rollback the Harness by restoring the separately verified v5 distribution. Application code already migrated to the hybrid structure needs its own project rollback or compatibility plan; replacing the Harness alone does not reverse product changes.
