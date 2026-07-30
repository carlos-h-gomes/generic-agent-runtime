# Qualification 5.0

Qualification date: 2026-07-30.

## Evidence

- The v4.2 archive baseline was hashed and compared byte-for-byte with its extracted directory before implementation.
- Bundled strict contract validation passed with eight schemas; the optional third-party `jsonschema` meta-validator was unavailable and reported as a skip.
- Twenty-nine functional regression tests cover bridge integrity, bounded execution, Windows process handling, environment minimization, explicit project trust, archive traversal and compression limits, deterministic packaging, stale/current Next and Node policy, incomplete UI review, and unauthorized/ambiguous adversarial targets.
- Built-in source, secret-pattern, sensitive-file, policy, lifecycle, and deployment checks passed or were correctly `NOT_APPLICABLE` for this framework-independent runtime.
- The UI gate correctly reports `NOT_APPLICABLE` because the Harness runtime itself has no web UI; downstream detected web UIs require an approved machine contract.
- The example adversarial plan passed schema and guardrail validation in plan mode with zero network requests.
- The package plan was deterministic across repeated builds and a fresh extracted consumer distribution passed runtime validation.

## Claim boundary

Behavioral model evaluation remains a pinned, executable specification and was not run against a remote model in this source qualification. Optional external dependency advisory scanning was not applicable to the Harness source because it has no package manifest or runtime dependency set. No production host, VPS, external target, or application was tested or certified.

The separately distributed archive digest must be published outside the archive and verified before extraction.
