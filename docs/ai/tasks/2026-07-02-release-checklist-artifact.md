# Task — Release checklist as a first-class runtime artifact

Date: 2026-07-02
Level: 2
Status: done

## User request

Structure runtime v3.8 and add a per-launch checklist, starting from a user-provided 8-section production-readiness draft (deployment, auth, secrets, database, payments, observability, cost, incident response) to be evaluated and improved.

## Intent

Make launch/deploy readiness a governed, written artifact owned by the Observability/Release gate instead of ad-hoc chat knowledge.

## Acceptance criteria

- A single checklist file exists in project memory, split into launch readiness (once + re-audit) and per-release (every deploy).
- Items are tiered Blocker/Recommended; conditional sections skip cleanly; N/A follows the §16 preservation rule.
- Stack-agnostic wording (brands only as examples).
- Gaps covered for this stack: privacy/LGPD, AI/LLM & agents, external integrations/inbound webhooks, supply chain.
- Wired into AGENTS.md (§1, §11, §17), CLAUDE.md, `specialists/observability-release`, `docs/ai/quality-gates.md`. Version bumped to 3.8.

## Structured task specification

```json
{
  "triage_status": "ready_for_implementation",
  "intent": "Add governed release checklist artifact",
  "task_level": "2",
  "description": "Create docs/ai/release-checklist.md (Part A launch readiness, Part B per-release) and wire it into the Observability/Release gate.",
  "acceptance_criteria": ["see above"],
  "affected_files": {
    "owned": [
      "docs/ai/release-checklist.md",
      "AGENTS.md",
      "CLAUDE.md",
      ".agents/skills/specialists/observability-release/SKILL.md",
      "docs/ai/quality-gates.md",
      "docs/ai/decision-log.md"
    ],
    "shared": [],
    "do_not_touch": ["scripts/", "prompt-templates/", "other skills"],
    "discovery_needed": []
  },
  "scope": {
    "in_scope": ["checklist artifact", "gate wiring", "version bump 3.7 -> 3.8"],
    "out_of_scope": ["automation of checklist verification", "CI enforcement", "new scripts"]
  },
  "gates_triggered": ["observability-release", "documentation"],
  "skills_to_load": ["core/documentation", "specialists/observability-release"],
  "context_packet_required": true,
  "task_file_required": true,
  "human_approval_required": { "required": false, "reason": "docs-only, reversible, no production impact" },
  "validation_plan": {
    "commands": [],
    "manual_checks": ["all cross-references resolve", "version strings consistent", "markdown renders"],
    "quality_loop_max_attempts": 3
  },
  "missing_information": [],
  "routing_decision": "implement"
}
```

## Gates triggered

- [x] Observability/Release — triggered: the artifact belongs to this gate.
- [x] Code Quality/Testing — not applicable — reason: no executable code changed.
- [x] UX/Product — not applicable — reason: no user-facing product surface.
- [x] Security/Compliance — partially: checklist content encodes security/privacy controls; no runtime security behavior changed.
- [x] Data/Integration — not applicable — reason: docs only.
- [x] FinOps — not applicable — reason: docs only.
- [x] AI/LLM — not applicable — reason: docs only; ASI Top 10 referenced, not modified.
- [x] Architecture/UML — not applicable — reason: no module/data/deployment change.

## Key evaluation decisions on the source draft

1. Split into Part A (launch readiness, prove-once + re-audit) and Part B (per-release, <10 min) — mixing both makes per-release checklists rot.
2. Tiering [B]/[R] plus conditional sections; N/A per §16.
3. De-branded (Supabase/Stripe/Bubble/Replit → generic with brand examples).
4. Added sections 6 (external integrations/inbound webhooks), 9 (privacy/LGPD), 10 (AI/LLM & agents); added supply-chain items to Secrets and DNS/TLS to Deployment.
5. Blockers require recorded evidence of verification, aligning with the written-memory rule §1.

## Validation

### Commands run

None — repository has no doc-lint tooling; `./scripts/*.sh` target product code, not runtime docs.

### Manual checks

- Cross-references (`AGENTS.md` §11/§16/§17, skill, quality-gates) verified after edits.
- Version strings updated in AGENTS.md and CLAUDE.md.

### Not validated

- No automated markdown lint (not present in repo).

## Risks and pending items

- Checklist can rot if never re-audited; Part A prescribes re-audit triggers (major change / quarterly).
- Optional follow-up: a `./scripts/release-check.sh` that automates the mechanical Part B items (tag present, validate.sh green, migration reversibility flag).

## Final handoff

v3.8 ships the release checklist as project memory. Next agent: when a task is a production launch/deploy, load `specialists/observability-release` and apply Part A/B per the gate.
