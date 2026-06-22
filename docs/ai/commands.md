# Commands

Status: template. Fill during Project Profiling.

Only document commands verified from repository files such as package files, Makefiles, CI config, Docker files, README, or existing scripts.

## Package manager

- Detected package manager:
- Install command:
- Dev command:
- Build command:

## Validation commands

```bash
# Test

# Lint

# Typecheck

# Build

# Security check (SAST + secrets)

# Dependency / supply-chain scan (SCA, e.g. trivy fs / pip-audit / npm audit)

# Docker/infra check

# Cost/usage check
```

## Safe commands

Commands agents may run without approval:

```bash
# Example:
# npm test
# npm run lint
# docker compose config
```

## Approval-required commands

Commands that need explicit human approval:

```bash
# production deploy
# destructive migration
# data deletion
# bulk message sending
# paid high-volume execution
# secrets rotation
```

## Command notes

- Do not invent commands.
- Prefer the smallest relevant validation subset.
- Record command failures honestly.
- Never claim validation passed unless it actually ran successfully.
