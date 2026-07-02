# Decision Log

Append durable decisions here. Do not rely on chat history or mental notes.

Use this file for decisions that future agents must preserve. Do not use it as a full chat transcript.

## Entry format

```text
## YYYY-MM-DD — Decision title
Status: active / superseded / deprecated
Supersedes: optional previous decision or rule

### Context

### Decision

### Alternatives considered

### Consequences

### Risks

### Follow-ups
```

## Memory hygiene rules

- Keep `project-profile.md` focused on the current project state.
- Move durable reasons and historical tradeoffs here when they matter.
- Mark old decisions as `superseded` instead of leaving contradictory rules in multiple files.
- Delete or compact stale memory only when a newer repository source, user instruction, or decision entry clearly replaces it.
- If unsure whether old context is still valid, mark it as `Needs verification` in the appropriate doc instead of deleting it silently.

## Lessons learned (agent experience)

Capture short, reusable lessons when a task hit a non-obvious failure, a wrong assumption, a flaky validation step, or a fix that future agents should reuse. This turns one-time pain into durable guidance and reduces repeated mistakes. Keep each entry to one or two lines. Do not paste full logs.

| Date | Context | What went wrong / what worked | Reusable lesson |
|---|---|---|---|
|  |  |  |  |

## 2026-06-22 — Integrate ponytail minimalism as a core skill
Status: active
Supersedes: (none)

### Context

Evaluated the ponytail project (DietrichGebert/ponytail, MIT) — an always-on "laziest senior dev" ruleset that minimizes code via a YAGNI ladder. ponytail and this runtime occupy the same slots (`AGENTS.md`, `.agents/skills`, per-tool adapter files) but act on different axes: the runtime governs how much process/safety to apply; ponytail governs how large the solution is. Goal: gain the minimalism discipline without a second competing always-on ruleset or a colliding `AGENTS.md`.

### Decision

Absorb ponytail's ladder as a native core skill (`core/minimalism`) and wire it as a lightweight lens into triage (scope check), implementation (the ladder), and code-quality-testing (delete-list review). Register it in the core skills list and default principles. Keep the runtime as the single source of truth. The ladder is reimplemented in the runtime's own wording; no upstream files or prose were copied.

### Alternatives considered

- Vendor ponytail's `skills/` + adapters subordinate to the runtime: more tooling (`/ponytail-review`, hooks, MCP, benchmarks) but two rulesets to keep aligned and an `AGENTS.md` to reconcile. Rejected as heavier than needed.
- Install ponytail as a separate per-agent plugin: zero maintenance and free upstream updates, but not governed by or portable with the runtime, and two always-on rulesets whose priority is unmanaged. Kept as an optional way to trial upstream tooling, not as the integration.

### Consequences

- New core skill plus light additive wiring across `AGENTS.md`, `CLAUDE.md`, `constitution.md`, `README.md`, `CHANGELOG.md`. Version bumped 3.5 → 3.6 (15 skills).
- Minimalism is explicitly scoped to solution code; it cannot be used to skip gates, task files, written memory, or approval boundaries.

### Risks

- An agent could misread "laziest dev, skip it" as license to skip a runtime control. Mitigated by the explicit scope boundary in the skill and the preservation rule in `AGENTS.md`.

### Follow-ups

- Optional: vendor the `/ponytail-review`/`-audit` commands or the ponytail MCP later if a delete-list command proves useful in practice.
- Attribution: ponytail is MIT; credit kept in the skill body and here. Add a NOTICE/LICENSE only if upstream text is later copied verbatim.

## 2026-06-22 — Adopt rtk at the tooling layer
Status: active
Supersedes: (none)

### Context

Evaluated rtk (rtk-ai/rtk, Apache-2.0) alongside caveman (MIT) as token optimizers to pair with ponytail / `core/minimalism`. The three act on different axes: minimalism cuts code written, caveman cuts the agent's prose, rtk cuts tool-output tokens entering context. The runtime is command-centric (`./scripts/*.sh`, git, tests), so rtk is the highest-leverage, lowest-risk add: a deterministic Rust CLI proxy, no LLM, not a competing always-on instruction ruleset.

### Decision

Adopt rtk at the tooling layer as an optional, recommended wrapper for validation/git/test commands. Do not vendor it; document the pattern and a hard rule: never base a pass or a fix on filtered/truncated output — diagnose from rtk's tee'd full output on failure. Install is external and per-machine (`brew`/`cargo` + `rtk init -g`). caveman was deferred (see alternatives).

### Alternatives considered

- caveman (output-style compression): real but smaller surface here — the runtime's structured artifacts (task spec, reports, decision log) must never be compressed, so caveman would add a second always-on style ruleset for a small conversational gain. Deferred to optional ad-hoc use of `/caveman`, `/caveman-commit`; explicitly do not run `caveman-compress` on `AGENTS.md`/`CLAUDE.md`.
- Vendoring rtk into the runtime: unnecessary — it is an external binary at the tooling layer, not a skill.

### Consequences

- Doc-layer additions only (`AGENTS.md` §13, `CLAUDE.md` behavior, `core/validation`, `code-quality-testing`, `commands.md` template). Version bumped 3.6 → 3.7.
- rtk stays optional with graceful degradation; the runtime does not depend on it.

### Risks

- Bash-hook-only auto-rewrite: Claude Code built-in Read/Grep/Glob bypass it; use shell or explicit `rtk` for those.
- Reflection loop could fix against a truncated test view — mitigated by the "diagnose from tee'd output" rule.
- tee'd full output may contain secrets/sensitive data — treat those files as sensitive; do not commit or forward them.
- Telemetry exists but is opt-in/off-by-default with an env override; keep it disabled to match the self-host/privacy stance.
- Apache-2.0 (not MIT): permissive; only relevant if rtk source is ever vendored, which this decision avoids.

### Follow-ups

- Optional: add `rtk gain`/`discover` to a periodic cost review if rtk is adopted across projects.
- Revisit caveman only if sessions become conversation-heavy and artifact-light.

## 2026-07-02 — Release checklist as a first-class artifact (v3.8)
Status: active
Supersedes: (none)

### Context

Launch/deploy readiness knowledge lived in chat and in each engineer's head. A user-provided 8-section production-readiness draft (deployment, auth, secrets, database, payments, observability, cost, incidents) was evaluated for adoption.

### Decision

Adopt the draft as `docs/ai/release-checklist.md`, restructured: Part A (launch readiness — run once, re-audit on major change or quarterly) vs Part B (per-release, <10 min); [B]locker/[R]ecommended tiering; conditional sections; N/A handling per §16; blockers require recorded verification evidence. Ownership assigned to the Observability/Release gate. Added sections missing from the draft for this stack: external integrations/inbound webhooks, privacy/LGPD, AI/LLM & agents; supply-chain items under Secrets. De-branded vendor-specific wording. Version bumped 3.7 → 3.8.

### Alternatives considered

- New specialist skill `launch-readiness`: rejected — duplicates the Observability/Release gate and contradicts the consolidation philosophy (§15).
- Keep as external doc outside `docs/ai`: rejected — violates the written-memory rule and would not be discovered by agents.
- Single flat checklist per release: rejected — mixes prove-once items with per-deploy items, causing checklist rot.

### Consequences

- New memory file plus light wiring in `AGENTS.md` (§1, §11, §17), `CLAUDE.md`, `specialists/observability-release`, `docs/ai/quality-gates.md`.
- Level 3 completion checklist now includes release-checklist status for production launches/deploys.

### Risks

- Checklist theater if items are ticked without evidence — mitigated by the verification-evidence rule for blockers.
- Rot if Part A is never re-audited — mitigated by explicit re-audit triggers.

### Follow-ups

- Optional `./scripts/release-check.sh` to automate mechanical Part B items.
- Consider per-project overrides (e.g. dropping the payments section permanently in projects that will never bill).

## 2026-07-02 — Agent bridge: file-based multi-agent coordination protocol (v3.9)
Status: active
Supersedes: (none — makes AGENTS.md §4 concrete)

### Context

AGENTS.md §4 required cross-tool coordination "through text files" but defined no protocol: no fixed file, no schema, no read budget. In practice each agent re-read broad context, and handoffs between Claude Code, Codex and local models were prose-heavy and token-expensive.

### Decision

Adopt an event-log + materialized-view pattern: `docs/ai/bridge/ledger.jsonl` (append-only JSONL events, short keys, notes ≤140 chars, pointers not payloads) plus `docs/ai/bridge/board.md` (one-page overwritten current-state snapshot). Mechanics via `scripts/bridge.sh` (board/tail/log/claims/compact — pure bash, python3 optional). Fixed session boot: board + tail 15 + claims + only the relevant task file (~≤600 tokens). File claims are ledger events; `done`/`release` frees them. Compaction past 200 lines into `ledger-archive.jsonl`. New core skill `core/agent-bridge`; restricted lane for local/small models via `prompt-templates/04-bridge-worker.txt` (Level 0/1 execution only). Version bumped 3.8 → 3.9. The distribution zip now extracts at repository root (no nested folder).

### Alternatives considered

- Git-only coordination (branches + commit messages): authoritative for code but invisible to uncommitted/in-flight work and unreadable cheaply mid-task. Kept as the code layer, not the coordination layer.
- One markdown "conversation" file agents append prose to: token growth is unbounded and unparseable; exactly the failure mode to avoid. Rejected.
- MCP/socket-based live coordination: not portable across Codex/local models, adds infrastructure. Rejected; files are the lowest common denominator.
- Lockfiles per path (`.lock` files): litter the tree and leak into commits. Claims-in-ledger keep coordination data in one place. Rejected.

### Consequences

- New skill (16 core+specialist skills), new script, new `docs/ai/bridge/` memory surface, template for local models; §4 now has teeth.
- Reads stay flat as history grows (tail + compaction); writes cost ~50–80 tokens/event.

### Risks

- Stale claims from crashed sessions block others — mitigation: claims are advisory + humans/planners may log `release` on behalf of a dead session, with a note.
- Agents pasting payloads despite the cap — mitigated by the 140-char hard cap in `bridge.sh` and the pointer rule in the skill.
- Board drift vs ledger — board declares the ledger authoritative for claims; `claims` recomputes from events.

### Follow-ups

- Optional: `bridge.sh stale` to flag claims older than N hours.
- Optional: git hook appending a `note` event per commit for human commits.
