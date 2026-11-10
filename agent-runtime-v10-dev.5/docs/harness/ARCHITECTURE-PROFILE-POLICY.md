# Open Architecture Profile Policy

Status: normative for v8.

## Selection

Brownfield projects preserve their observed stack until migration is separately approved. Greenfield projects reuse an explicit user choice. When a material language, framework, platform, or tool choice is missing, the agent presents a small relevant set of options with team-fit, deployment, ecosystem, support, security, performance, and cost tradeoffs and obtains the user's decision before application implementation.

The user owns the product choice. Safety, support, compliance, and release gates may reject an unsafe or unsupported option or require human risk acceptance. Do not ask again when the request or verified project already answers the question.

## Profile

`schemas/architecture-profile.schema.json` supports layered, feature, mixed, and ecosystem-native organizations. A profile declares roots, modules, responsibilities, allowed dependencies, composition roots, interface contracts, extensions, and evidence. Folder names are not universal; ownership and dependency direction are.

Every entrypoint is a thin composition root. It may assemble startup, routers, middleware, providers, dependency injection, and layouts. It must not own routes, persistence, external clients, business rules, feature state/data, or reusable UI. File length is a warning signal, not proof of design quality.

Python/FastAPI plus React remains an optional packaged compatibility profile. It is not the default for unrelated greenfield projects.

## Verification

`scripts/architecture_check.py` reads v8 open profiles and v7 legacy Python/React policies. Python and JavaScript/TypeScript adapters perform syntax, dependency, and composition-root checks. A manual adapter requires explicit evidence. Missing adapter or user-decision evidence returns `INCOMPLETE`, never pass.
