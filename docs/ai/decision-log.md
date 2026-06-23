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
