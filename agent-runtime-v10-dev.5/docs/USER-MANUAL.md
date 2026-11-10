# GAR 10 User Manual

**Status:** release candidate, built 2026-11-10; not officially released. **Documented version:** 10.0.0. **Audience:** vibecoders, agent-assisted builders, and repository maintainers. **Owner:** ProcessSurge GAR maintainers. **Last reviewed:** 2026-11-10.

## What GAR does

GAR gives coding agents and their users a shared set of repository rules, task contracts, specialist skills, local validators, and evidence requirements. It helps turn a request into scoped work, show which checks ran, and keep failures or missing proof visible.

GAR is a governance aid. It does not write or deploy your application by itself, provision infrastructure, guarantee that an agent follows instructions, or secure your computer, application, server, network, or production environment.

## Before you install

GAR 10.0.0 is still a local candidate. The current public release is GAR 8.1.0. Wait for an official v10.0.0 release before adopting it in a maintained project. The candidate archive checksum is not a public release checksum.

For an official release, use Python 3.11 or newer, verify the archive checksum from the official release page, extract into a new staging folder, inspect the manifest, and run:

```text
python -B scripts/runtime_check.py --static --strict
```

Do not extract over project files. Read `docs/harness/INSTALL.md` and `HARNESS-ADOPTION-POLICY.md` before adoption.

## First project workflow

1. Describe the outcome, intended user, and acceptance criteria. Make unresolved business or stack choices explicit.
2. Ask the agent to inventory the project and read its `AGENTS.md`, current `docs/ai/`, and relevant skills before making changes.
3. For managed multi-file or high-risk work, review the task contract. It should state scope, affected files, risk, authorization, gates, validation, exclusions, and the next action.
4. Review the architecture/security/UX/data decisions that apply before implementation. GAR's skills provide procedures; they do not grant permission.
5. Review the proposed diff and run the smallest relevant checks. Keep failed checks, skips, and unknown results visible.
6. Before a release, verify every required gate and the exact archive. Missing proof remains incomplete.

For adoption into an existing project, GAR creates a read-only plan first. Review every preserved, replaced, skipped, or conflicting file before applying. A Harness upgrade never authorizes changes to application code or deployment.

## Skills and optional tools

The GAR package includes 19 skills for core work and specialist gates. Load only the skills triggered by the task. A skill is a procedure, not a permission grant or security boundary.

External skills, scanners, browser tools, and adapters are not installed automatically. Before use, the maintainer must review their exact source, revision, license, dependencies, provenance, data/network behavior, update owner, and rollback. A report parser only checks report structure; it does not prove that the underlying tool ran.

## Feedback and recovery

GAR results use explicit states: a check can pass, fail, be incomplete, or be not applicable with a reason. If a check fails, ask the agent to report the exact command, exit code, relevant evidence, and a bounded next step. Do not treat a skipped or unavailable scanner as a pass.

If a plan conflicts with existing project files, stop and resolve the conflict. Do not force an overwrite. For workspace hygiene, inventory first and review a digest-bound plan; apply, restore, and deletion are separate actions. Restore never overwrites a live path.

For rollback, restore the preserved prior GAR files and validate the project's existing governance. GAR cannot restore application data or roll back a deployment.

## Roles and permissions

The user owns product choices, scope, and protected actions. The agent can perform only the local changes authorized by the task and user. Public GitHub changes, publication, production, credentials, destructive operations, purchases, and external security testing need explicit scope and approval. A passing local check does not grant those permissions.

## Accessibility and interaction

GAR is delivered as Markdown documentation, JSON contracts, and command-line scripts; this package does not include a graphical interface. For downstream applications, use the UX skill and the project's applicable accessibility standard. A build or automated scan alone is not accessibility approval.

## Troubleshooting and known limits

- **Python too old:** install/use Python 3.11 or newer for GAR 10 commands.
- **Incomplete validation:** check whether an optional validator is missing or a platform-specific test was skipped. Record it as not verified until covered.
- **Host/network permissions:** GAR's operation preflight compares records; it cannot intercept host tool calls. Verify isolation in the actual host and do not claim network denial based on configuration text alone.
- **External tool output:** check artifact identity, run status, target, scope, and digest. A parseable report is not proof of a successful or safe scan.
- **Release status:** candidate is not published. Use the official repository and release tag as the source for release files and hashes.

For installation or security concerns, consult `docs/harness/INSTALL.md`, `SECURITY-MODEL.md`, `SECURITY-OPERATIONS.md`, and the current release notes. Do not include secrets or private customer data in issue reports.
