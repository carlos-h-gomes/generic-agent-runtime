# User Manual

Status: DRAFT — blocks official release until initialized and reviewed.
Documented product version: `<VERSION>`
Audience: `<AUDIENCE>`
Owner: `<OWNER>`
Last reviewed: `<DATE>`

## Product purpose and prerequisites

## Access and first use

## Navigation

## Features and expected outcomes

## Primary workflows

When this repository exposes Harness maintainer workflows, explain that governance adoption, application bootstrap, architecture migration, and deployment require separate authorization. Document how operators review adoption-plan conflicts, record stack choices, and validate an open solution decision without activating production.

Explain that managed Level 2/3 changes require a persisted, validated task contract before implementation. Destructive production requests remain unexecuted without exact approval and must include a concrete rollback procedure. Discovered skills require source and provenance review before use.

When workspace hygiene is enabled, document inventory, exact plan review, separate apply authorization, manifest verification, index-first historical retrieval, and collision-safe restore. State clearly that age alone is insufficient and archive does not authorize deletion.

## Forms, validation, and feedback

## Roles, permissions, and restrictions

## Loading, empty, failure, degraded, and recovery states

Explain `rolled_back` and `blocked_recovery` archive outcomes, where the operator finds the manifest and move journal, and that restore never overwrites a live path.

## Accessibility and supported interaction methods

## Troubleshooting and frequently asked questions

If the host does not expose trustworthy latency, token, or cost telemetry, show it as `not_verified`. Do not display an estimated zero or claim a performance or cost advantage from missing data.

## Support and escalation

## Version and release notes

Use user-facing language. Do not expose internal implementation details, secrets, private data, or operational attack surface.
