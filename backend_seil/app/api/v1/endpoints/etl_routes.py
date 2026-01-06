from fastapi import APIRouter, Depends, HTTPException
from app.utils.airflow_client import airflow_client
from app.db.session import get_db
from app.core.dependencies import get_current_user
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.etl import ETLExecution, ExecutionState
import traceback

router = APIRouter(prefix="/etl", tags=["ETL"])

@router.post("/trigger")
async def trigger_etl(
    dag_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disparar un DAG de Airflow y registrar la ejecución en DB"""
    # Validar permisos (current_user es un dict con el payload del JWT)
    if current_user.get("role") != "ADMIN":
        raise HTTPException(403, "Solo administradores pueden ejecutar el ETL")
    
    try:
        # 1. Disparar DAG en Airflow vía CLI  
        response = await airflow_client.trigger_dag(dag_id)
        
        # 2. Registrar ejecución en base de datos
        execution = ETLExecution(
            dag_id=dag_id,
            dag_run_id=response["dag_run_id"],
            execution_date=datetime.utcnow(),
            triggered_by_user_id=current_user.get("sub"),  # UUID del usuario (campo 'sub' en JWT)
            state=ExecutionState.QUEUED,
            start_date=datetime.utcnow()
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)
        
        return {
            "execution_id": execution.id,
            "dag_run_id": execution.dag_run_id,
            "status": execution.state.value,
            "message": "ETL disparado correctamente"
        }
        
    except Exception as e:
        # Imprimir traceback completo para debugging
        print("=" * 80)
        print("ERROR EN TRIGGER ETL:")
        print(traceback.format_exc())
        print("=" * 80)
        
        # Manejar errores de Airflow o DB
        error_msg = str(e)
        
        if "docker" in error_msg.lower() or "container" in error_msg.lower():
            raise HTTPException(
                status_code=503,
                detail="No se pudo conectar con Airflow. Verifica que el contenedor esté corriendo."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Error al disparar ETL: {error_msg}"
            )


@router.get("/history")
async def get_history(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 20
):
    """Obtiene el historial de ejecuciones ETL desde la base de datos"""
    # Consultar últimas ejecuciones ordenadas por fecha de creación
    executions = db.query(ETLExecution).order_by(
        ETLExecution.created_at.desc()
    ).limit(limit).all()
    
    # Formatear respuesta
    history = []
    
    # Optimización: Solo buscar detalles para las últimas 5 ejecuciones para no saturar
    # (Las llamadas CLI son lentas)
    for i, exec in enumerate(executions):
        duration = None
        if exec.start_date and exec.end_date:
            duration = int((exec.end_date - exec.start_date).total_seconds())
        
        details = {}
        # Solo intentar obtener XCom para las primeras 5 y si son de los DAGs conocidos
        if i < 5 and exec.dag_id in ["00_carga_excel_staging", "01_etl_conformed"] and exec.state.value in ["success", "failed", "running"]:
            task_resumen = "stg_resumen" if exec.dag_id == "00_carga_excel_staging" else "dw_resumen"
            try:
                xcom_data = await airflow_client.get_task_xcom(
                     exec.dag_id,
                     exec.dag_run_id,
                     task_resumen
                )
                if xcom_data and isinstance(xcom_data, dict):
                     details = xcom_data
                     print(f"[DEBUG HIST] XCom para {exec.id}: {details}")
            except Exception as e:
                print(f"[WARN] Error XCom history: {e}")

        history.append({
            "id": exec.id,
            "dag_id": exec.dag_id,
            "dag_run_id": exec.dag_run_id,
            "execution_date": exec.execution_date.isoformat() if exec.execution_date else None,
            "state": exec.state.value,
            "start_date": exec.start_date.isoformat() if exec.start_date else None,
            "end_date": exec.end_date.isoformat() if exec.end_date else None,
            "duration": duration,
            "details": details
        })
    
    return {"history": history}


@router.get("/status/{execution_id}")
async def get_status(
    execution_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene el estado de una ejecución ETL específica con detalles de tareas"""
    print(f"[DEBUG] Consultando estado de ejecución ID: {execution_id}")
    
    # Buscar ejecución en base de datos
    execution = db.query(ETLExecution).filter(
        ETLExecution.id == execution_id
    ).first()
    
    if not execution:
        print(f"[ERROR] Ejecución {execution_id} no encontrada en DB")
        raise HTTPException(404, "Ejecución no encontrada")
    
    print(f"[DEBUG] Estado actual en DB: {execution.state.value}")
    print(f"[DEBUG] dag_id: {execution.dag_id}, dag_run_id: {execution.dag_run_id}")
    
    # Sincronizar estado desde Airflow si aún no ha terminado
    if execution.state.value in ["queued", "running"]:
        print(f"[DEBUG] Estado necesita sincronización, consultando Airflow...")
        
        airflow_status = await airflow_client.get_dag_run_status(
            execution.dag_id, 
            execution.dag_run_id
        )
        
        print(f"[DEBUG] Respuesta de Airflow: {airflow_status}")
        
        # Mapear estados de Airflow a nuestros estados
        state_mapping = {
            "success": ExecutionState.SUCCESS,
            "failed": ExecutionState.FAILED,
            "running": ExecutionState.RUNNING,
            "queued": ExecutionState.QUEUED
        }
        
        new_state = state_mapping.get(airflow_status["state"], execution.state)
        print(f"[DEBUG] Estado mapeado: {airflow_status['state']} -> {new_state}")
        
        if new_state != execution.state:
            print(f"[DEBUG] Actualizando estado: {execution.state} -> {new_state}")
            execution.state = new_state
            if new_state in [ExecutionState.SUCCESS, ExecutionState.FAILED]:
                execution.end_date = datetime.utcnow()
                print(f"[DEBUG] Estado final alcanzado, estableciendo end_date")
            db.commit()
            print(f"[DEBUG] Estado guardado en DB")
        else:
            print(f"[DEBUG] Estado sin cambios")
    else:
        print(f"[DEBUG] Estado ya es final: {execution.state.value}, no se sincroniza")
    
    # Calcular progreso basado en tareas completadas
    total_tasks = len(execution.tasks) if execution.tasks else 0
    completed_tasks = sum(1 for task in execution.tasks if task.state.value in ["success", "failed", "skipped"]) if execution.tasks else 0
    progress = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
    
    print(f"[DEBUG] Progreso: {completed_tasks}/{total_tasks} tareas = {progress}%")

    # Extraer métricas adicionales (registros procesados) si es el DAG de staging
    details = {}
    if execution.dag_id in ["00_carga_excel_staging", "01_etl_conformed"]:
        task_resumen = "stg_resumen" if execution.dag_id == "00_carga_excel_staging" else "dw_resumen" # Ajustar nombre task si es necesario
        
        # Intentar obtener XCom
        try:
             # Solo si la ejecución está avanzada (running o success o failed)
            if execution.state.value in ["success", "failed", "running"]:
                 xcom_data = await airflow_client.get_task_xcom(
                     execution.dag_id,
                     execution.dag_run_id,
                     task_resumen
                 )
                 if xcom_data and isinstance(xcom_data, dict):
                     details = xcom_data
                     print(f"[DEBUG] Detalles obtenidos de XCom: {details}")
        except Exception as e:
            print(f"[WARN] No se pudieron obtener detalles de XCom: {e}")
    
    
    # Formatear tareas
    tasks = []
    if execution.tasks:
        for task in execution.tasks:
            tasks.append({
                "task_id": task.task_id,
                "state": task.state.value,
                "start_date": task.start_date.isoformat() if task.start_date else None,
                "end_date": task.end_date.isoformat() if task.end_date else None,
                "duration": task.duration
            })
    
    return {
        "execution_id": execution.id,
        "dag_id": execution.dag_id,
        "state": execution.state.value,
        "start_date": execution.start_date.isoformat() if execution.start_date else None,
        "end_date": execution.end_date.isoformat() if execution.end_date else None,
        "end_date": execution.end_date.isoformat() if execution.end_date else None,
        "progress": progress,
        "details": details,
        "tasks": tasks
    }


@router.post("/sync/{execution_id}")
async def sync_execution(
    execution_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sincroniza manualmente el estado de una ejecución desde Airflow"""
    execution = db.query(ETLExecution).filter(
        ETLExecution.id == execution_id
    ).first()
    
    if not execution:
        raise HTTPException(404, "Ejecución no encontrada")
    
    # Consultar estado en Airflow
    airflow_status = await airflow_client.get_dag_run_status(
        execution.dag_id,
        execution.dag_run_id
    )
    
    # Actualizar estado
    state_mapping = {
        "success": ExecutionState.SUCCESS,
        "failed": ExecutionState.FAILED,
        "running": ExecutionState.RUNNING,
        "queued": ExecutionState.QUEUED
    }
    
    new_state = state_mapping.get(airflow_status["state"])
    if new_state and new_state != execution.state:
        execution.state = new_state
        if new_state in [ExecutionState.SUCCESS, ExecutionState.FAILED]:
            execution.end_date = datetime.utcnow()
        db.commit()
    
    return {
        "execution_id": execution.id,
        "previous_state": execution.state.value,
        "current_state": new_state.value if new_state else "unknown",
        "synced": True
    }


@router.post("/callback/task")
async def task_callback(
    dag_id: str,
    dag_run_id: str,
    task_id: str,
    state: str,
    try_number: int = 1,
    log_message: str = None,
    db: Session = Depends(get_db)
):
    """Callback desde Airflow para actualizar estado de tareas"""
    # Buscar ejecución por dag_run_id
    execution = db.query(ETLExecution).filter(
        ETLExecution.dag_run_id == dag_run_id
    ).first()
    
    if not execution:
        raise HTTPException(404, f"Ejecución con dag_run_id={dag_run_id} no encontrada")
    
    # Buscar o crear task instance
    from app.models.etl import ETLTaskInstance, TaskState, ETLLog, LogLevel
    
    task_instance = db.query(ETLTaskInstance).filter(
        ETLTaskInstance.execution_id == execution.id,
        ETLTaskInstance.task_id == task_id
    ).first()
    
    if not task_instance:
        task_instance = ETLTaskInstance(
            execution_id=execution.id,
            task_id=task_id,
            state=TaskState(state.lower()),
            try_number=try_number,
            start_date=datetime.utcnow() if state.lower() == "running" else None
        )
        db.add(task_instance)
    else:
        task_instance.state = TaskState(state.lower())
        task_instance.try_number = try_number
        
        if state.lower() == "running" and not task_instance.start_date:
            task_instance.start_date = datetime.utcnow()
        elif state.lower() in ["success", "failed"]:
            task_instance.end_date = datetime.utcnow()
            if task_instance.start_date:
                task_instance.duration = int((task_instance.end_date - task_instance.start_date).total_seconds())
    
    # Registrar log si hay mensaje
    if log_message:
        log = ETLLog(
            task_instance_id=task_instance.id or task_instance,  # Puede no tener ID hasta commit
            log_timestamp=datetime.utcnow(),
            level=LogLevel.ERROR if state.lower() == "failed" else LogLevel.INFO,
            message=log_message
        )
        db.add(log)
    
    db.commit()
    
    return {"status": "ok", "message": "Task callback procesado"}


@router.post("/callback/dag")
async def dag_callback(
    dag_id: str,
    dag_run_id: str,
    state: str,
    db: Session = Depends(get_db)
):
    """Callback desde Airflow para actualizar estado del DAG completo"""
    # Buscar ejecución
    execution = db.query(ETLExecution).filter(
        ETLExecution.dag_run_id == dag_run_id
    ).first()
    
    if not execution:
        raise HTTPException(404, f"Ejecución con dag_run_id={dag_run_id} no encontrada")
    
    # Actualizar estado
    execution.state = ExecutionState(state.lower())
    
    if state.lower() == "running" and not execution.start_date:
        execution.start_date = datetime.utcnow()
    elif state.lower() in ["success", "failed"]:
        execution.end_date = datetime.utcnow()
    
    db.commit()
    
    return {"status": "ok", "message": "DAG callback procesado"}


@router.get("/logs/{execution_id}")
async def get_logs(
    execution_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene todos los logs de una ejecución ETL"""
    from app.models.etl import ETLLog, ETLTaskInstance
    
    # Verificar que la ejecución existe
    execution = db.query(ETLExecution).filter(
        ETLExecution.id == execution_id
    ).first()
    
    if not execution:
        raise HTTPException(404, "Ejecución no encontrada")
    
    # Obtener logs de todas las tareas de esta ejecución
    logs = db.query(ETLLog).join(ETLTaskInstance).filter(
        ETLTaskInstance.execution_id == execution_id
    ).order_by(ETLLog.log_timestamp.asc()).all()
    
    # Formatear respuesta
    formatted_logs = []
    for log in logs:
        formatted_logs.append({
            "task_id": log.task_instance.task_id,
            "timestamp": log.log_timestamp.isoformat(),
            "level": log.level.value,
            "message": log.message
        })
    
    return {"logs": formatted_logs}
