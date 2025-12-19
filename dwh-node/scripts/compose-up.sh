#!/usr/bin/env bash
set -euo pipefail

# Uso: ./scripts/compose-up.sh
# Levanta el contenedor Data Warehouse

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/.."

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: Docker no está en PATH" >&2
  exit 1
fi

docker compose up -d
