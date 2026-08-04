# Migration from Harness 6.0 to 7.0

Version 7 is a breaking admission and automation-governance release. Keep the v6 archive and its separately published SHA-256 as the rollback baseline. Never extract v7 over an active repository.

## What changes

- Governance adoption, application bootstrap, architecture migration, and deployment are separate actions.
- Existing projects are admitted through an observed brownfield posture instead of being silently treated as Python/React targets.
- Material automations require a `code`, `n8n`, or `hybrid` execution-plane decision.
- `adopt_harness.py` adds manifest-verified plan/apply/verify behavior and explicit file ownership.
- Task v1, GateResult v1, bridge event v2, security, UI, and project-template v1 remain readable. Automation decision v1 and adoption plan v1 are additive contracts.

## Upgrade procedure

1. Verify `agent-runtime-v7.0.zip` through a separately published digest and `MANIFEST.sha256` in a clean staging directory.
2. Keep the current v6 distribution, target backup, and project-specific rollback procedure.
3. Run `python scripts/adopt_harness.py plan --target <project-root> --out <plan.json>` from staging.
4. Review every replacement, preservation, skip, and shared-file conflict. Reconcile shared conflicts manually and rerun plan with `--accept-shared <path>` for each reviewed target file.
5. Apply only the final plan. Use `--approve-replace` only after confirming the target contains a supported prior Harness and the rollback path is acceptable.
6. Run `verify`, strict Harness validation, and project-specific checks only after separately trusting project code.
7. Initialize or reconcile `.harness/adoption-state.json`, architecture policy, automation decisions, technical documentation, and user manual as applicable.

## Brownfield architecture

An upgrade does not migrate product code. Existing v6 projects already using `python-react-hybrid` retain that policy. A project that had v6 files manually inserted into another topology must first record its actual architecture; do not create missing Python/React directories merely to satisfy a validator.

## Rollback

Restore the verified v6 distribution and the project files preserved under `.harness/rollback/<plan-digest>/`. Remove or retain newly created v7-only files only through a reviewed project-specific rollback plan. Replacing Harness files does not reverse any separately authorized product migration.
