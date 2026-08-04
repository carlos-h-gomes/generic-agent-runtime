# Harness v7 adoption and automation governance

Status: implementation authorized on 2026-08-04.

Machine contract: `2026-08-04-harness-v7-adoption-automation.task.json`.

## Accepted decisions

- Derive `agent-runtime-v7.0` from immutable v6.0; never patch a released baseline.
- Separate governance installation, application bootstrap, architecture migration, and Harness upgrade.
- Keep `python-react-hybrid` as the greenfield generation target while admitting brownfield projects through an observed, non-destructive posture.
- Classify automations as `code`, `n8n`, or `hybrid`; code owns authoritative domain behavior and n8n owns bounded edge orchestration.
- Require plan-first, full-preflight, non-overwriting adoption with explicit file ownership and approvals.
- Qualify only with synthetic repositories and workflow decisions; no real downstream project or n8n instance is authorized.

## Release boundary

Local candidate files, tests, documentation, and deterministic packaging are authorized. Deployment, publication, downstream mutation, network installation, production access, credentials, commits, pushes, and external tests are not authorized.

## Handoff

- Baseline ZIP SHA-256: `3857C989F99AA7FBDEFA70627706F445FF05B4EC86D206FB6E85B04C70F04122`.
- Design: approved by the workspace owner; formal gates recorded beside this task.
- Next action: create the v7 successor and implement the approved contracts.
