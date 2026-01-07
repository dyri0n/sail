"""Script simple para disparar el DAG maestro."""

import requests
from requests.auth import HTTPBasicAuth

# Airflow 3.x usa /api/v2
url = "http://localhost:8080/api/v2/dags/99_maestro_poblado_completo_dwh/dagRuns"
auth = HTTPBasicAuth("airflow", "airflow")

try:
    r = requests.post(
        url,
        json={"conf": {}},
        auth=auth,
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    print(f"Status: {r.status_code}")
    if r.status_code in [200, 201]:
        data = r.json()
        print(f"DAG Run ID: {data.get('dag_run_id')}")
        print(f"State: {data.get('state')}")
    else:
        print(f"Error: {r.text}")
except requests.exceptions.ConnectionError:
    print("Error: No se puede conectar a Airflow en localhost:8080")
except Exception as e:
    print(f"Error: {e}")
