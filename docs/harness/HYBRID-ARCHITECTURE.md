# Hybrid application architecture

Harness v6 application projects have two isolated deployable boundaries: a Python HTTP API and a React TypeScript/Vite client. The frontend never imports Python source; the backend never owns React presentation. Integration is through a versioned, validated API contract.

The minimum topology is defined in `docs/ai/conventions.md` and `docs/ai/architecture-policy.json`. It is not a closed list. Add a directory when it has a distinct responsibility that does not fit an existing layer, then record its owner and permitted dependencies.

Backend direction is controllers to services to models/repositories. Controllers map HTTP, services own use cases, repositories own persistence adapters, models own domain/persistence representation, and schemas own DTO validation.

Frontend transport belongs in `api`, presentation orchestration in `services`, route composition in `pages`, reusable structure and controls in `components`, reusable React behavior in `hooks`, genuine cross-tree state in `context`, static or synthetic content in `data`, and pure helpers in `utils`.

Entrypoints are composition roots. Filename alone is not a violation; owned behavior is. Static validation catches minimum structure, known dependency reversals, oversized or behavior-bearing entrypoints, and undocumented new layers. Human architecture review remains required because static checks cannot prove semantic quality.
