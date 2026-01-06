import asyncio
import time
from app.utils.airflow_client import airflow_client

async def verify_etl_run():
    """Verifica la ejecución del ETL y obtiene conteos"""
    print("--- STARTING VERIFICATION ---")
    
    # 1. Trigger DAG
    print("[1] Triggering DAG 00_carga_excel_staging...")
    trigger_result = await airflow_client.trigger_dag("00_carga_excel_staging")
    
    if not trigger_result:
        print("❌ Failed to trigger DAG")
        return
    
    dag_run_id = trigger_result["dag_run_id"]
    print(f"    -> DAG Run ID: {dag_run_id}")
    
    # 2. Esperar a que termine
    print("[2] Waiting for completion (polling)...")
    max_wait = 300  # 5 minutos máximo
    poll_interval = 5  # segundos
    elapsed = 0
    
    while elapsed < max_wait:   
        # In the while loop:
        status = await airflow_client.get_dag_run_status("00_carga_excel_staging", dag_run_id)
        if status is None:
            print("❌ Failed to get DAG status - check CLI permissions or container name.")
            return None
        current_state = status["state"]
        print(f"    -> Current State: {current_state}")
        
        if current_state in ["success", "failed"]:
            break
            
        await asyncio.sleep(poll_interval)
        elapsed += poll_interval
    
    if elapsed >= max_wait:
        print("⚠️  Timeout waiting for DAG completion")
        return
    
    print(f"    -> Finished with state: {current_state}")
    
    if current_state != "success":
        print("❌ DAG failed")
        return
    
    print("[3] Fetching XCom from stg_resumen...")
    keys_to_try = ['return_value', 'row_count']  # Exact matches from your DAG
    
    for key in keys_to_try:
        print(f"    -> Trying key: '{key}'")
        result = await airflow_client.get_task_xcom(
            dag_id="00_carga_excel_staging",
            dag_run_id=dag_run_id,
            task_id="stg_resumen",
            xcom_key=key
        )
        if result is not None:
            print(f"    ✅ Found in '{key}': {result}")
            if isinstance(result, (int, float)):
                final_count = result
                print(f"🎉 Total records: {final_count}")
                return final_count
            # If dict, extract as before (e.g., result.get('records') or similar)
            return result
    
    # Fallback: Try other tasks if stg_resumen has no XCom (unlikely)
    other_tasks = ["stg_cargar_sap", "stg_cargar_capacitaciones", "stg_cargar_asistencia_cap", "stg_cargar_asistencia"]
    for task_id in other_tasks:
        print(f"\n    -> Fallback to task: {task_id}")
        for key in keys_to_try:
            result = await airflow_client.get_task_xcom(
                dag_id="00_carga_excel_staging",
                dag_run_id=dag_run_id,
                task_id=task_id,
                xcom_key=key
            )
            if result is not None:
                print(f"    ✅ Found in '{task_id}'/'{key}': {result}")
                return result  # Adjust extraction if needed
    
    # Debug: List all XComs for the run (add to get_task_xcom if needed)
    print("\n[4] No XCom found - listing all for stg_resumen...")
    all_xcoms = await airflow_client.get_task_xcom(
        dag_id="00_carga_excel_staging",
        dag_run_id=dag_run_id,
        task_id="stg_resumen",
        xcom_key=None  # Gets all
    )
    if all_xcoms:
        print("All XCom entries:", all_xcoms)
    
    print("⚠️ No XCom found. Check: 1) Task runs/succeeds, 2) xcom_push happens, 3) API auth/URL.")
    return None

if __name__ == "__main__":
    result = asyncio.run(verify_etl_run())
    if result is not None:
        print(f"\n🎉 CONTEOS OBTENIDOS: {result}")
    else:
        print(f"\n❌ No se pudo obtener ningún conteo")