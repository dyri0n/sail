const API = 'http://localhost:8000/api/v1/etl';

// =========== INTERFACES ===========
export interface ETLExecution {
    id: string;
    dag_id: string;
    dag_run_id: string;
    execution_date: string;
    start_date?: string;
    end_date?: string;
    state: string;
    triggered_at: string;
    triggered_by_user_id?: string;
}

export interface HistoryResponse {
    history: ETLExecution[];
    recent_logs?: LogEntry[];
}

export interface LogEntry {
    timestamp: string;
    level: string;
    message: string;
    task_id?: string;
}

export interface TriggerResponse {
    execution_id: string;
    status: string;
}

export interface StatusResponse {
    execution_id: string;
    state: string;
    start_date?: string;
    end_date?: string;
    progress?: number;
}

// =========== FUNCIONES ===========
export async function triggerETL(dagId: string, token: string): Promise<TriggerResponse> {
    const res = await fetch(`${API}/trigger?dag_id=${dagId}`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    });

    if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Error ${res.status}: ${errorText}`);
    }

    return res.json();
}

export async function getHistory(token: string): Promise<HistoryResponse> {
    const res = await fetch(`${API}/history`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });

    if (!res.ok) {
        const errorText = await res.text();
    }

    return res.json();
}

export async function getExecutionStatus(executionId: string, token: string): Promise<StatusResponse> {
    const res = await fetch(`${API}/status/${executionId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });

    if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Error ${res.status}: ${errorText}`);
    }

    return res.json();
}