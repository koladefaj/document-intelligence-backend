import uuid
import logging
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from app.api.v1.websocket_manager import manager
from app.infrastructure.logging import setup_logging, request_id_var
from app.api.v1.router import router as v1_router

# Logging setup
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Document Intelligence Backend")

# Include your routes
app.include_router(v1_router, prefix="/api/v1")

@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    # This UUID will follow the request through every log entry
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    request_id_var.set(request_id)

    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    return response

@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """
    The frontend connects here using the task_id returned 
    when they uploaded the Telco Churn PDF.
    """
    await manager.connect(task_id, websocket)
    try:
        # We keep the connection open while the worker 
        # is busy summarizing the document via Gemini.
        while True:
            # We wait for data, but primarily this loop keeps 
            # the socket alive for the manager to push data TO it.
            await websocket.receive_text()
    except WebSocketDisconnect:
        # Clean up connection if user closes the tab
        manager.disconnect(task_id)

@app.get("/", status_code=200)
def health_check(request: Request):
    logger.info("Health check called", extra={"request_id": request.state.request_id})
    return {"status": "ok", "message": "Document Intelligence API is running"}