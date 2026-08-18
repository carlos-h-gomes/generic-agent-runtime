# Generic Agent Runtime

A governance harness for software built with AI coding agents.

AI agents write code fast. What they do not bring is process: a task contract
that defines what "done" means, a quality gate per engineering discipline, and
evidence that survives the end of the chat session. This project supplies that
layer as files in the repository, not as instructions in a prompt.

It is model-neutral. Claude, Codex, Gemini and local models read the same
contracts and write to the same ledger.

## What it does

- **Task contracts.** Every unit of work is a versioned JSON contract with
  acceptance criteria, scope and risk level, not a chat message.
- **Gates per discipline.** Seventeen skills, nine core and eight specialist
  (security and compliance, architecture and UML, code quality and testing,
  data integration, AI and LLM, FinOps, observability and release, UX and
  product). Each produces a machine-readable gate result.
- **Evidence before release.** A release claim is blocked when a required
  check is unavailable, when a critical finding was silently downgraded, when
  a package carries a sensitive file class, or when UI work has no review
  evidence.
- **Multi-agent coordination.** A file-based protocol: append-only event ledger
  plus a materialized board, with per-file claims, so agents from different
  vendors work in the same repository without overwriting each other. The
  bridge is advisory coordination, not authentication.
- **Untrusted execution by default.** Project-owned scripts are not executed
  until the operator passes `--trust-project-code`. Commands run with argument
  arrays, a minimized environment, timeouts, bounded output and process-tree
  cleanup.
- **Supply chain evidence.** Deterministic packaging with a SHA-256 manifest, a
  CycloneDX 1.7 SBOM and SLSA-shaped provenance, with an explicit statement
  that provenance proves integrity, not authenticity.

## Requirements

Python 3.9 or newer. Standard library only, no runtime dependencies.

## Quick start

Validate the harness itself:

```bash
bash scripts/validate.sh          # structural lint, functional tests, runtime and package checks
bash scripts/validate.sh --full   # adds security assurance and UI quality assurance
```

Adopt governance into an existing project, plan first:

```bash
python scripts/adopt_harness.py plan   --target <project-root> --out plan.json
python scripts/adopt_harness.py apply  --target <project-root> --plan plan.json
python scripts/adopt_harness.py verify --target <project-root>
```

`apply` never overwrites a differing file. It writes rollback copies and
reports unresolved conflicts as incomplete rather than forcing a result.

Bootstrap a greenfield application, as a separate and explicit action:

```bash
python scripts/bootstrap_project.py plan  --target <project-root>
python scripts/bootstrap_project.py apply --target <project-root>
```

Installing governance does not create, migrate or overwrite product code.
Governance adoption, application bootstrap, architecture migration and
deployment are four different authorizations.

## Repository layout

| Path | Contents |
|---|---|
| `.agents/skills/` | 17 skills, core and specialist |
| `schemas/` | 12 versioned JSON Schema contracts |
| `scripts/` | validation, packaging, adoption, security and bridge tooling |
| `docs/harness/` | security model, hybrid architecture, migration and qualification guides |
| `docs/ai/` | the governance surface a governed project receives |
| `scaffold/` | what gets installed into a target repository |
| `project-templates/` | optional Python API plus React TypeScript application template |

Maintainer commands and packaging live in `docs/harness/MAINTAINER.md`.

## What this project does not claim

The harness enforces process, structure and evidence rules. It cannot prove
semantic architecture quality, and it cannot secure a downstream application,
host, model, tool, network or deployment by itself. Human architecture review
and human risk acceptance remain required.

The behavioral evaluation suite in `docs/harness/evaluation-suite.md` is a
specification. Its cases are pinned to a fixture hash but have not been run
against a live model, and the file says so. Treat documented gate behavior as
designed, not as benchmarked.

## Status

Version 7.0.0, released 2026-08-04. `CHANGELOG.md` covers the path from 3.x
and `docs/harness/MIGRATION-*.md` covers upgrades between majors.

## License

MIT. See `LICENSE`.

## Author

Carlos Henrique Gomes
