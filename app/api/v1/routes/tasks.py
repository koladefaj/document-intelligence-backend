from fastapi import APIRouter, Depends
from app.application.use_case.get_task_status import get_task_status
from app.dependencies import get_task_queue

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/{task_id}")
def task_status(task_id: str, queue=Depends(get_task_queue)):
    response = get_task_status(task_id, queue=queue)
    return response
