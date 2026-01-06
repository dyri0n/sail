-- Migración: Sistema de Logs ETL
-- Fecha: 2026-01-06
-- Descripción: Crea tablas para tracking de ejecuciones ETL, tareas y logs

-- Tabla: etl_executions
CREATE TABLE IF NOT EXISTS etl_executions (
    id SERIAL PRIMARY KEY,
    dag_id VARCHAR(250) NOT NULL,
    dag_run_id VARCHAR(250) NOT NULL UNIQUE,
    execution_date TIMESTAMP,
    triggered_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    state VARCHAR(20) NOT NULL DEFAULT 'queued',
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Índices para etl_executions
CREATE INDEX idx_etl_executions_dag_id ON etl_executions(dag_id);
CREATE INDEX idx_etl_executions_dag_run_id ON etl_executions(dag_run_id);
CREATE INDEX idx_etl_executions_state ON etl_executions(state);
CREATE INDEX idx_etl_executions_triggered_by ON etl_executions(triggered_by_user_id);

-- Tabla: etl_task_instances
CREATE TABLE IF NOT EXISTS etl_task_instances (
    id SERIAL PRIMARY KEY,
    execution_id INTEGER NOT NULL REFERENCES etl_executions(id) ON DELETE CASCADE,
    task_id VARCHAR(250) NOT NULL,
    state VARCHAR(20) NOT NULL DEFAULT 'queued',
    try_number INTEGER NOT NULL DEFAULT 1,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    duration INTEGER  -- en segundos
);

-- Índices para etl_task_instances
CREATE INDEX idx_etl_task_instances_execution_id ON etl_task_instances(execution_id);
CREATE INDEX idx_etl_task_instances_task_id ON etl_task_instances(task_id);
CREATE INDEX idx_etl_task_instances_state ON etl_task_instances(state);

-- Tabla: etl_logs
CREATE TABLE IF NOT EXISTS etl_logs (
    id SERIAL PRIMARY KEY,
    task_instance_id INTEGER NOT NULL REFERENCES etl_task_instances(id) ON DELETE CASCADE,
    log_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    level VARCHAR(20) NOT NULL DEFAULT 'INFO',
    message TEXT NOT NULL
);

-- Índices para etl_logs
CREATE INDEX idx_etl_logs_task_instance_id ON etl_logs(task_instance_id);
CREATE INDEX idx_etl_logs_timestamp ON etl_logs(log_timestamp);
CREATE INDEX idx_etl_logs_level ON etl_logs(level);

-- Trigger para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_etl_execution_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_etl_execution_timestamp
    BEFORE UPDATE ON etl_executions
    FOR EACH ROW
    EXECUTE FUNCTION update_etl_execution_timestamp();

-- Comentarios en tablas
COMMENT ON TABLE etl_executions IS 'Registra ejecuciones de DAGs de Airflow';
COMMENT ON TABLE etl_task_instances IS 'Registra instancias de tareas dentro de cada ejecución ETL';
COMMENT ON TABLE etl_logs IS 'Registra logs individuales por tarea ETL';
