from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from sqlalchemy import select

from app.infrastructure.config import settings
from app.infrastructure.db.session import get_session
from app.infrastructure.db.models import User

oauth2_scheme = HTTPBearer()

async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
) -> User:

    try:
        payload = jwt.decode(
            token.credentials,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        user_id: str = payload.get("sub")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
