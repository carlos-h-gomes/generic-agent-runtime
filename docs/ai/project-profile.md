# Project Profile

Status: template. Fill during Project Profiling. Keep concise enough to load every session.

## Project summary

- Name:
- Product / domain:
- Primary users:
- Business goal:
- Current maturity: prototype / internal / production / critical production
- Current owner(s):

## Stack

- Frontend:
- Backend:
- Database:
- Infra/runtime:
- Auth:
- Background jobs / queues:
- External integrations:
- AI/LLM usage:
- Observability:

## Architecture map

Use text, Mermaid, PlantUML, or concise bullets. Prefer only the views that matter.

### C4 / system context

```text
External users/systems → application boundaries → external dependencies
```

### Containers / modules

```text
Main modules, services, jobs, workers, routes, integrations
```

### Critical data flows

```text
Input → validation → business logic → persistence/integration → output
```

## Important paths

```text
src/
app/
server/
docs/
scripts/
```

## Environment assumptions

- Local dev:
- Test:
- Staging:
- Production:
- Secrets/config location:

## Durable business rules

- Rule:
- Source:
- Files affected:

## Known constraints

- Technical:
- Business:
- Security:
- Compliance/privacy:
- Cost:
- Operational:

## Agent notes

- Prefer existing patterns over new abstractions.
- Ask for approval before destructive or production-impacting work.
- Keep documentation proportional to task level.
- Do not rely on mental notes; write durable context to `docs/ai`.
