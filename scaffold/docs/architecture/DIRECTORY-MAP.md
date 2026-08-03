# Directory responsibility map

Status: initialize project-specific extensions; the minimum profile below is mandatory.

| Path | Responsibility | Permitted dependencies |
|---|---|---|
| `backend/app/controllers/` | HTTP routes, request/response mapping and transport errors | services, schemas |
| `backend/app/services/` | Use cases and authoritative business rules | models, repositories, schemas, approved server integrations |
| `backend/app/models/` | Domain and persistence models | pure shared model utilities |
| `backend/app/schemas/` | Validated API and integration DTOs | model types without transport behavior |
| `backend/app/repositories/` | Persistence adapters | models and database client abstractions |
| `frontend/src/api/` | HTTP transport and typed API clients | utils and generated contract types |
| `frontend/src/assets/` | Static assets | none |
| `frontend/src/components/layout/` | Structural reusable UI | UI components, hooks, context, utils, assets |
| `frontend/src/components/ui/` | Reusable visual primitives | hooks, utils, assets |
| `frontend/src/context/` | Genuine cross-tree client state | services, hooks, utils |
| `frontend/src/data/` | Static content and synthetic mocks | pure types and utils |
| `frontend/src/hooks/` | Reusable React behavior | api, services, context, utils |
| `frontend/src/pages/` | Route-level composition | components, hooks, context, services, api, data, utils |
| `frontend/src/services/` | Presentation-side orchestration and approved third-party clients | api, data, utils |
| `frontend/src/utils/` | Pure reusable functions | other pure utilities only |

Additional directories are allowed. Record every new top-level architectural layer here or in `docs/ai/conventions.md` with its responsibility, owner, permitted dependencies, and reason it does not fit an existing layer.
