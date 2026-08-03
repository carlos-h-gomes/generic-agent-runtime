# Generic Agent Runtime v6

Maintainer source for the Generic Agent Runtime hybrid engineering harness.

Version 6 generates and validates application projects with an isolated Python HTTP API and React TypeScript/Vite frontend. It adds a minimum but extensible directory contract, constructive refusal of single-file monoliths, collision-safe project bootstrap, an authoritative `SOURCE-OF-TRUTH.md` index, and release-grade technical and user documentation.

The portable consumer artifact is `agent-runtime-v6.0.zip`. It keeps application structure under `project-templates/python-react-hybrid/`; installing the Harness does not blindly create or overwrite product code.

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
