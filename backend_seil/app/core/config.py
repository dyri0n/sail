import os

AIRFLOW_BASE_URL = os.getenv("AIRFLOW_BASE_URL", "http://airflow-webserver:8080")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME", "etl_api")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD")
