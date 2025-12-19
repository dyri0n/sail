#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# SCRIPT MAESTRO - DETENER TODA LA INFRAESTRUCTURA
# =============================================================================
# Ejecutar desde la raíz del proyecto: ./scripts/stop-all.sh
# =============================================================================

echo "========================================"
echo " Deteniendo Infraestructura Completa"
echo "========================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# -----------------------------------------------------------------------------
# 1. Airflow (detener primero para liberar conexiones)
# -----------------------------------------------------------------------------
echo "[1/3] Deteniendo Airflow..."
cd "$ROOT_DIR/etl-node/airflow"
./scripts/compose-down.sh

# -----------------------------------------------------------------------------
# 2. Staging Database (ambos modos si están activos)
# -----------------------------------------------------------------------------
echo ""
echo "[2/3] Deteniendo Staging Database..."
cd "$ROOT_DIR/stg-node"
./scripts/compose-down.sh

# -----------------------------------------------------------------------------
# 3. Data Warehouse
# -----------------------------------------------------------------------------
echo ""
echo "[3/3] Deteniendo Data Warehouse..."
cd "$ROOT_DIR/dwh-node"
./scripts/compose-down.sh

# -----------------------------------------------------------------------------
# Resumen
# -----------------------------------------------------------------------------
echo ""
echo "========================================"
echo " Infraestructura Detenida!"
echo "========================================"
echo ""

cd "$ROOT_DIR"
