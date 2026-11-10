# Generic Agent Runtime 10.0.0 — Maintainer Guide

**Status:** local release candidate, not officially released. The public GAR baseline remains v8.1.0 until a separately qualified v10.0.0 release is published.

GAR is a portable, model-neutral governance layer for agent-assisted software work. It contains authority instructions, 19 core/specialist skills, schemas, bounded local validators, optional project templates, adoption and release guidance, and evaluation fixtures. The optional Python/React template is not the required application architecture.

## Source and release boundaries

- Published GAR 8.1 and GAR 9 artifacts remain immutable.
- Build corrections in a new versioned successor; do not patch previous candidates or reuse their behavioral results as proof for a new archive.
- Record the source baseline hash before changes and the final archive hash after qualification.
- Keep maintainer task runs and live state out of the consumer package.
- Do not claim host, application, network, or production security from GAR checks alone.
- A release requires fresh applicable gates, independent review where required, exact source/archive correspondence, a complete manifest, a clean extraction, rollback guidance, and authenticated publisher provenance where supported.

## Local verification commands

Run from a reviewed maintainer source root with Python 3.11 or newer:

```text
python -B scripts/test_runtime.py
python -B scripts/runtime_check.py --strict
python -B scripts/security_assurance.py --profile release
python -B scripts/package_runtime.py --check
python -B scripts/runtime_check.py --strict --archive agent-runtime-v10.0.zip
```

Run full platform-specific validation only with its documented bounded runner. Record exact exit codes and skips; a generic successful command does not replace behavioral, security, UX, provenance, or independent-review evidence.

## Packaging

The package builder uses the deterministic `build_date` for ZIP timestamps and the SBOM. A `candidate` manifest must have `released: null`; a `released` manifest must bind `released` to the build date. Set release status/date only in the final qualified source. Rebuild deterministically, verify `MANIFEST.sha256`, inspect archive paths/types/size bounds, and validate a new extraction before publication.

The embedded `PROVENANCE.intoto.json` is a deterministic statement of inputs and output. It is unsigned unless a trusted publisher attestation is separately produced and verified. Do not describe the embedded statement as authenticated provenance.

## Qualification blockers

See `QUALIFICATION-10.0.md` and the maintainer's active task contract for the current exact status. Known historical blockers include incomplete full final-artifact behavioral repeats, incomplete independent Bandit triage/provenance review, a failed network-disabled loopback boundary probe, and missing representative human-comprehension evidence. Old evidence is not transferable to a corrected archive.

## Downstream adoption

Use the plan-first workflow in `INSTALL.md` and `HARNESS-ADOPTION-POLICY.md`. Adoption does not authorize application code changes, stack migration, infrastructure setup, production promotion, or deployment. Any discovered project command requires its own trust review.
