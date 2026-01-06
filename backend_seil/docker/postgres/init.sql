CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) NOT NULL,
    department VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Usuario admin inicial (password: admin123)
-- Hash generado con bcrypt 3.2.0: $2b$12$2dfgIoCqNYpwNRw3sX8iB.sJnM1q4Xt8j3adPHmxTqnmbTfptxalW
INSERT INTO users (name, email, username, password_hash, role)
VALUES (
    'Administrador',
    'admin@sail.cl',
    'admin',
    '$2b$12$2dfgIoCqNYpwNRw3sX8iB.sJnM1q4Xt8j3adPHmxTqnmbTfptxalW',
    'ADMIN'
);

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    username VARCHAR(100),
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(255),
    ip_address VARCHAR(45),
    level VARCHAR(20) DEFAULT 'INFO',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata_json JSONB
);

CREATE TABLE etl_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dag_id VARCHAR(100) NOT NULL,
    dag_run_id VARCHAR(250) NOT NULL UNIQUE,
    execution_date TIMESTAMP NOT NULL,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    state VARCHAR(50),
    triggered_by_user_id UUID REFERENCES users(id),
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);
CREATE TABLE etl_task_instances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id UUID REFERENCES etl_executions(id) ON DELETE CASCADE,
    task_id VARCHAR(250) NOT NULL,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    state VARCHAR(50),
    operator VARCHAR(100)
);
CREATE TABLE etl_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_instance_id UUID REFERENCES etl_task_instances(id) ON DELETE CASCADE,
    log_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    log_level VARCHAR(20),
    message TEXT NOT NULL,
    extra_data JSONB
);
CREATE INDEX idx_etl_executions_dag_id ON etl_executions(dag_id);
CREATE INDEX idx_etl_logs_timestamp ON etl_logs(log_timestamp DESC);