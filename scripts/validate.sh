#!/usr/bin/env bash
set -euo pipefail

run_if_exists() {
  local cmd="$1"
  local label="$2"
  if eval "$cmd" >/dev/null 2>&1; then
    echo "==> $label"
    eval "$cmd"
  fi
}

echo "Generic Agent Runtime validation runner"

# 1. Validação Node.js
if [ -f package.json ]; then
  if command -v npm >/dev/null 2>&1; then
    echo "==> Executando lint e testes (Node)"
    npm run lint --if-present
    npm run typecheck --if-present
    npm test --if-present
    npm run build --if-present
  fi
fi

# 2. Validação Python
if [ -f pyproject.toml ] || [ -f requirements.txt ]; then
  if command -v ruff >/dev/null 2>&1; then 
    echo "==> Executando lint (Ruff)"
    ruff check .
  fi
  if command -v pytest >/dev/null 2>&1; then 
    echo "==> Executando testes (Pytest)"
    pytest
  fi
fi

# 3. Infraestrutura e Orquestração
if [ -f docker-compose.yml ] || [ -f compose.yml ]; then
  if command -v docker >/dev/null 2>&1; then 
    echo "==> Validando sintaxe do Docker Compose"
    docker compose config >/dev/null
  fi
  
  if command -v trivy >/dev/null 2>&1; then
    echo "==> Varredura de configurações (Trivy)"
    # Analisa o manifesto em busca de más práticas de privilégio em containers
    trivy config . || true
  else
    echo "[Aviso] Trivy não encontrado. Fortemente recomendado para auditar configurações de containers."
  fi
fi

echo "Validation completed."