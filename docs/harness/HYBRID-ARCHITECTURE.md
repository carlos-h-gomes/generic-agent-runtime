# Optional Python/React hybrid application profile

This retained Harness v7 compatibility profile has two isolated deployable boundaries: a Python HTTP API and a React TypeScript/Vite client. It is used in Harness 8 only when the user selects it, an existing project already conforms, or a separate migration authorizes it. The frontend never imports Python source; the backend never owns React presentation. Integration is through a versioned, validated API contract. Brownfield governance adoption preserves the observed stack.

The profile topology is defined by `project-templates/python-react-hybrid/` and its version-1 architecture contract. It is not a closed list. Add a directory when it has a distinct responsibility that does not fit an existing layer, then record its owner and permitted dependencies.

Backend direction is controllers to services to models/repositories. Controllers map HTTP, services own use cases, repositories own persistence adapters, models own domain/persistence representation, and schemas own DTO validation.

Frontend transport belongs in `api`, presentation orchestration in `services`, route composition in `pages`, reusable structure and controls in `components`, reusable React behavior in `hooks`, genuine cross-tree state in `context`, static or synthetic content in `data`, and pure helpers in `utils`.

Entrypoints are composition roots. Filename alone is not a violation; owned behavior is. Static validation catches minimum structure, known dependency reversals, oversized or behavior-bearing entrypoints, and undocumented new layers. Human architecture review remains required because static checks cannot prove semantic quality.
