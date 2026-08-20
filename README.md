# Generic Agent Runtime

A repository-native harness for AI coding agents.

Generic Agent Runtime adds a shared operating layer to your project so coding agents can work with consistent **rules, skills, task contracts and quality gates**.

Instead of relying on a long prompt or on instructions that disappear when the chat ends, the harness keeps the workflow inside the repository.

Claude, Codex, Gemini and other agents can read the same contracts and follow the same project rules.

## What you get

- **Agent rules** — persistent instructions for how agents should work inside the repository.
- **Skills** — reusable engineering guidance for security, architecture, testing, integrations, AI, observability, UX and more.
- **Task contracts** — explicit scope, acceptance criteria and risk level for each piece of work.
- **Quality gates** — checks that must pass before work can be considered complete.
- **Multi-agent coordination** — shared task state and file claims so multiple agents can work in the same repository.
- **Security boundaries** — protections against untrusted project instructions, unsafe execution and common agent failure modes.
- **Evidence** — machine-readable records of what was checked, approved and produced.

## Why use a harness?

Coding agents are very good at generating code.

The harder problem is keeping their behavior consistent across tasks, sessions and models.

Without a shared harness, every conversation starts from scratch:

- What can the agent change?
- What does "done" mean?
- Which checks are required?
- When should it ask for approval?
- How should risky operations be handled?
- What happens when two agents work on the same repository?

Generic Agent Runtime keeps those decisions in the project itself.

The repository becomes the source of truth for **how agents are expected to work**.

## Quick start

Validate the harness:

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

Start a new project:

```bash
python scripts/bootstrap_project.py plan  --target <project-root>
python scripts/bootstrap_project.py apply --target <project-root>
```

The adoption process does not silently overwrite existing project files. Conflicts are reported and rollback copies are created when necessary.

## How it changes agent behavior

Once the harness is part of a repository, the agent has project-level instructions before it starts changing code.

Depending on the task and risk level, it can be required to:

- understand the task contract before implementation;
- stay inside the declared scope;
- ask for approval before risky actions;
- run the appropriate engineering skills;
- produce quality-gate results;
- record evidence of checks performed;
- coordinate file ownership with other agents;
- refuse or ignore untrusted instructions found inside project content.

The goal is not to make an agent autonomous.

The goal is to make its behavior **more predictable, reviewable and repeatable**.

## Security

The harness also includes controls for common risks when coding agents interact with real repositories.

Project-owned scripts are treated as untrusted by default and are not executed until explicitly authorized with:

```bash
--trust-project-code
```

Commands use argument arrays, minimized environments, timeouts, bounded output and process-tree cleanup.

The project also contains behavioral evaluation cases covering scenarios such as:

- prompt injection through repository content;
- attempts to expose secrets or tokens;
- attempts to modify files outside the authorized scope;
- unsafe execution;
- silent gate downgrades.

See `docs/harness/evaluation-suite.md` for the evaluation suite and its recorded execution status.

## Repository layout

| Path | Purpose |
| --- | --- |
| `.agents/skills/` | Core and specialist agent skills |
| `schemas/` | Versioned contracts and schemas |
| `scripts/` | Validation, adoption, packaging, security and coordination tooling |
| `docs/harness/` | Harness architecture, security model and qualification documentation |
| `docs/ai/` | Governance files installed into governed projects |
| `scaffold/` | Files adopted into an existing repository |
| `project-templates/` | Optional application templates |

## Model neutral

The harness is not tied to a specific AI provider.

It is designed so different coding agents can operate over the same repository-level contracts and workflow.

Examples include:

- Claude
- Codex
- Gemini
- local models
- other repository-aware coding agents

Agent-specific adapters can exist, but the project rules remain in the repository.

## What this project does not do

Generic Agent Runtime does not guarantee that generated code is correct or secure.

It does not replace architecture review, security review or human approval.

The harness provides **process, boundaries, checks and evidence** around agent work.

It makes behavior easier to control and inspect; it does not turn probabilistic models into deterministic software.

## Requirements

Python 3.9 or newer.

Runtime tooling uses the Python standard library and has no runtime dependencies.

## Status

Version 7.0.0.

See `CHANGELOG.md` for release history and `docs/harness/MIGRATION-*.md` for migration guides.

## License

MIT. See `LICENSE`.

## Author

Carlos Henrique Gomes
