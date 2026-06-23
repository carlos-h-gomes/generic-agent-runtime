# 2026-06-22 — rtk tooling-layer integration

Status: done

## Structured task specification

```json
{
  "triage_status": "ready_for_implementation",
  "intent": "Adopt rtk as an optional, recommended output-compressing proxy for validation/git/test commands at the runtime's tooling layer.",
  "task_level": "2",
  "description": "Document rtk (rtk-ai/rtk, Apache-2.0) as a tooling-layer optimizer in the runtime: validation policy, entry-point behavior, reflection-loop diagnosis rule, and an optional commands.md slot. Do not vendor; keep it optional with graceful degradation.",
  "acceptance_criteria": [
    "AGENTS.md validation policy notes rtk as an optional wrapper with fallback to plain commands.",
    "core/validation and code-quality-testing forbid concluding a pass or fixing code from filtered/truncated output; require diagnosing from the tee'd full output on failure.",
    "commands.md template has an optional RTK-aware validation slot.",
    "decision-log records the decision plus security/privacy notes.",
    "CHANGELOG 3.7 added and version strings consistent; nothing removed."
  ],
  "affected_files": {
    "owned": [
      "AGENTS.md",
      "CLAUDE.md",
      "README.md",
      "CHANGELOG.md",
      "docs/ai/commands.md",
      "docs/ai/decision-log.md",
      ".agents/skills/core/validation/SKILL.md",
      ".agents/skills/specialists/code-quality-testing/SKILL.md",
      "docs/ai/tasks/2026-06-22-rtk-tooling-integration.md"
    ],
    "shared": [],
    "do_not_touch": [".agents/skills/core/minimalism/SKILL.md"],
    "discovery_needed": []
  },
  "scope": {
    "in_scope": ["Doc/convention changes that make rtk a recommended optional tool."],
    "out_of_scope": [
      "Installing or running rtk (external, per-machine, user's responsibility).",
      "Vendoring rtk source.",
      "Integrating caveman (deferred)."
    ]
  },
  "gates_triggered": ["data_integration", "security_compliance", "finops"],
  "human_approval_required": {
    "required": false,
    "reason": "Edits are to the runtime's own markdown docs; rtk install/run is external and not performed here."
  },
  "validation_plan": {
    "commands": ["./scripts/validate.sh", "./scripts/lint.sh", "./scripts/test.sh"],
    "manual_checks": [
      "Version strings consistent at 3.7 across AGENTS.md/CLAUDE.md/README.md.",
      "rtk references resolve and read as optional with graceful degradation.",
      "No gate/approval/written-memory rule removed."
    ],
    "quality_loop_max_attempts": 3
  }
}
```

## Gate review

- **Data/Integration** — rtk is an external tooling integration. Here it is read-only documentation/convention; the actual command interception happens on the user's machine via rtk's own hook. No schema/contract/webhook change in the runtime.
- **Security/Compliance** — surfaced in the decision-log: Bash-hook-only scope, telemetry opt-in/off-by-default, tee files may contain secrets (treat as sensitive, do not commit/forward).
- **FinOps** — the purpose is variable-cost (token) reduction on common dev commands; no new spend introduced.
- **Architecture/UML** — Not applicable: no module boundary, data model, or deployment change.
- **UX/Product** — Not applicable: no user-facing surface.
- **Observability/Release** — Not applicable: no production/runtime change in this repo.

## Validation

- `./scripts/validate.sh`, `./scripts/lint.sh`, `./scripts/test.sh`: exit 0 (no-op — governance/docs repo, no app code).
- Structural: version strings = 3.7 across the three files; rtk references resolve; the "diagnose from tee'd output" rule present in both `core/validation` and `code-quality-testing`; no gate/approval/written-memory rule removed (preservation rule respected).

## Handoff notes

- rtk is optional. Nothing in the runtime depends on it; plain commands remain the fallback path.
- The one behavioral rule that matters: under any output-compressing proxy, never report a pass or fix code from the filtered/truncated view — use the tee'd full output on failure.
- caveman remains deferred (optional ad-hoc `/caveman` commands only; never `caveman-compress` on `AGENTS.md`/`CLAUDE.md`). Revisit only if sessions become conversation-heavy and artifact-light.
- Install reference for the user (external): `brew install rtk` or `cargo install --git https://github.com/rtk-ai/rtk`, then `rtk init -g`; keep telemetry disabled.
