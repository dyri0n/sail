#!/usr/bin/env bash
set -euo pipefail

# Uso: ./scripts/compose-up-prod.sh
# Levanta staging en modo producción (sin datos)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/.."

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: Docker no está en PATH" >&2
  exit 1
fi

docker compose --profile prod up -d
