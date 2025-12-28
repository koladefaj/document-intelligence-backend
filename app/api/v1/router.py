from fastapi import APIRouter
from app.api.v1.routes import auth, documents, tasks

router = APIRouter()

router.include_router(auth.router)

router.include_router(tasks.router)
router.include_router(documents.router)