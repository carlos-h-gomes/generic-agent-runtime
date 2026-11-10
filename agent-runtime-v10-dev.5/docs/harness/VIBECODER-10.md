# GAR 10 development candidate

This successor is local and unqualified. GAR 9 archives remain frozen. No production safety, host enforcement, behavioral success or measured token savings is claimed.

## Delivery workflow

1. Read ancestor AGENTS instructions, project docs/ai and the triggered skills. Establish user/job/critical journey and acceptance criteria.
2. Review a delivery policy with the artifact SHA-256 and disposition of every VC-01..VC-15 control from the maintainer roadmap. Every applicable control needs named automated/manual checks; inapplicability needs a reviewed rationale.
3. Produce fresh evidence bound to that artifact. Keep sanitized proofs inside the project; record path, SHA-256, observation and expiry. Missing manual accessibility, recovery, security or other applicable proof remains incomplete.
4. Run `scripts/delivery_check.py` with an independently reviewed policy digest. Exit 0 means evidence structure is complete, 1 failed check, 2 invalid/stale/drifted inputs, 3 incomplete. It does not establish evidence authenticity or application safety. Trust the reviewer and tools through independent controls.
5. Promotion still uses the existing environment/promotion contracts and separate exact user authorization. `operation_check` is only a pure record comparison, never a live interceptor.

`context_plan.py` inventories explicitly selected files with hashes and a byte budget. Mandatory context is retained even over budget; reconcile the budget before proceeding. The caller must discover ancestor instructions and applicable skills. Byte/4 is an approximate token estimate, not measured usage.

`vibecoder_tools.py --root PROJECT component --record RECORD --expected-record-sha256 DIGEST` checks a component review record. `operation --action ACTION --approval APPROVAL` compares exact scope but stays incomplete without verified host interception. `report --profile PROFILE --report REPORT --expected-report-sha256 DIGEST` inspects a supported report and stays incomplete until tool identity, scan scope and successful execution are independently qualified. These commands read bounded local files only; they never install or execute tools.

## Clear communication

Start with the result in the user's language. Explain only material behavior, actual verification, unresolved risk and the next necessary action. Prefer familiar words, one idea per paragraph and progressive detail. Do not omit a safety blocker to meet a word target. Avoid repeated status, raw logs and unnecessary technical terminology. Ask one material decision at a time. Human comprehension must be evaluated; short text alone is not clarity.

Portuguese example: “A alteração está pronta no ambiente local. O fluxo principal passou nos testes. Ainda falta verificar o acesso entre usuários; a publicação continua bloqueada.”

## External tools and credits

Playwright (Microsoft, Apache-2.0), axe-core (Deque, MPL-2.0), OSV-Scanner (Google, Apache-2.0) and Gitleaks (MIT, project contributors) are research candidates, not bundled dependencies or qualified tools. Public-source review does not qualify a binary. Require immutable artifact and integrity/provenance, license/NOTICE, dependency/advisory review, bounded permissions/network/telemetry and an expiry before execution. Skills likewise require file-by-file review; a README or popularity is not admission.

Do not enable experimental page-defined agent tools, automatic fix commands, broad hooks or telemetry by default. Mocked reports prove parser behavior only. Actual scanner/browser execution, keyboard/visual review, behavioral comparative tests and human comprehension remain independent gates.

## Migration and rollback

This is an additive candidate based on GAR 9; new controls must be opt-in while qualification is pending. Do not install over user files. Preserve project-owned policy, configure controls in a reviewed task, and bind proofs to the actual delivery. Roll back by restoring the preserved GAR 9 installation and reviewing contract compatibility; do not reuse GAR 10 evidence as GAR 9 proof.

## Failure-class coverage catalog

| Failure class | Required evidence | Release consequence |
|---|---|---|
| VC-01 misunderstood requirements | User/job/primary journey; observable acceptance criteria; unresolved material decisions identified; prototype where useful | Missing material decision blocks affected implementation |
| VC-02 attractive but broken workflow | End-to-end success/failure tests with assertions over actual persisted effects, not just visible buttons | Failed critical journey blocks release |
| VC-03 client-only auth or cross-user access | Server/resource ownership tests using at least two synthetic identities/tenants and alternate access routes | Unauthorized access blocks release |
| VC-04 secrets exposed in repo/client/logs | Redacted secret scan, server/client boundary review, scoped configuration inventory | Confirmed secret exposure blocks release and triggers scoped incident guidance |
| VC-05 unsafe input/injection/SSRF/upload | Applicable trust-boundary tests, payload limits, parser/egress rules and inert negative fixtures | High/critical failure blocks release |
| VC-06 unsafe data/migration | Constraints, transaction/error behavior, migration rehearsal, rollback/restore proof; data purpose/retention and access review | Destructive uncertainty or unverified recovery blocks promotion |
| VC-07 duplicate payments/events or retry corruption | Idempotency, signed webhook validation where applicable, replay and partial-failure tests with mocks | Failed business invariants block release |
| VC-08 fragile architecture and dependencies | Reuse inventory, module contracts, thin entrypoints, supported runtime evidence, lockfile/SBOM/advisory review | Unsupported or applicable high/critical vulnerability blocks release under existing authority rules |
| VC-09 incomplete UX/accessibility | Loading/empty/success/error/permission/disabled/recovery/offline/content-stress matrix; compact/wide visuals; automated plus keyboard/manual accessibility | Missing applicable visual/manual evidence blocks UI release |
| VC-10 rate/cost/reliability runaway | Input/volume/time limits, retry budgets, alerts/owner, timeout/degradation tests, cost cap and stop mechanism | Missing critical bounds blocks relevant release |
| VC-11 direct production or configuration drift | Same artifact/configuration/migration bound to staging, exact approval, monitoring and credible recovery | Absent/stale/drifted evidence blocks promotion |
| VC-12 agent injection or unauthorized tool action | Untrusted content fixtures; explicit tool permissions; operation interception tests where supported; no inherited secrets | Forbidden action or unsupported enforcement claim blocks qualification |
| VC-13 false completion | Criterion-to-evidence mapping; actual command exits; explicit skip/incomplete status; independent fixture expectations | Missing required verification stays blocked |
| VC-14 verbose or confusing handoff | Result-first Portuguese/plain-language outputs, decision/next-step comprehension rubric, no duplicated status or raw logs | Safety omission blocks; clarity failure requires revision |
| VC-15 lost/poisoned context | Evidence source/revision/expiry, minimal verified handoff, conflicts reconciled and old claims not reused as current proof | Unknown or contradictory facts remain unverified |
