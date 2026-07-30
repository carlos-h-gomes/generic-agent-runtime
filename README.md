# Generic Agent Runtime v5

Maintainer source for the security- and UI-assurance release of the Generic Agent Runtime Harness.

The portable consumer artifact is `agent-runtime-v5.0.zip`. It contains a small authority kernel, on-demand skills, clean project-memory templates, versioned schemas, bounded validation, safe adversarial-test contracts, UI review enforcement, SBOM, provenance, and an internal file manifest.

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

All commands are bounded. Project-owned scripts require an explicit trust flag and receive a minimized environment. Adversarial HTTP execution defaults to loopback; `plan` has no network effect.

## Release claim

The Harness improves process controls and evidence. It does not by itself secure, clean, deploy, monitor, or prove the safety of an application, VPS, container, network, model, tool, or production environment.
