import requests
from app.core.config import settings


class AirflowService:

    def trigger_dag(self, dag_id: str, conf: dict):
        url = f"{settings.AIRFLOW_BASE_URL}/api/v1/dags/{dag_id}/dagRuns"

        response = requests.post(
            url,
            auth=(settings.AIRFLOW_USER, settings.AIRFLOW_PASSWORD),
            json={"conf": conf},
            timeout=10
        )

        response.raise_for_status()
        return response.json()
