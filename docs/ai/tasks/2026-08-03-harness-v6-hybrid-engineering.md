# Harness v6 hybrid engineering

Status: implementation authorized on 2026-08-03.

Machine contract: `2026-08-03-harness-v6-hybrid-engineering.task.json`.

## Accepted decisions

- Derive a new immutable-successor candidate `agent-runtime-v6.0`; never patch v5.0.
- Generated application projects use a Python API backend and React frontend with strict runtime and responsibility boundaries.
- FastAPI plus React, TypeScript, and Vite is the default generation profile; Flask is compatible when Blueprints and the same layers are preserved.
- `main.py`, `server.py`, `App.jsx`, and `App.tsx` may exist only as thin composition roots.
- Minimum directories are required; additional directories remain allowed when their responsibility and dependency direction are explicit.
- The project template is packaged under a dedicated template root and applied by a collision-safe plan/apply bootstrap, never extracted blindly over a repository.
- `SOURCE-OF-TRUTH.md` is the authoritative index of project facts and detailed sources, below platform/user/AGENTS authority and without replacing tasks or evidence.
- Technical documentation and the user manual evolve on material impact and block official release when incomplete.

## Release boundary

The work is local and reversible. It does not authorize downstream project mutation, network dependency installation, deployment, production access, credentials, external messages, commits, or pushes.

## Validation boundary

Static Harness and synthetic fixture code may run after inspection. No real downstream project code or external adversarial traffic is authorized.

## Handoff

- Baseline ZIP SHA-256: `A2DF0C4DC057DD166E5F530BA76280796F03D3AF63F4FC8F340281BE5C5406FF`.
- Current state: contract recorded; design and implementation pending.
- Next action: record the architecture decision and design-phase gate results.
