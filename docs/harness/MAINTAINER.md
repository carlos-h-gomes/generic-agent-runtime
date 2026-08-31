# Generic Agent Runtime v8.1

Maintainer source for the Generic Agent Runtime governance harness.

Version 8.1 retains v8 reuse-first work, user-owned open architecture and solution decisions, generalized composition-root checks, and optional model profiles. It adds reversible, evidence-based workspace hygiene. Governance installation, workspace archival, stack selection, application bootstrap, migration, and deployment remain separate.

The candidate artifact is `agent-runtime-v8.1.zip`. Python/React remains an optional template under `project-templates/python-react-hybrid/`; it is never applied without the user's stack choice and an explicit bootstrap action.

`QUALIFICATION-8.0.md` records the local evidence and the remaining behavioral-host release blocker. Do not convert candidate status to a public release claim until that condition is closed and the owner separately approves Git and publication actions.

`WORKSPACE-HYGIENE.md` defines the v8.1 archive lifecycle. Development and packaging never authorize applying that lifecycle to maintainer or user workspace material.

## Maintainer commands

Windows:

```powershell
.\scripts\run.ps1 validate
.\scripts\run.ps1 validate --full
.\scripts\run.ps1 package --check
```

POSIX:

```bash
bash scripts/validate.sh
bash scripts/validate.sh --full
bash scripts/package.sh --check
```

## Downstream bootstrap

Adopt Harness governance from a clean portable extraction:

```text
python scripts/adopt_harness.py plan --target <project-root> --out <plan.json>
python scripts/adopt_harness.py apply --target <project-root> --plan <plan.json>
python scripts/adopt_harness.py verify --target <project-root>
```

Validate an automation decision:

```text
python scripts/automation_decision.py <decision.json>
```

Validate the v8 open solution decision:

```text
python scripts/solution_decision.py <decision.json>
```

Bootstrap the optional Python/React profile only after user selection and as a separate action:

Inspect first:

```text
python scripts/bootstrap_project.py plan --target <project-root>
```

Apply only after reviewing the plan:

```text
python scripts/bootstrap_project.py apply --target <project-root>
```

Differing existing files block apply. `--skip-existing` permits a non-overwriting merge and still reports unresolved conflicts as incomplete.

## Release claim

Behavioral qualification uses `scripts/run_evaluation.py`. Every run must pin
the candidate archive digest, model, reasoning effort, host, and repeat. Use
the example manual-review and metrics files under `docs/harness/examples/`;
missing transcripts, review, required behavioral quality metrics, repeats, or
authenticated execution remains incomplete. Host latency, token, and estimated
cost telemetry is reported independently as `not_verified` when unavailable;
never infer it or claim an economic advantage. A same-suite cost baseline is
required only for a separate cost comparison.
Materialization must expose intended non-secret fixture context inside the
synthetic target, and grading must independently pass protected workspace
integrity. A case missing the artifact or context required by its prompt is
void fixture evidence, not a model failure.

The Harness enforces process, structure, and evidence rules but cannot prove semantic architecture quality or secure a downstream application, host, model, tool, network, or deployment by itself.
