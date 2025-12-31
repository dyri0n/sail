#!/usr/bin/env bash
# Start postgres DB via docker compose
# Usage: ./start-db.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSE_FILE="$PROJECT_ROOT/docker/postgres/docker-compose.yml"

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker not found in PATH" >&2
  exit 1
fi

if [ ! -f "$COMPOSE_FILE" ]; then
  echo "docker compose file not found: $COMPOSE_FILE" >&2
  exit 1
fi

echo "Starting Postgres with: docker compose -f $COMPOSE_FILE up -d"
docker compose -f "$COMPOSE_FILE" up -d

echo "Done. Run 'docker ps' to check containers."
