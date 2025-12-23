import uuid
import logging
from fastapi import FastAPI, Request
from app.infrastructure.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
app = FastAPI(title="Document Intelligence Backend")

@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    return response

@app.get("/health", status_code=200)
def health_check(request: Request):
    logger.info(
        "Health check called",
        extra={"request_id": request.state.request_id}
    )
    return {"status": "ok"}