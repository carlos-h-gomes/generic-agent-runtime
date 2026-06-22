#!/usr/bin/env bash
set -euo pipefail

# Security check — layered, graceful-degradation.
# Each layer runs only if its tool exists. Missing tools print an actionable hint
# and the layer is recorded as "not validated" rather than failing the whole run.
# Tools current as of 2026: Semgrep (SAST), Gitleaks/TruffleHog (secrets),
# Trivy/pip-audit/npm audit (SCA / dependency CVEs).

echo "[Security] Iniciando varredura de segurança em camadas..."
ran_any=false

# ------------------------------------------------------------------
# 1. SAST — application logic flaws, injections, SSRF patterns
# ------------------------------------------------------------------
echo "==> [SAST] Falhas de lógica, injeções e padrões inseguros..."
if command -v semgrep >/dev/null 2>&1; then
  # p/default is the broad community ruleset; add p/secrets for inline secrets.
  semgrep scan --config="p/default" --config="p/secrets" --error . || true
  ran_any=true
else
  echo "[Aviso] Semgrep não encontrado. Recomendado para SSRF, injeções e prompt-injection patterns."
fi

# ------------------------------------------------------------------
# 2. Secrets — leaked credentials in code/history
# ------------------------------------------------------------------
echo "==> [Secrets] Credenciais e segredos vazados..."
if command -v gitleaks >/dev/null 2>&1; then
  # Fast, single-binary, SARIF-capable. Scans working tree + staged.
  gitleaks detect --no-banner --redact || true
  ran_any=true
elif command -v trufflehog >/dev/null 2>&1; then
  # TruffleHog verifies whether found keys are still LIVE (read-only API calls).
  trufflehog filesystem . --no-verification --exclude-paths=.trufflehog-exclude || true
  ran_any=true
else
  echo "[Aviso] Gitleaks/TruffleHog não encontrados. Usando fallback heurístico via regex..."
  PATTERN='(api[_-]?key|secret|token|password|passwd|private[_-]?key|BEGIN RSA PRIVATE KEY|BEGIN OPENSSH PRIVATE KEY|access[_-]?key)'
  if command -v rg >/dev/null 2>&1; then
    rg -n --hidden --glob '!node_modules' --glob '!.git' --glob '!dist' --glob '!build' -i "$PATTERN" . || true
  else
    grep -RInEi "$PATTERN" . --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=build || true
  fi
fi

# ------------------------------------------------------------------
# 3. SCA — dependency / supply-chain CVEs (OWASP LLM03 / ASI04)
# ------------------------------------------------------------------
echo "==> [SCA] Vulnerabilidades em dependências (supply chain)..."
if command -v trivy >/dev/null 2>&1; then
  # Filesystem SCA across most package managers. ignore-unfixed avoids blocking
  # on CVEs with no available fix.
  trivy fs --scanners vuln --severity HIGH,CRITICAL --ignore-unfixed . || true
  ran_any=true
else
  # Per-ecosystem fallbacks.
  if [ -f requirements.txt ] || [ -f pyproject.toml ] || [ -f poetry.lock ] || [ -f uv.lock ]; then
    if command -v pip-audit >/dev/null 2>&1; then
      echo "    -> pip-audit (Python deps)"
      pip-audit || true
      ran_any=true
    else
      echo "[Aviso] Python detectado mas Trivy/pip-audit ausentes. SCA não executado."
    fi
  fi
  if [ -f package.json ] && command -v npm >/dev/null 2>&1; then
    echo "    -> npm audit (Node deps)"
    npm audit --audit-level=high || true
    ran_any=true
  fi
fi

# ------------------------------------------------------------------
# 4. IaC / container misconfig (when infra present)
# ------------------------------------------------------------------
if [ -f docker-compose.yml ] || [ -f compose.yml ] || [ -f Dockerfile ] || ls ./*.tf >/dev/null 2>&1; then
  echo "==> [IaC] Más configurações de containers/infra..."
  if command -v trivy >/dev/null 2>&1; then
    trivy config . || true
    ran_any=true
  else
    echo "[Aviso] Trivy não encontrado. Recomendado para auditar Dockerfile/compose/Terraform."
  fi
fi

if [ "$ran_any" = false ]; then
  echo "[Security] Nenhuma ferramenta de segurança disponível. Registre como 'not validated' e instale ao menos Semgrep + Gitleaks + Trivy."
fi

echo "[Security] Varredura concluída."
