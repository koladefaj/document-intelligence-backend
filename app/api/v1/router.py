from fastapi import APIRouter
from app.api.v1.routes import auth
from app.api.v1.routes import documents
from app.infrastructure.auth.dependencies import get_current_user

router = APIRouter()

router.include_router(auth.router)
router.include_router(documents.router)