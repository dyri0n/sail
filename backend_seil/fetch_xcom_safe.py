#!/usr/bin/env python
"""
Script seguro para obtener XComs en Airflow 3.X
Uso: python fetch_xcom_safe.py <dag_id> <run_id> <task_id> [<key>]
"""

import sys
import json
from airflow import settings
from airflow.models import XCom

def get_xcom_value(dag_id, run_id, task_id, key='return_value'):
    """Obtiene el valor XCom usando la sesión de Airflow"""
    try:
        # Usar la sesión de Airflow
        session = settings.Session()
        
        # Consultar el XCom
        xcom = session.query(XCom).filter(
            XCom.dag_id == dag_id,
            XCom.run_id == run_id,
            XCom.task_id == task_id,
            XCom.key == key
        ).order_by(XCom.timestamp.desc()).first()
        
        if xcom:
            value = xcom.value
            
            # Si el valor es string, intentar parsear como JSON
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except:
                    return value
            return value
        return None
        
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        return None
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python fetch_xcom_safe.py <dag_id> <run_id> <task_id> [<key>]")
        sys.exit(1)
    
    dag_id = sys.argv[1]
    run_id = sys.argv[2]
    task_id = sys.argv[3]
    key = sys.argv[4] if len(sys.argv) > 4 else 'return_value'
    
    result = get_xcom_value(dag_id, run_id, task_id, key)
    
    # Imprimir resultado como JSON o None
    if result is None:
        print("null")
    else:
        try:
            print(json.dumps(result))
        except:
            print(json.dumps(str(result)))