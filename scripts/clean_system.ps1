Write-Host "========================================" -ForegroundColor Cyan
Write-Host " CLEANING UP SYSTEM DATA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Clean Backend Tables (Audit Logs + ETL History)
Write-Host "Cleaning Backend Tables (sail_backend)..." -ForegroundColor Yellow
try {
    docker exec -i sail_backend_postgres psql -U sail_admin -d sail_backend -c "TRUNCATE TABLE audit_logs, etl_logs, etl_task_instances, etl_executions CASCADE;"
    if ($?) { Write-Host "OK" -ForegroundColor Green }
}
catch {
    Write-Host "Error cleaning backend tables" -ForegroundColor Red
}

# 2. Clean ETL Execution Logs (Airflow)
Write-Host "`nCleaning ETL Logs (Airflow)..." -ForegroundColor Yellow
try {
    docker exec -i sail-airflow-webserver-1 rm -rf /opt/airflow/logs/dag_id=*
    docker exec -i sail-airflow-webserver-1 rm -rf /opt/airflow/logs/scheduler/*
    if ($?) { Write-Host "OK" -ForegroundColor Green }
}
catch {
    Write-Host "Error cleaning ETL logs" -ForegroundColor Red
}

# 3. Clean ETL History (Airflow Database)
Write-Host "`nCleaning ETL History (Airflow DB)..." -ForegroundColor Yellow
try {
    docker exec -i sail-airflow-postgres-1 psql -U airflow -d airflow -c "DELETE FROM task_instance; DELETE FROM dag_run; DELETE FROM job; DELETE FROM log;"
    if ($?) { Write-Host "OK" -ForegroundColor Green }
}
catch {
    Write-Host "Error cleaning ETL history" -ForegroundColor Red
}

# 4. Clean DWH Fact Tables
Write-Host "`nCleaning DWH Fact Tables (dwh-rrhh)..." -ForegroundColor Yellow
try {
    # Note: Using CASCADE to ensure dependencies are handled if any
    docker exec -i dwh_rrhh_container psql -U postgres -d rrhh_prod -c "TRUNCATE TABLE dwh.fact_rotacion, dwh.fact_dotacion_snapshot, dwh.fact_seleccion, dwh.fact_asistencia, dwh.fact_realizacion_capacitacion, dwh.fact_participacion_capacitacion CASCADE;"
    if ($?) { Write-Host "OK" -ForegroundColor Green }
}
catch {
    Write-Host "Error cleaning DWH tables" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " SYSTEM CLEANUP COMPLETED" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
