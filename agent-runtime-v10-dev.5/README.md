> Current: GAR 10 development candidate, build date 2026-11-10; not released. Release qualification is blocked. Earlier GAR 9 descriptions below are inherited historical behavior; new controls and migration are authoritative in docs/harness/VIBECODER-10.md.

# Generic Agent Runtime

A governance harness for software built with AI coding agents.

AI agents write code fast. What they do not bring is process: a task contract
that defines what "done" means, a quality gate per engineering discipline, and
evidence that survives the end of the chat session. This project supplies that
layer as files in the repository, not as instructions in a prompt.

It is model-neutral. Claude, Codex, Gemini and local models read the same
contracts and write to the same ledger.

## What it does

- **Proportional task contracts.** Authorized managed changes use versioned
  JSON contracts with acceptance criteria, scope and risk. Answers,
  inspections, diagnoses and reviews remain read-only unless persistence is
  separately authorized.
- **Gates per discipline.** Nineteen skills, eleven core and eight specialist
  (security and compliance, architecture and UML, code quality and testing,
  data integration, AI and LLM, FinOps, observability and release, UX and
  product). Managed change and release evidence uses schema-validated gate
  results; read-only reviews return the same conclusions inline.
- **Evidence before release.** A release claim is blocked when a required
  check is unavailable, when a critical finding was silently downgraded, when
  a package carries a sensitive file class, or when UI work has no review
  evidence.
- **Concrete product safety baseline.** A plain-language checklist covers
  identity, sessions, authorization, request limits, API and business-flow
  abuse, browser controls, uploads, SSRF, dependencies, operations, LGPD,
  retention, data-subject rights, incidents and international transfers.
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
- **User-owned architecture and tools.** Brownfield stacks are preserved;
  greenfield choices are requested only when missing. Open profiles govern
  modularity, reuse, solution components and optional model capabilities.
- **Reversible context hygiene.** Read-only inventory and digest-bound plans
  precede explicitly authorized local archive moves. Payloads remain indexed,
  hash-verified and collision-safe to restore; purge is not implemented.
- **Decision interviews and adaptive communication.** An explicit read-only
  interview asks one material question per turn and reuses prior evidence.
  Responses stay compact by default without hiding blockers, skipped checks,
  high risks, approvals, changed files or pending work.
- **Staging-to-production integrity.** Vendor-neutral environment and promotion
  contracts require separate boundaries, the same artifact, bound configuration,
  migration, policy, gates and exact approval, plus rollback and monitoring.

## Requirements

Python 3.11 or newer. Runtime uses the Python standard library only; optional
qualification tools are separately reviewed and are not bundled.

## Quick start

Validate the harness itself:

```powershell
.\scripts\run.ps1 validate --full
```

Adopt governance into an existing project, plan first:

```bash
python scripts/adopt_harness.py plan   --target <project-root> --out plan.json
python scripts/adopt_harness.py apply  --target <project-root> --plan plan.json
python scripts/adopt_harness.py verify --target <project-root>
```

`apply` never overwrites a differing file. It writes rollback copies and
reports unresolved conflicts as incomplete rather than forcing a result.

After recording the user's stack choice, optionally bootstrap the bundled Python/React profile as a separate action:

```bash
python scripts/bootstrap_project.py plan  --target <project-root>
python scripts/bootstrap_project.py apply --target <project-root>
```

Installing governance does not create, migrate or overwrite product code.
Governance adoption, application bootstrap, architecture migration and
deployment are four different authorizations.

Inventory workspace lifecycle state without moving anything:

```bash
python scripts/workspace_hygiene.py inventory --root <workspace>
```

Planning, apply, verify and restore are documented in
`docs/harness/WORKSPACE-HYGIENE.md`. Installing GAR does not create archives.

Validate an environment policy and an optional promotion receipt without making
network calls or deployments:

```bash
python scripts/environment_check.py --policy docs/ai/environment-policy.json --require-production-ready
python scripts/environment_check.py --policy docs/ai/environment-policy.json --promotion docs/ai/releases/<release-id>.promotion.json
```

For an internet-facing product, start the security and privacy review with
`docs/harness/PRODUCT-SECURITY-PRIVACY.md`. Unknown applicable controls block
the release gate rather than being treated as safe defaults.

## Repository layout

| Path | Contents |
|---|---|
| `.agents/skills/` | 19 skills, core and specialist |
| `schemas/` | 22 versioned JSON Schema contracts |
| `scripts/` | validation, packaging, adoption, security and bridge tooling |
| `docs/harness/` | architecture, solution, reuse, model, security, migration and qualification guides |
| `docs/ai/` | the governance surface a governed project receives |
| `scaffold/` | what gets installed into a target repository |
| `project-templates/` | optional Python API plus React TypeScript application template |

Maintainer commands and packaging live in `docs/harness/MAINTAINER.md`.

## What this project does not claim

The harness enforces process, structure and evidence rules. It cannot prove
semantic architecture quality, and it cannot secure a downstream application,
host, model, tool, network or deployment by itself. Human architecture review
and human risk acceptance remain required.

The behavioral evaluation suite in `docs/harness/evaluation-suite.md` specifies
the versioned cases pinned to a fixture hash. `scripts/run_evaluation.py` makes them
runnable and gradable, but execution status is per case and recorded in
`evaluation-run.json`. Until a case appears there with a pass on every required
repeat, it is specification only and no behavioral claim is made for it. Treat
undocumented gate behavior as designed, not as benchmarked.

## Status

Version 10.0.0 local development candidate, built 2026-11-10 and not released. `CHANGELOG.md` covers the path from 3.x
and `docs/harness/MIGRATION-*.md` covers upgrades between majors.

## License

MIT. See `LICENSE`.

## Author

Carlos Henrique Gomes
