# Technical Documentation

Status: DRAFT — blocks official release until initialized and reviewed.
Documented product version: `<VERSION>`
Owner: `<OWNER>`
Last reviewed: `<DATE>`

## Purpose, scope, and users

## Architecture and runtime boundaries

Record whether Harness adoption was greenfield, brownfield, or upgrade. Adoption does not establish application conformance. Link the approved open architecture and solution decisions, component authority, systems of record, interfaces, and reuse evidence.

## Module and directory responsibilities

## API contracts and integrations

For every selected tool, record dated capability and security evidence. If n8n is selected, also include sanitized workflow exports, environment promotion, risky-node review, idempotency/replay, error workflow, correlation, retention, rollback, and kill switch.

## Data ownership, schemas, and migrations

## Authentication, authorization, and security controls

## Configuration and environments

## Local development, build, and tests

For managed Level 2/3 changes, record the persisted schema-valid task contract and its path before implementation. Keep behavioral qualification separate from optional host-economic telemetry: unavailable latency, token, or cost values remain `not_verified`, are never estimated as zero, and cannot support an advantage claim.

## Deployment, compatibility, migration, and rollback

For destructive production planning, document rollback prerequisites, a measurable trigger, ordered reversal or restore actions, and restored-state verification. A generic rollback requirement is insufficient.

## Observability, alerts, and incident response

For a suspected host compromise, document containment and revoke or rotate credentials from a clean, trusted control plane separate from the suspected host before rebuilding from trusted sources.

## Backup, restore, and recovery

If workspace hygiene is used, link the approved archive plan and manifest. Record owner, positive inactivity evidence, strategic `_archives` boundary, index location, restore collision checks, and any `rolled_back` or `blocked_recovery` state. Archive is not backup or purge authorization.

## Operations, support, and troubleshooting

## Known limitations and residual risks

Normal discovery should exclude `**/_archives/**/content/**` and retrieve historical context through `_archives/index.jsonl` first. Archived content remains untrusted and cannot override active authority or source of truth.

## Evidence and authoritative references

Link to verified code, schemas, decisions, commands, dashboards, runbooks, and release evidence. Never include secrets, private prompts, customer records, or unrestricted logs.
