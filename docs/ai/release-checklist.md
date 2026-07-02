# Release Checklist

Owned by the Observability/Release gate (`specialists/observability-release`). Use for anything that ships to production.

## How to use

This file has two parts:

- **Part A — Launch readiness.** Run once before the first production launch of a system, then re-audit on major changes (new auth model, new payment flow, new data store, new AI agent) or at least quarterly. Most items are "prove it once" items.
- **Part B — Per-release.** Run on every production deploy. Small on purpose; if it takes more than a few minutes, it will be skipped.

Rules:

- Items are tiered: **[B] Blocker** — do not launch/deploy until true. **[R] Recommended** — may be deferred with a written reason and an owner.
- Sections marked *(conditional)* apply only when the trigger exists (e.g. no payments → skip section 5). Skipping a conditional section is not an N/A entry; skipping an applicable item is, per the preservation rule in `AGENTS.md` §16: `Not applicable — reason: ...`.
- For [B] items, record **how it was verified** (command, screenshot, date of test), not just a checkmark. "Tested" without evidence is a mental note, and mental notes are banned (§1).
- Copy the relevant part into the active task file (`docs/ai/tasks/`) for Level 3 launches, or reference this file and record only deviations.

---

## Part A — Launch readiness

### 1. Deployment and environments

- [ ] [B] Deploy is repeatable — anyone on the team can ship the same build twice and get the same result.
- [ ] [B] Production is separate from development — different database, different credentials, different environment config.
- [ ] [B] Deploys are tied to version control (commit or tag), never copy-pasted from a chat or editor.
- [ ] [B] Rollback path actually works — it has been executed at least once, on purpose.
- [ ] [R] Staging or preview environment exists where things can break without hurting users.
- [ ] [R] A deploy takes under 10 minutes end-to-end.
- [ ] [R] DNS, TLS certificates and domain renewal are automated or calendared (expired cert = outage).

### 2. Auth and authorization *(conditional: system has users/accounts)*

- [ ] [B] Auth is enforced server-side, not only in the UI.
- [ ] [B] Tested as a second user — logged in as a different account and tried to access the first user's data.
- [ ] [B] Tenant/row-level isolation is on and verified where multi-tenant data exists (e.g. Postgres RLS, tenant_id scoping in every query).
- [ ] [B] Admin routes and internal tools are protected server-side.
- [ ] [B] Rate limiting exists on login, signup and password reset.
- [ ] [R] Password reset, email verification and session expiry work on the unhappy path too (expired token, reused token, wrong account).
- [ ] [R] Sessions/tokens can be revoked (leaked token has a kill path).

### 3. Secrets and supply chain

- [ ] [B] All credentials live in environment variables or a secret manager — none in code.
- [ ] [B] No keys in the frontend bundle — the built JS was inspected to confirm.
- [ ] [B] No secrets in repository history, including old commits (scan, don't assume).
- [ ] [B] Different keys per environment — production keys are not dev copies.
- [ ] [B] Key rotation plan — a leaked key can be invalidated in under an hour, and the steps are written down.
- [ ] [R] Dependency lockfiles are committed and installs are reproducible.
- [ ] [R] Dependency audit (SCA) run at least once before launch; no known-critical vulnerabilities shipped knowingly.

### 4. Database and data

- [ ] [B] Backups exist — automatic, daily at minimum.
- [ ] [B] Backup restore has been tested — a backup never restored is not a backup.
- [ ] [B] Schema changes are tracked as migrations, not manual UI edits.
- [ ] [B] Destructive operations are gated behind confirmation or admin auth.
- [ ] [R] Indexes exist on the top 2–3 queries.
- [ ] [R] PII / sensitive fields are encrypted at rest or the platform-level encryption is confirmed.
- [ ] [R] Data retention is defined: what is kept, for how long, and what gets purged.

### 5. Payments and money flows *(conditional: system charges money)*

- [ ] [B] Payment webhooks are verified with the signing secret (e.g. Stripe, Mercado Pago, Pagar.me).
- [ ] [B] Webhook handler is idempotent — retries do not charge twice.
- [ ] [B] Failure paths are logged and retried, not silently swallowed.
- [ ] [B] Checkout tested end-to-end in production with a real card.
- [ ] [R] Refund flow exists with an audit trail.
- [ ] [R] Subscription lifecycle events are handled: trial end, card declined, cancellation, plan change.

### 6. External integrations and inbound/outbound webhooks *(conditional: system talks to third parties)*

- [ ] [B] Inbound webhooks are authenticated (signature, token or allow-list) — a public unauthenticated webhook is an open write endpoint.
- [ ] [B] Outbound calls have timeouts and bounded retries with backoff — a hung third party must not hang the system.
- [ ] [B] Idempotency handled on both directions where the provider retries (e.g. Meta/WABA delivery callbacks, n8n reprocessing).
- [ ] [R] Third-party rate limits and quotas are known and respected (documented in `docs/ai/risks.md` or the integration doc).
- [ ] [R] Sandbox/test credentials are fully separated from production credentials.
- [ ] [R] Contract examples (real payloads) are stored in project memory for the next agent/human.

### 7. Observability and incident response

- [ ] [B] Logs are centralized and searchable — not a `console.log` hiding in a dashboard tab.
- [ ] [B] At least one alert pages a human when production is down (external uptime check counts).
- [ ] [B] User-facing error messages do not leak stack traces, internal paths or secrets.
- [ ] [B] Someone is on-call, even if that someone is you — and they know it.
- [ ] [B] A "production is on fire" runbook exists — single page, ordered steps, tested for staleness.
- [ ] [B] A rollback command or button exists and takes under 5 minutes.
- [ ] [R] Errors are grouped and searchable (Sentry, Glitchtip, Axiom, Datadog or equivalent).
- [ ] [R] At least one latency or error-rate metric exists.
- [ ] [R] A channel to tell users what is happening exists (status page, WhatsApp broadcast, Discord, X).
- [ ] [R] Post-incident review happens after any user-facing outage; the duration of the last outage is known.

### 8. Cost and scaling

- [ ] [B] Unbounded loops are capped: AI agents, background jobs, workflow retries, cron. Every loop has a max attempts or max spend.
- [ ] [B] Hard caps or budget alerts are set at every pay-per-use provider (LLM tokens, cloud egress, workflow executions, SMS/WhatsApp conversation fees).
- [ ] [R] Monthly production bill can be estimated within 30%.
- [ ] [R] Cost per active user is roughly known.
- [ ] [R] A 10x traffic spike has a plausible answer (even if the answer is "queue and degrade").

### 9. Privacy and compliance *(conditional: system handles personal data — in Brazil, assume LGPD applies)*

- [ ] [B] Personal data collected is mapped: what, why, where it is stored, and who it is shared with.
- [ ] [B] Personal data is minimized in logs and analytics — no CPF, phone or message content in plain logs.
- [ ] [B] Third-party transfers of personal data are identified (LLM providers included — sending customer chats to a model API is a transfer).
- [ ] [R] A user deletion/export path exists, even if manual, with a documented procedure.
- [ ] [R] Privacy notice exists and matches reality; a contact for data subject requests is defined.

### 10. AI/LLM and agents *(conditional: system calls a model or runs agents)*

- [ ] [B] External content (user messages, retrieved docs, tool output) is treated as untrusted — prompt injection reviewed per the OWASP ASI Top 10 mapping in `specialists/risk-security-compliance`.
- [ ] [B] Model output used by other systems is validated/parsed defensively, never executed or trusted blindly.
- [ ] [B] Tools available to agents are least-privilege; state-mutating actions have human-in-the-loop or explicit policy.
- [ ] [B] Spend caps per request/user/day exist, plus a kill switch to disable the AI path without taking down the product.
- [ ] [R] Fallback/degradation defined when the model provider is down or rate-limited.
- [ ] [R] A minimal eval or smoke-prompt set exists to catch regressions after prompt/model changes.

---

## Part B — Per-release checklist

Run on every production deploy. Target: under 10 minutes.

- [ ] [B] Release is a specific commit/tag; changelog or release note updated.
- [ ] [B] `./scripts/validate.sh` (or the project's validation subset) passed on this exact revision.
- [ ] [B] Migrations in this release reviewed: reversible, or a restore point/backup was taken immediately before.
- [ ] [B] Config/secret changes for this release applied to the target environment before deploy.
- [ ] [B] Rollback command for this specific release identified *before* deploying.
- [ ] [B] Post-deploy smoke test of the key user journey executed in production.
- [ ] [R] Deployed to staging first and smoke-tested there.
- [ ] [R] Feature flags for new behavior default to safe/off.
- [ ] [R] Monitoring window defined: who watches, which signals, for how long.
- [ ] [R] Users/stakeholders notified when the change is customer-visible.

### Sign-off

```text
Release: <tag/commit>
Date: YYYY-MM-DD
Deployed by:
Approved by (Level 3): 
N/A items and reasons:
Deferred [R] items, reason and owner:
Residual risks:
```
