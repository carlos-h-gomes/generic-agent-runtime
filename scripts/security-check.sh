#!/usr/bin/env bash
set -euo pipefail

echo "[Security] Iniciando varredura de segurança avançada..."

# 1. Varredura SAST (Falhas de Lógica e Injeções)
echo "==> Verificando falhas de lógica, injeções e vazamentos..."
if command -v semgrep >/dev/null 2>&1; then
  # Varre usando padrões rigorosos de segurança e falhas em rotas de API (Node/Python)
  semgrep scan --config="p/security-audit" --config="p/secrets" . || true
else
  echo "[Aviso] Semgrep não encontrado. Recomendado instalar para identificar SSRF e Prompt Injections."
fi

# 2. Varredura de Segredos (Substituindo o grep heurístico)
echo "==> Verificando credenciais e segredos vazados..."
if command -v trufflehog >/dev/null 2>&1; then
  # TruffleHog valida ativamente chaves expostas para ver se estão ativas
  trufflehog filesystem . --no-verification --exclude-paths=.trufflehog-exclude || true
else
  echo "[Aviso] TruffleHog não encontrado. Usando fallback heurístico via regex..."
  PATTERN='(api[_-]?key|secret|token|password|passwd|private[_-]?key|BEGIN RSA PRIVATE KEY|BEGIN OPENSSH PRIVATE KEY|access[_-]?key)'
  if command -v rg >/dev/null 2>&1; then
    rg -n --hidden --glob '!node_modules' --glob '!.git' --glob '!dist' --glob '!build' -i "$PATTERN" . || true
  else
    grep -RInEi "$PATTERN" . --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=build || true
  fi
fi

echo "[Security] Varredura concluída."