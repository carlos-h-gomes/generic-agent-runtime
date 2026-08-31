# Project Source of Truth

Status: UNINITIALIZED
Truth schema: 1.0
Last reconciled: not set
Owner: not set

This file is the authoritative index of current project facts and their detailed sources. It does not replace `AGENTS.md`, active tasks, decisions, schemas, code, tests, technical documentation, or the user manual. Platform and user authority apply before repository instructions.

## Project identity and release

- Product: `<PROJECT_NAME>`
- Purpose: `<PROJECT_PURPOSE>`
- Current official version: `<VERSION>`
- Release status: development
- Release artifact and digest: not released

## Architecture profile

- Profile: selection or observation pending; record the approved `profile_id`
- Languages/frameworks/platforms: record the user's choice or verified brownfield stack
- Organization: record layered, feature, mixed, or ecosystem-native responsibilities and dependency direction
- Interface contracts: record the project-specific paths here
- Directory policy: `docs/ai/architecture-policy.json`
- Directory responsibilities: `docs/architecture/DIRECTORY-MAP.md`

## Authoritative source map

| Concern | Authoritative source | Status |
|---|---|---|
| Product scope and release | This file | uninitialized |
| Architecture constraints | `docs/ai/architecture-policy.json` and `docs/ai/conventions.md` | initialize |
| Interface surface | project architecture profile | create or replace pointer |
| Data model and migrations | project-owned model and migration paths | initialize |
| Current work | `docs/ai/tasks/` | task-specific |
| Durable decisions | `docs/ai/decision-log.md` | initialize |
| Verified commands | `docs/ai/commands.md` | initialize |
| Material risks | `docs/ai/risks.md` | initialize |
| Technical documentation | `docs/TECHNICAL-DOCUMENTATION.md` | draft |
| User manual | `docs/USER-MANUAL.md` | draft |

## Active work and decisions

- Active task: none recorded
- Last completed milestone: none recorded
- Current architecture decision: user selection or brownfield observation pending

## Risks and unknowns

- Material risks: see `docs/ai/risks.md`
- Unknowns that block safe work: project identity, deployment, auth, data ownership, and release state are not initialized

## Last qualified evidence

- Validation state: not run
- Gate results: none
- Artifact digest: none

## Reconciliation rule

A material fact absent from this index or an authoritative source it names is unverified, not automatically false. Verify existing code, schemas, tests, tasks, and decisions before replacing or rebuilding work. Update this index when project identity, architecture, public contracts, authoritative pointers, official release, or material risks change.
