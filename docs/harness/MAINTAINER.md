# Generic Agent Runtime v7

Maintainer source for the Generic Agent Runtime hybrid engineering harness.

Version 7 adds plan-first Harness adoption for greenfield, brownfield, and prior-Harness projects, plus machine-governed `code`, `n8n`, and `hybrid` automation decisions. Governance installation no longer implies application bootstrap or architecture migration. The Python HTTP API plus React TypeScript/Vite profile remains the greenfield generation target.

The portable consumer artifact is `agent-runtime-v7.0.zip`. It keeps application structure under `project-templates/python-react-hybrid/`; installing the Harness does not blindly create or overwrite product code.

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

Bootstrap a greenfield application only as a separate action:

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

The Harness enforces process, structure, and evidence rules but cannot prove semantic architecture quality or secure a downstream application, host, model, tool, network, or deployment by itself.
