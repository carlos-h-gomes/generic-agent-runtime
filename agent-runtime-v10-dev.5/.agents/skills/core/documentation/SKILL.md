---
name: documentation
description: "Use when a completed change creates durable architecture, contract, operating, migration, or user knowledge that maintainers need."
---

# Documentation

Own durable project and user documentation. `core/context-memory` owns active task continuity.

## Write only durable value

Document a fact when its absence could cause misuse, unsafe changes, repeated investigation, or operational failure. Typical triggers:

- a public/internal contract, schema, integration, business rule, or migration changed;
- architecture or a rejected alternative matters later;
- a new security, privacy, cost, or operational risk exists;
- build, release, rollback, recovery, or support behavior changed;
- users or maintainers need migration or usage instructions.

Every task declares documentation impact: `none`, `technical`, `user_manual`, or `both`. `none` needs a concrete no-impact reason. Update `docs/TECHNICAL-DOCUMENTATION.md` for material architecture, API, data, configuration, security, deployment, operations, recovery, migration, or support changes. Update `docs/USER-MANUAL.md` for user-visible features, flows, navigation, permissions, feedback, accessibility, errors, recovery, or support changes.

These two files are canonical entrypoints and may link to focused subdocuments. Before an official release, verify their product version, review date, ownership, coverage, link integrity, absence of placeholders, and consistency with the truth index and released behavior. Micro changes may batch documentation until the next material milestone; do not let a release batch cross the release gate.

Prefer the existing authoritative document. Create the smallest new file only when no current home fits. Link to code and task evidence; do not paste discoverable file trees, generated output, or temporary debugging notes.

## Quality rules

- State current behavior first and date/version changing claims.
- Separate verified fact, decision, assumption, and future work.
- Record supersession instead of silently erasing important history.
- Use synthetic examples and redacted evidence.
- Never store secrets, personal/customer data, private prompts, chain-of-thought, or full logs.
- Keep commands in `commands.md` only after they actually run or are verified from an authoritative project source.

Documentation writes require task authorization. A request to answer, inspect, diagnose, review, or assess production readiness does not authorize durable documentation or governance initialization; return the result inline unless persistence was separately authorized or an existing governed workflow explicitly requires an update. Reuse an authoritative document before creating a new one. When a formal artifact is required, use its canonical template and validate it against the canonical schema before treating it as evidence. Finish by checking links, paths, version numbers, and consistency with the task contract, schemas, and actual implementation.
