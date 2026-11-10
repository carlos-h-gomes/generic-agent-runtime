# Harness 4.1 Qualification Record

Release date: 2026-07-17

## Mechanical qualification

The clean runtime distribution was checked with:

- `python -B scripts/runtime_check.py --strict`
- `python -B scripts/test_runtime.py`
- `bash scripts/lint.sh`
- `bash scripts/test.sh`
- `bash scripts/validate.sh`

Results in the release workspace:

- schema, manifest, skill inventory, instruction budgets, Python syntax, and bridge doctor: passed;
- functional suite: 16 tests, 11 passed, 5 platform/source-only skips, 0 failures;
- timeout termination and bounded failure-output tests: passed;
- standard validation: passed;
- PowerShell execution was not available in the Linux release workspace; the PowerShell adapter is syntax-reviewed and remains covered by its parser test when PowerShell is available.

## Behavioral qualification

`evaluation-cases.json` remains the model-host qualification specification. This release does not claim that every Codex desktop version, model, extension, operating system, repository, or third-party command has been executed. Run the evaluation suite and representative repository tasks before organization-wide rollout.

## Crash-safety claim

Harness 4.1 removes known harness-controlled crash amplifiers: indefinite commands, watch mode by default, unbounded terminal output, repeated identical validation attempts, speculative multi-skill loading, and unnecessary bridge subprocess fan-out.

It cannot guarantee that the Codex desktop application itself will never crash. A native application crash can still originate in the application, operating system, graphics stack, extension host, repository size, third-party tools, or resource pressure outside the Harness.
