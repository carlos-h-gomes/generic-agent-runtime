# Generic Agent Runtime

A repository-native support and governance layer for software built with AI coding agents.

Generic Agent Runtime (GAR) helps individual builders and engineering teams
define scope, control risky actions, preserve project context, run quality
checks, and keep evidence of what was actually validated.

Its goal is to make AI-assisted development more predictable, reviewable, and
recoverable. GAR is model-neutral: Claude, Codex, Gemini, local models, and
other repository-aware agents can follow the same project rules without
forcing a specific application stack.

## Why use GAR

- **Continuity across sessions and agents.** Project rules, decisions, and
  evidence remain in the repository instead of disappearing with a chat.
- **Clear scope and approvals.** Task contracts distinguish analysis from
  changes and require explicit authorization for risky or external actions.
- **Fewer forgotten engineering concerns.** Security, privacy, architecture,
  testing, accessibility, cost, observability, and release checks are part of
  the workflow.
- **Evidence before release.** Required checks, unavailable tools, skips, and
  blockers are recorded instead of being silently treated as passes.
- **Model and stack neutrality.** Teams keep their chosen tools and
  architecture while different coding agents use the same operating rules.
- **Safer adoption and recovery.** GAR plans before writing, avoids silently
  overwriting differing files, and provides rollback and restoration guidance.

## How it works

- **Repository rules and memory** give agents persistent project context and
  authority boundaries.
- **Proportional task contracts** define the outcome, scope, risk, acceptance
  criteria, approvals, and validation required for managed changes.
- **Engineering skills and quality gates** route work through the disciplines
  that actually apply to the task.
- **Release evidence** connects claims to tests, artifacts, manifests, and
  explicit residual risks.
- **Multi-agent coordination** provides shared task state and file claims. It
  is an advisory coordination layer, not an authentication system.

## Optional model capability profiles

GAR remains usable without any specific premium or separately provisioned
model. Optional, dated profiles add model-aware governance only when a project
chooses them and access is actually available.

- **Daybreak Blue.** For users who already have separately approved and
  provisioned access, GAR includes additional guidance for authorized
  defensive cybersecurity work: access detection, target and scope boundaries,
  budgets, safe fallback, and evaluation requirements.
- **GPT-5.6 Sol.** GAR includes an optional capability profile with access
  detection, explicit budgets, fallbacks, and representative evaluation
  requirements.

GAR does not provide, unlock, request, or prove access to either model. A
profile never expands task scope, target authorization, production permission,
or the controlled-adversarial-testing safety boundaries.

See [Model capability profiles](docs/harness/MODEL-CAPABILITY-PROFILES.md) for
the complete rules and limitations.

## Quick start

Requirements: Python 3.9 or newer. Runtime tooling uses only the Python
standard library.

Validate GAR:

```bash
bash scripts/validate.sh
bash scripts/validate.sh --full
```

Plan and apply adoption to an existing project:

```bash
python scripts/adopt_harness.py plan   --target <project-root> --out plan.json
python scripts/adopt_harness.py apply  --target <project-root> --plan plan.json
python scripts/adopt_harness.py verify --target <project-root>
```

`apply` does not silently overwrite differing files. Review the plan and every
conflict before authorizing replacement. Governance adoption does not create,
migrate, or deploy application code.

See [Safe installation and adoption](docs/harness/INSTALL.md) for the complete
workflow.

## Security, privacy, and workspace support

GAR includes a practical baseline for identity, sessions, authorization,
request and resource limits, API and business-flow abuse, browser controls,
uploads, SSRF, dependencies, incidents, recovery, and LGPD responsibilities.
Start with [Product security and privacy](docs/harness/PRODUCT-SECURITY-PRIVACY.md).

Workspace hygiene is inventory-first and reversible. Nothing is archived
automatically, and purge is not implemented. See
[Workspace hygiene](docs/harness/WORKSPACE-HYGIENE.md).

## Limits

GAR supplies rules, contracts, checks, and evidence around agent work. It does
not secure a downstream application, host, model, network, toolchain, or
deployment by itself. It does not certify LGPD compliance, provide model
access, replace human review, or accept security risk on a person's behalf.

Behavioral claims are limited to the cases and executions recorded in the
[evaluation suite](docs/harness/evaluation-suite.md) and
[`evaluation-run.json`](evaluation-run.json).

## Documentation

- [User manual](docs/USER-MANUAL.md)
- [Technical documentation](docs/TECHNICAL-DOCUMENTATION.md)
- [Security model](docs/harness/SECURITY-MODEL.md)
- [Maintainer guide](docs/harness/MAINTAINER.md)
- [Changelog](CHANGELOG.md)

## Status

Version 8.1.0, released 2026-08-31. See the
[v8.1.0 release](https://github.com/carlos-h-gomes/generic-agent-runtime/releases/tag/v8.1.0).

## License

MIT. See [LICENSE](LICENSE).

## Author

Carlos Henrique Gomes
