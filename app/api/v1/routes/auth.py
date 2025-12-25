from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.v1.schemas import RegisterRequest, LoginRequest
from app.infrastructure.db.session import get_session
from app.application.use_case.auth import register_user as register_uc, login as login_uc
from app.domain.exceptions import AuthenticationFailed
from starlette import status


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user_route(
        body: RegisterRequest,
        session: AsyncSession = Depends(get_session),
):
    try:
        user = await register_uc(session=session, email=body.email, password=body.password)
        return {"id": str(user.id), "email": user.email, "role": user.role}
    except AuthenticationFailed as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user_route(
        body: LoginRequest,
        session: AsyncSession = Depends(get_session),
):
    try:
        tokens = await login_uc(email=body.email, password=body.password, session=session)
        return tokens
    except AuthenticationFailed as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))