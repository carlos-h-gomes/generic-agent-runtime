# Migration 4.2 to 5.0

Version 5.0 is a security-boundary release. Do not extract it over an active repository.

## Breaking behavior

- Project-owned commands require explicit `--trust-project-code`.
- Project commands receive a minimized environment by default. Secret-like environment names are removed.
- `test`, `lint`, `build`, `security`, and `ui` distinguish `PASS`, `FAIL`, `INCOMPLETE`, and `NOT_APPLICABLE`.
- Web releases require an in-date security policy, supported pinned runtime/framework versions, threat and incident artifacts, and applicable scanner evidence.
- Material web UI requires `docs/ai/ui-review.json`, state coverage, responsive evidence, accessibility evidence, and reviewed visual baselines.
- HTTP adversarial execution is plan-only by default. Non-loopback targets and every `POST` require a bounded, unexpired authorization.
- Archives have entry, path, member-size, total-size, type, and compression-ratio limits.

## Safe merge

1. Verify the archive hash and `MANIFEST.sha256` in an empty staging directory.
2. Run `python scripts/runtime_check.py --strict`.
3. Compare governance, schemas, scripts, prompts, and `docs/ai` with the target project.
4. Preserve project decisions, active tasks, risks, incident history, commands, and the live bridge ledger.
5. Merge intentionally; do not replace nearer project instructions.
6. Update the project profile, threat model, incident response, security policy applicability, and UI contract.
7. Run validation without project trust first.
8. Review discovered commands, then explicitly run them with `--trust-project-code`.

## Runtime migration

- Pin Node to an allowed LTS major declared in `security-policy.json`.
- Commit a lockfile and use immutable install mode in CI.
- Pin Next.js to at least the policy floor for its supported major.
- Disable or justify package lifecycle scripts during dependency installation.
- Treat any previously exposed host as an incident: rebuild from trusted images and rotate credentials outside this Harness workflow.

Version 5.0 does not certify a host as clean and does not authorize testing systems you do not own.
