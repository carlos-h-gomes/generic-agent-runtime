# Python API backend

This boundary exposes the application's HTTP API and owns authoritative business rules, authorization at the resource boundary, persistence orchestration, and server-side integrations.

Dependency direction: `controllers -> services -> models/repositories`. Request and response DTOs live in `schemas`. `app/main.py` is a thin composition root and must not contain route implementations, database access, or business rules.
