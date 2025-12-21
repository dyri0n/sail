#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# SCRIPT MAESTRO - LEVANTAR TODA LA INFRAESTRUCTURA
# =============================================================================
# Ejecutar desde la raíz del proyecto: ./scripts/start-all.sh
# =============================================================================

echo "========================================"
echo " Levantando Infraestructura Completa"
echo "========================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# -----------------------------------------------------------------------------
# 1. DWH Node (Data Warehouse + Staging)
# -----------------------------------------------------------------------------
echo "[1/2] Levantando Data Warehouse (puerto 6000)..."
cd "$ROOT_DIR/dwh-node"
./scripts/compose-up.sh

# -----------------------------------------------------------------------------
# 2. ETL Node (Airflow)
# -----------------------------------------------------------------------------
echo ""
echo "[2/2] Levantando Airflow (puerto 8080)..."
cd "$ROOT_DIR/etl-node/airflow"
./scripts/compose-up.sh

# -----------------------------------------------------------------------------
# Resumen
# -----------------------------------------------------------------------------
echo ""
echo "========================================"
echo " Infraestructura Levantada!"
echo "========================================"
cat <<EOF

Servicios disponibles:
  - Data Warehouse:  localhost:6000 (usuario: dwh_admin, schemas: stg y dwh)
  - Airflow UI:      http://localhost:8080 (admin/admin)

Próximos pasos:
  1. Verifica que .env esté configurado correctamente en etl-node/airflow/
  2. Espera ~60s para que Airflow inicialice completamente
  3. Accede a http://localhost:8080 para ver los DAGs

EOF

cd "$ROOT_DIR"
