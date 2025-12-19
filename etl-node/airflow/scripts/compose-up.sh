#!/usr/bin/env bash
set -euo pipefail

# Uso: ./scripts/compose-up.sh [--testing]
# Levanta docker-compose; con --testing activa el perfil "testing".

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/.."

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: Docker no está en PATH" >&2
  exit 1
fi

PROFILE=""
if [[ "${1-}" == "--testing" ]]; then
  PROFILE="testing"
fi

compose_cmd=(docker compose)
if [[ -n "$PROFILE" ]]; then
  compose_cmd+=(--profile "$PROFILE")
fi

"${compose_cmd[@]}" up -d
