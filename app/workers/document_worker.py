from app.infrastructure.queue.celery_app import celery_app
from app.dependencies import get_document_processor
from app.infrastructure.db.session_sync import get_db_sync
from app.infrastructure.db.models import Document
from app.dependencies import get_storage_service
from app.infrastructure.config import settings
import multiprocessing
import json
from app.infrastructure.config import settings
import redis

# Initialize Redis client for the notification bridge
# Host 'redis' matches your docker-compose service name
redis_client = redis.from_url(settings.redis_url)

multiprocessing.set_start_method('spawn', force=True)
processor = get_document_processor()
storage_service = get_storage_service()

@celery_app.task(bind=True, name="process_document_task")
def process_document_task(self, document_id: str):
    """Background Processing of uploaded file with Real-time Notification"""
    db = get_db_sync()
    task_id = self.request.id # This is the ID the WebSocket is listening to
    doc = None

    try:
        doc = db.query(Document).filter(Document.id == document_id).first()

        if not doc:
            return {"error": "Document not found"}

        # 1. RUN AI PROCESSOR (PDF Extraction -> Gemini Summary)
        result = processor.process(doc.local_path)

        # 2. SAVE TO DATABASE
        doc.raw_text = result["raw_text"]
        doc.analysis = json.dumps(result["analysis"])
        doc.status = "COMPLETED"
        db.commit()

        # 3. PUSH REAL-TIME NOTIFICATION
        # We publish to a unique channel for this specific task
        notification_payload = {
            "task_id": task_id,
            "document_id": document_id,
            "status": "COMPLETED",
            "analysis": result["analysis"]
        }
        
        redis_client.publish(
            f"notifications_{task_id}", 
            json.dumps(notification_payload)
        )

        return {"document_id": document_id, "status": "COMPLETED"}

    except Exception as e:
        # Handle failures by updating status and notifying the UI
        if doc:
            doc.status = "FAILED"
            db.commit()
        
        error_payload = {"task_id": task_id, "status": "FAILED", "error": str(e)}
        redis_client.publish(f"notifications_{task_id}", json.dumps(error_payload))
        raise e
    
    finally:
        db.close()