# Task Notes — Executable behavioral evaluation runner

Machine contract: `2026-08-18-evaluation-runner.task.json` using `schemas/task-contract.schema.json`.

Gate results: `2026-08-18-evaluation-runner.gates/<gate>.json`.

## Context and evidence read

| Pointer | Why it matters | Verified / inferred / historical |
|---|---|---|
| `docs/harness/evaluation-cases.json` | Declares `execution_status: specification_only_not_executed` and carries 32 cases with hard assertions | Verified |
| `docs/harness/evaluation-fixtures.json` | 28 synthetic repositories, fully materializable as file maps | Verified |
| `docs/harness/evaluation-suite.md` | Stated 27 cases while the suite contains 32 | Verified |
| `docs/harness/SECURITY-MODEL.md` | Release invariant: no credentials in gate results or packages | Verified |

## Clarifications and assumptions

| Question or assumption | Decision / evidence | Impact |
|---|---|---|
| Should the runner invoke the agent host? | No. Hosts differ per operator and per platform, and embedding one would bind the suite to a vendor | The runner materializes and grades; the operator runs the host between the two steps |
| What happens to an assertion the tool cannot decide? | It is reported as `incomplete` and blocks the case from passing until a human records a verdict | Prevents the grader from manufacturing evidence |
| Should raw transcripts be stored in results? | No. Results carry aggregates, observed counts and sanitized pointers | Keeps the release invariant on sensitive data |

## Gate index

| Gate | Phase | Status | Revision | GateResult path |
|---|---|---|---|---|
| code_quality_testing | pre_release | passed | 1 | `2026-08-18-evaluation-runner.gates/code_quality_testing.json` |
| security_compliance | pre_release | passed | 1 | `2026-08-18-evaluation-runner.gates/security_compliance.json` |
| observability_release | pre_release | passed | 1 | `2026-08-18-evaluation-runner.gates/observability_release.json` |
| architecture_uml | pre_release | not_applicable | 1 | `2026-08-18-evaluation-runner.gates/architecture_uml.json` |
| ux_product | pre_release | not_applicable | 1 | `2026-08-18-evaluation-runner.gates/ux_product.json` |
| data_integration | pre_release | not_applicable | 1 | `2026-08-18-evaluation-runner.gates/data_integration.json` |
| finops | pre_release | not_applicable | 1 | `2026-08-18-evaluation-runner.gates/finops.json` |
| ai_llm | pre_release | not_applicable | 1 | `2026-08-18-evaluation-runner.gates/ai_llm.json` |

## Implementation notes

Three subcommands, each with a single responsibility.

`materialize` verifies the pinned fixture digest, writes the fixture repository into an
empty directory, writes the case prompt to a separate file and records a hash snapshot
of every file before the run.

`grade` recomputes the snapshot, diffs it, and decides each hard assertion by one of
three methods: filesystem, transcript or manual. Filesystem assertions are decided from
the hash diff. Transcript assertions are decided from the captured output. Everything
else is `incomplete` until a verdict appears in `manual-verdicts.json`.

`aggregate` combines run results, enforces the suite's own `repeats_per_case` rule and
states how many of the specified cases were attempted at all, so partial coverage can
never read as full coverage.

## Documentation impact

- Classification: `technical`
- Reason: operators gain an execution procedure and a grading contract for the suite
- Required artifacts: `docs/harness/evaluation-suite.md`

## Validation attempts

One attempt. `bash scripts/validate.sh` passed. Four manual scenarios were exercised
against synthetic fixtures: clean run, dirty run, undecidable assertion and repeat
shortfall. Each behaved as specified.
