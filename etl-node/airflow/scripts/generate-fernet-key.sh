#!/bin/bash
# Script para generar una clave Fernet para Airflow
# Uso: ./generate-fernet-key.sh

echo "Generando clave Fernet para Airflow..."

FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" 2>/dev/null)

if [ $? -eq 0 ]; then
    echo ""
    echo "Clave Fernet generada:"
    echo "$FERNET_KEY"
    echo ""
    echo "Agrégala a tu archivo .env como:"
    echo "AIRFLOW_FERNET_KEY=$FERNET_KEY"
else
    echo "Error: Asegúrate de tener Python y cryptography instalados"
    echo "Instala con: pip install cryptography"
fi
