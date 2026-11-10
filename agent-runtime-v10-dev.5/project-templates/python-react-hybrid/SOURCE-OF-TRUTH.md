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

- Profile: `python-react-hybrid`
- Frontend: React with TypeScript and Vite under `frontend/`
- Backend: Python API under `backend/`; FastAPI is the default and modular Flask is compatible
- API contract: `backend/openapi.json` or the project-specific path recorded here
- Directory policy: `docs/ai/architecture-policy.json`
- Directory responsibilities: `docs/architecture/DIRECTORY-MAP.md`

## Authoritative source map

| Concern | Authoritative source | Status |
|---|---|---|
| Product scope and release | This file | uninitialized |
| Architecture constraints | `docs/ai/architecture-policy.json` and `docs/ai/conventions.md` | initialize |
| API surface | `backend/openapi.json` | create or replace pointer |
| Data model and migrations | `backend/app/models/` and project migration path | initialize |
| Current work | `docs/ai/tasks/` | task-specific |
| Durable decisions | `docs/ai/decision-log.md` | initialize |
| Verified commands | `docs/ai/commands.md` | initialize |
| Material risks | `docs/ai/risks.md` | initialize |
| Technical documentation | `docs/TECHNICAL-DOCUMENTATION.md` | draft |
| User manual | `docs/USER-MANUAL.md` | draft |

## Active work and decisions

- Active task: none recorded
- Last completed milestone: none recorded
- Current architecture decision: hybrid profile initialization pending

## Risks and unknowns

- Material risks: see `docs/ai/risks.md`
- Unknowns that block safe work: project identity, deployment, auth, data ownership, and release state are not initialized

## Last qualified evidence

- Validation state: not run
- Gate results: none
- Artifact digest: none

## Reconciliation rule

A material fact absent from this index or an authoritative source it names is unverified, not automatically false. Verify existing code, schemas, tests, tasks, and decisions before replacing or rebuilding work. Update this index when project identity, architecture, public contracts, authoritative pointers, official release, or material risks change.
