from fastapi import APIRouter
from app.infrastructure.queue.celery_app import celery_app

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/{task_id}")
def get_task_status(task_id: str):
    result = celery_app.AsyncResult(task_id, app=celery_app)
    response = {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.successful() else None,
        "is_completed": result.successful(),
        "is_failed": result.failed(),
        "is_pending": result.status in ["PENDING", "STARTED"]

    }

    return response
