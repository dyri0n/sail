@router.get("/logs/{execution_id}")
async def get_logs(execution_id: str, db: Session = Depends(get_db)):
    logs = db.query(ETLLog).join(ETLTaskInstance).filter(
        ETLTaskInstance.execution_id == execution_id
    ).order_by(ETLLog.log_timestamp).all()
    
    return {
        "logs": [
            {
                "task_id": log.task_instance.task_id,
                "timestamp": log.log_timestamp.isoformat(),
                "level": log.log_level,
                "message": log.message
            }
            for log in logs
        ]
    }