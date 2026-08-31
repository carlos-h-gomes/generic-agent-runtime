# Reuse-first Policy

Status: normative for v8.

Before a material dependency, helper, abstraction, module, or substantial implementation, inspect:

1. matching current code and extension points;
2. platform or standard-library capability;
3. installed dependencies;
4. established project patterns;
5. the gap that remains.

Choose reuse, adapt, replace, or create. Record a `reuse-decision` for managed, disputed, dependency-adding, or cross-boundary choices; micro-edits do not require ceremony.

Apply the same discipline to governance. Reuse an authoritative task, decision, gate, or review home before creating another. Read-only reviews return conclusions inline. When persistence is authorized and formally required, use the canonical template and schema; invalid output is incomplete evidence, not a completed control.

Reuse is not automatically safer. Verify ownership, support, licensing, security, compatibility, test seams, operational behavior, and migration cost. Minimalism sizes the solution and may not delete required authorization, validation, accessibility, testing, rollback, observability, privacy, or documentation.
