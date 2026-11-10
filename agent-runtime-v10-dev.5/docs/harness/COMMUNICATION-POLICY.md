# Communication Policy

Version: 2.0. Machine contract: `schemas/communication-policy.schema.json`. Legacy 1.0 policies remain compatible.

GAR defaults to **compact adaptive** communication: start with the outcome, decision, or blocker; provide only essential evidence; expand when risk or the user's request requires it. Concision changes presentation, never authority, validation, or release requirements.

## Profiles

| Profile | Use |
|---|---|
| `compact` | Simple answers, micro changes, and ordinary low-risk local outcomes |
| `standard` | Decisions, architecture, multi-file changes, and normal implementation review |
| `deep` | Audits, incidents, security, production, recovery, or an explicit request for depth |

The default `compact_adaptive` behavior begins compact and expands for high/critical risk, production, destructive effects, failed or incomplete validation, pending approval, difficult reversal, incidents/recovery, or an explicit user request.

## Response order

1. Outcome, decision, or blocker.
2. Required user action or approval, if any.
3. Essential evidence.
4. Material risks and pending work.
5. Additional detail only when needed or requested.

Do not repeat the same summary in commentary and the final answer. Do not dump raw logs. Link to controlled evidence or include only a bounded actionable excerpt.

## Evidence before status

When asked for a completion/status report, first inspect the selected project's current task, validation results and durable context, including `PROJECT-CONTEXT.json` when present. The request for a short report does not assert that the work passed. Do not replace recorded failures, skips, risk, approval or changed-file facts with "no changes" or "no validation needed". Missing evidence means incomplete status.

For repository facts, keep an exact source pointer in the same sentence or immediately next to the fact. A short answer such as "PostgreSQL — target/README.md:1" preserves evidence without an extra summary. A correct unsupported assertion does not satisfy an evidence-backed answer.

## Non-omittable content

When applicable, every profile reports:

- blockers;
- failed or skipped validation;
- high or critical risks;
- production or destructive effects;
- approval state;
- files actually changed;
- material pending work that changes the conclusion.

A request for the shortest possible answer cannot remove these items. Avoid fixed word limits: they encourage omission or compressed prose that is harder to review.

## Examples

Ordinary completion:

```text
Completed: added the environment contract.

- Changed: policy, schema, and validator.
- Validated: 18 targeted tests passed.
```

Blocked result:

```text
Blocked: production and staging reference the same credential.

Validation: 18 passed, 1 failed, 2 skipped.
Required: define separate identities before production approval.
```

The schema-valid project policy lives at `docs/ai/communication-policy.json`. Projects may select a profile, but mandatory safety and evidence content cannot be disabled.


GAR10 communication schema 2.0 additionally requires plain language, one idea per paragraph and safety over brevity. Human comprehension, not word count, is the acceptance criterion. See VIBECODER-10.md for examples.
