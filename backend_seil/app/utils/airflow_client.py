import aiohttp
import asyncio
import subprocess
from typing import Dict, Any, Optional
import json
from datetime import datetime
import textwrap  # Added for dedent

class AirflowClient:
    def __init__(self):
        self.base_url = "http://localhost:8080/api/v2"  
        self.username = "admin" 
        self.password = "admin" 
        self.container_name = "airflow-airflow-webserver-1"
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        url = f"{self.base_url}{endpoint}"
        auth = aiohttp.BasicAuth(self.username, self.password)
        headers = kwargs.pop('headers', {})
        headers['Content-Type'] = 'application/json'

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, auth=auth, headers=headers, **kwargs) as response:
                    if 200 <= response.status < 300:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        print(f"[WARN API] Status {response.status} en {endpoint}: {error_text}")
                        return None
        except Exception as e:
            print(f"[ERROR API] Excepción al llamar {endpoint}: {str(e)}")
            return None

    async def trigger_dag(self, dag_id: str, conf: Dict = None):
        print(f"[DEBUG] Disparando DAG (API): {dag_id}")
        endpoint = f"/dags/{dag_id}/dagRuns"
        timestamp = datetime.utcnow().isoformat()
        custom_run_id = f"manual__{timestamp}"
        payload = {
            "dag_run_id": custom_run_id,
            "conf": conf or {}
        }
        try:
            data = await self._make_request("POST", endpoint, json=payload)
            if data:
                print(f"✅ DAG disparado exitosamente (API). ID: {data.get('dag_run_id')}")
                return {
                    "dag_run_id": data.get("dag_run_id"),
                    "execution_date": data.get("execution_date"),
                    "state": data.get("state")
                }
            else:
                print("[WARN] API trigger falló, intentando Fallback CLI...")
                return await self._trigger_dag_cli(dag_id, conf, custom_run_id)
        except Exception as e:
            print(f"[ERROR] Trigger API falló: {e}")
            return None

    async def _trigger_dag_cli(self, dag_id: str, conf: Dict, run_id: str):
        cmd = [
            "docker", "exec", self.container_name,
            "airflow", "dags", "trigger", dag_id,
            "--run-id", run_id
        ]
        if conf:
            cmd.extend(["--conf", json.dumps(conf)])
        try:
            subprocess.run(cmd, capture_output=True, timeout=15)
            return {"dag_run_id": run_id, "state": "queued"}
        except:
            return None

    async def get_dag_run_status(self, dag_id: str, dag_run_id: str):
        dag_state = "unknown"
        cmd = [
            "docker", "exec", self.container_name,
            "airflow", "dags", "list-runs",
            dag_id,
            "--output", "json"
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if res.returncode == 0:
                output = res.stdout.strip()
                if output:
                    try:
                        runs = json.loads(output)
                        for r in runs:
                            if r.get('run_id') == dag_run_id or r.get('dag_run_id') == dag_run_id:
                                dag_state = r.get('state') or "unknown"
                                break
                    except:
                        pass
            else:
                print(f"[WARN] CLI list-runs falló: {res.stderr}")
        except Exception as e:
            print(f"[ERROR] get_dag_run_status (DAG) error: {e}")

        tasks_list = []
        cmd_tasks = [
            "docker", "exec", self.container_name,
            "airflow", "tasks", "states-for-dag-run",
            dag_id, dag_run_id,
            "--output", "json"
        ]
        try:
            res = subprocess.run(cmd_tasks, capture_output=True, text=True, timeout=10)
            if res.returncode == 0:
                output = res.stdout.strip()
                if output:
                    try:
                        data = json.loads(output)
                        if isinstance(data, list):
                            for t in data:
                                tasks_list.append({
                                    "task_id": t.get("task_id"),
                                    "state": t.get("state"),
                                    "start_date": t.get("start_date"),
                                    "end_date": t.get("end_date")
                                })
                        elif isinstance(data, dict):
                            for tid, tstate in data.items():
                                if isinstance(tstate, dict):
                                    tasks_list.append({
                                        "task_id": tid,
                                        "state": tstate.get("state"),
                                        "start_date": tstate.get("start_date"),
                                        "end_date": tstate.get("end_date")
                                    })
                                else:
                                    tasks_list.append({"task_id": tid, "state": tstate})
                    except:
                        pass
            else:
                print(f"[WARN] CLI tasks states falló: {res.stderr}")
        except Exception as e:
            print(f"[ERROR] get_dag_run_status (Tasks) error: {e}")
        
        return {
            "state": dag_state,
            "tasks": tasks_list
        }

    async def get_task_xcom(self, dag_id: str, dag_run_id: str, task_id: str, xcom_key: str = 'return_value') -> Any:
        print(f"[DEBUG] Fetching XCom via API: dag={dag_id}, run={dag_run_id}, task={task_id}, key={xcom_key}")
        endpoint = f"/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/xcomEntries"
        params = {'key': xcom_key}
        data = await self._make_request("GET", endpoint, params=params)
        if data and 'xcom_entries' in data and data['xcom_entries']:
            value = data['xcom_entries'][0].get('value')
            print(f"    -> API Found: {value}")
            return value
        
        print("[WARN] API XCom failed, trying CLI fallback...")
        return await self._get_task_xcom_cli(dag_id, dag_run_id, task_id, xcom_key)

    async def _get_task_xcom_cli(self, dag_id: str, dag_run_id: str, task_id: str, xcom_key: str):
        """Fallback CLI to fetch XCom using python -c"""
        try:
            # Build Python snippet with dedent and error handling
            code_snippet = textwrap.dedent(f"""
                import warnings
                warnings.filterwarnings("ignore")
                from airflow.models.xcom import XCom
                from airflow.settings import Session
                import traceback

                try:
                    session = Session()
                    xcom = session.query(XCom).filter(
                        XCom.dag_id == '{dag_id}',
                        XCom.task_id == '{task_id}',
                        XCom.run_id == '{dag_run_id}',
                        XCom.key == '{xcom_key}'
                    ).first()
                    print(xcom.value if xcom else 'None')
                    session.close()
                except Exception as e:
                    print('Error: ' + str(e))
                    print(traceback.format_exc())
            """)

            cmd = ["docker", "exec", self.container_name, "python", "-c", code_snippet]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            output = res.stdout.strip()
            error = res.stderr.strip()
            if res.returncode == 0:
                if output == 'None':
                    print("    -> CLI: No XCom found")
                    return None
                if output.startswith('Error: '):
                    print(f"    -> CLI Error: {output}")
                    return None
                # Assume output is the value (e.g., int or str); parse if needed
                try:
                    return int(output)  # If count is int
                except ValueError:
                    try:
                        return json.loads(output)  # If JSON
                    except:
                        return output  # Else str
            else:
                print(f"[WARN] CLI XCom failed (rc={res.returncode}): stdout={output[:200]}, stderr={error[:200]}")
                return None
        except Exception as e:
            print(f"[ERROR] CLI XCom error: {e}")
            return None

airflow_client = AirflowClient()