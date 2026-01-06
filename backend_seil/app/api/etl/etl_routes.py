@router.post("/callback/task")
async def receive_task_callback(payload: dict, db: Session = Depends(get_db)):
    execution = db.query(ETLExecution).filter_by(
        dag_run_id=payload["dag_run_id"]
    ).first()
    
    if execution:
        task = ETLTaskInstance(
            execution_id=execution.id,
            task_id=payload["task_id"],
            state=payload["state"],
            operator=payload["operator"]
        )
        db.add(task)
        db.commit()
    
    return {"ok": True}
@router.post("/callback/dag")
async def receive_dag_callback(payload: dict, db: Session = Depends(get_db)):
    execution = db.query(ETLExecution).filter_by(
        dag_run_id=payload["dag_run_id"]
    ).first()
    
    if execution:
        execution.state = payload["state"]
        execution.end_date = payload["end_date"]
        db.commit()
    
    return {"ok": True}