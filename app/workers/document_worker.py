from app.infrastructure.queue.celery_app import celery_app
import time
import multiprocessing

multiprocessing.set_start_method('spawn', force=True)

@celery_app.task(bind=True, name="process_document")
def process_document_task(self, document_id: str):
    stages = ["received", "reading file", "extracting", "saving metadata", "completed"]

    for stage in stages:
        self.update_state(state="PROCESSING", meta={"stage": stage})
        time.sleep(2)
    return {"message": "Document Processed succesfully", "document_id": document_id}