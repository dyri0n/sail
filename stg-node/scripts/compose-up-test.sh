#!/usr/bin/env bash
set -euo pipefail

# Uso: ./scripts/compose-up-test.sh
# Levanta staging en modo testing (con datos de prueba)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/.."

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: Docker no está en PATH" >&2
  exit 1
fi

docker compose --profile testing up -d
