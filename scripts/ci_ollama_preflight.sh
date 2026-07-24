#!/usr/bin/env bash
set -euo pipefail

# EasyBDD AI preflight for CI: fail fast when Ollama or required models are unavailable.

OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11434}"
CRAWLER_AI_PROVIDER="${CRAWLER_AI_PROVIDER:-ollama}"
CRAWLER_AI_MODEL="${CRAWLER_AI_MODEL:-qwen2.5-coder:7b}"
BUILDER_CHAT_MODEL="${BUILDER_CHAT_MODEL:-qwen2.5-coder:7b}"

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "ERROR: required command not found: $1" >&2
    exit 2
  }
}

require_cmd curl

if [[ "${CRAWLER_AI_PROVIDER}" != "ollama" ]]; then
  echo "INFO: CRAWLER_AI_PROVIDER=${CRAWLER_AI_PROVIDER}; skipping Ollama model checks."
  exit 0
fi

echo "INFO: checking Ollama endpoint ${OLLAMA_BASE_URL}"
if ! curl -fsS "${OLLAMA_BASE_URL}/api/tags" >/tmp/easybdd_ollama_tags.json; then
  echo "ERROR: Ollama is unreachable at ${OLLAMA_BASE_URL}" >&2
  exit 1
fi

echo "INFO: Ollama is reachable"

missing=0
for model in "${CRAWLER_AI_MODEL}" "${BUILDER_CHAT_MODEL}"; do
  if ! grep -Fq "\"name\":\"${model}\"" /tmp/easybdd_ollama_tags.json; then
    echo "ERROR: required model not found in Ollama: ${model}" >&2
    missing=1
  else
    echo "INFO: model available: ${model}"
  fi
done

if [[ ${missing} -ne 0 ]]; then
  echo "ERROR: one or more required Ollama models are missing" >&2
  echo "HINT: pull models with: ollama pull <model> or deploy/ollama model-init profile" >&2
  exit 1
fi

echo "OK: Ollama preflight passed"
