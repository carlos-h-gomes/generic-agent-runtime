# Generic Agent Runtime

A repository-native harness for AI coding agents.

Generic Agent Runtime adds a shared operating layer to your project so coding agents can work with consistent **rules, skills, task contracts and quality gates**.

Instead of relying on a long prompt or instructions that disappear when the chat ends, the harness keeps the workflow inside the repository.

Claude, Codex, Gemini and other coding agents can read the same rules, follow the same contracts and produce evidence using the same process.

## What it does

- **Rules** — persistent instructions that define how agents are expected to work inside the repository.
- **Skills** — reusable engineering guidance for areas such as security, architecture, testing, integrations, AI, observability and UX.
- **Task contracts** — versioned definitions of scope, acceptance criteria and risk level for each unit of work.
- **Quality gates** — machine-readable checks that determine whether required engineering conditions were satisfied.
- **Security boundaries** — protections around untrusted instructions, project-owned code, sensitive files and risky operations.
- **Evidence** — records of checks, approvals and results that survive the end of a chat session.
- **Multi-agent coordination** — shared task state, event history and per-file claims so different agents can work in the same repository without silently overwriting each other.

## Why use a harness?

Coding agents can generate code quickly.

The harder problem is keeping their behavior consistent across tasks, sessions and models.

Without a shared harness, every conversation has to redefine questions such as:

- What can the agent change?
- What is outside the task scope?
- What does "done" mean?
- Which checks are required?
- When should the agent ask for approval?
- Which actions are considered risky?
- How should multiple agents work in the same repository?

Generic Agent Runtime keeps those decisions in the project itself.

The repository becomes the source of truth for **how agents are expected to work**.

## How it changes agent behavior

Once the harness is added to a repository, the agent receives project-level working rules before changing code.

Depending on the task and its risk level, the agent can be required to:

- understand the task contract before implementation;
- stay inside the declared scope;
- ask for approval before risky actions;
- use the appropriate engineering skills;
- run required quality gates;
- record evidence of checks performed;
- coordinate file ownership with other agents;
- reject or ignore untrusted instructions found inside project content.

The goal is not to make an agent autonomous.

The goal is to make agent behavior **more predictable, reviewable and repeatable**.

## Quick start

Validate the harness itself:

```bash
bash scripts/validate.sh
bash scripts/validate.sh --full
```

Add the harness to an existing project:

```bash
python scripts/adopt_harness.py plan   --target <project-root> --out plan.json
python scripts/adopt_harness.py apply  --target <project-root> --plan plan.json
python scripts/adopt_harness.py verify --target <project-root>
```

`apply` does not silently overwrite differing files. It creates rollback copies and reports unresolved conflicts instead of forcing a result.

Start a new project:

```bash
python scripts/bootstrap_project.py plan  --target <project-root>
python scripts/bootstrap_project.py apply --target <project-root>
```

Adding the harness does not create, migrate or overwrite application code.

Harness installation, application bootstrap, architecture migration and deployment are separate actions.

## Security

Repository content is not automatically trusted.

Project-owned scripts are not executed until the operator explicitly allows it with:

```bash
--trust-project-code
```

Commands run with argument arrays, a minimized environment, timeouts, bounded output and process-tree cleanup.

The project also includes behavioral tests for scenarios such as:

- malicious repository instructions attempting prompt injection;
- attempts to expose tokens or secrets;
- attempts to modify files outside the authorized scope;
- unsafe project-code execution;
- silent downgrades of critical findings;
- release claims without required evidence.

The evaluation suite is defined in `docs/harness/evaluation-suite.md`.

`scripts/run_evaluation.py` makes the cases runnable and records their results in `evaluation-run.json`.

A case is only treated as validated when the required executions are recorded as passing.

## Multi-agent coordination

The harness includes a file-based coordination protocol for repositories where more than one agent may be working.

It uses:

- an append-only event ledger;
- a materialized task board;
- per-file claims;
- shared task state.

This allows agents from different vendors to coordinate through the repository without depending on the same chat session or model provider.

The coordination layer is advisory. It is not an authentication or access-control system.

## Supply chain evidence

Release packaging can produce:

- deterministic package contents;
- a SHA-256 manifest;
- a CycloneDX 1.7 SBOM;
- SLSA-shaped provenance.

These artifacts provide integrity and build evidence.

They do not prove the identity or authenticity of the person or system that produced the package.

## Repository layout

| Path | Purpose |
| --- | --- |
| `.agents/skills/` | Core and specialist agent skills |
| `schemas/` | Versioned task, gate and evidence contracts |
| `scripts/` | Validation, adoption, packaging, security and coordination tooling |
| `docs/harness/` | Harness architecture, security model, migration and qualification documentation |
| `docs/ai/` | Agent rules and workflow files installed into projects |
| `scaffold/` | Files added when adopting the harness into an existing repository |
| `project-templates/` | Optional application templates |

Maintainer commands and packaging details are documented in `docs/harness/MAINTAINER.md`.

## Model neutral

Generic Agent Runtime is not tied to a specific AI provider.

Different coding agents can operate over the same repository-level rules, contracts and workflow.

Examples include:

- Claude
- Codex
- Gemini
- local models
- other repository-aware coding agents

Agent-specific adapters may exist, but the project rules remain in the repository.

## What this project does not claim

Generic Agent Runtime does not guarantee that generated code is correct, secure or architecturally sound.

It does not secure the downstream application, model, host, network, toolchain or deployment environment by itself.

Human review and human risk acceptance are still required where appropriate.

The harness provides **rules, boundaries, checks and evidence** around agent work.

It makes behavior easier to control and inspect; it does not turn probabilistic models into deterministic software.

## Requirements

Python 3.9 or newer.

Runtime tooling uses the Python standard library and has no runtime dependencies.

## Status

Version 7.0.0, released 2026-08-04.

See `CHANGELOG.md` for release history and `docs/harness/MIGRATION-*.md` for migration guides between major versions.

## License

MIT. See `LICENSE`.

## Author

Carlos Henrique Gomes
