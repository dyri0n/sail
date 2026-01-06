import requests
BACKEND_URL = "http://host.docker.internal:8000/api/v1/etl"
def notify_task_complete(context):
    task = context["task_instance"]
    dag_run = context["dag_run"]
    
    requests.post(
        f"{BACKEND_URL}/callback/task",
        json={
            "dag_run_id": dag_run.run_id,
            "task_id": task.task_id,
            "state": str(task.state),
            "start_date": task.start_date.isoformat(),
            "operator": task.operator
        },
        timeout=5
    )
def notify_dag_complete(context):
    dag_run = context["dag_run"]
    
    requests.post(
        f"{BACKEND_URL}/callback/dag",
        json={
            "dag_run_id": dag_run.run_id,
            "state": str(dag_run.state),
            "end_date": dag_run.end_date.isoformat()
        },
        timeout=5
    )