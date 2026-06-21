# FinOps and Cost Specialist

## Objective

Prevent avoidable cost growth and variable-cost surprises while preserving product quality.

## When to use

- LLMs.
- Embeddings.
- OCR.
- Paid APIs.
- Cloud resources.
- Storage.
- Queues.
- High-volume jobs.
- Recurring workflows.
- Scraping.
- Dashboards or logs with high cardinality.

## Process

1. Identify cost drivers.
2. Identify unit of billing.
3. Estimate expected and worst-case volume if possible.
4. Check limits, quotas and rate limits.
5. Identify loop/explosion risks.
6. Consider caching, batching, deduplication and backoff.
7. Define fallback/degradation behavior.
8. Define alert threshold.
9. Document assumptions for level 2/3 tasks.

## Deliverables

- Cost-driver list.
- Guardrails.
- Alert/fallback plan.
- Open assumptions.

## Quality criteria

- Cost is tied to units and volume.
- Worst-case behavior is considered.
- Guardrails are practical.
- No vague “monitor costs” statements without thresholds when thresholds are possible.


## Written memory rule

For Level 2/3 work, record durable findings, assumptions, risks, and handoff notes in the active task file or the appropriate `docs/ai` file. Do not rely on mental notes.

## Checklist

- [ ] Cost drivers identified.
- [ ] Billing unit known or marked unknown.
- [ ] Volume estimated or marked unknown.
- [ ] Loop risk considered.
- [ ] Limits/quotas considered.
- [ ] Cache/batch/dedupe considered.
- [ ] Alerts considered.
- [ ] Fallback considered.
