from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.infrastructure.db.models import User
from app.infrastructure.auth.password import hash_password, verify_password
from app.infrastructure.auth.jwt import create_refresh_token, create_access_token
from app.domain.exceptions import AuthenticationFailed

async def register_user(session: AsyncSession, email: str, password: str) -> User:
    result = await session.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise AuthenticationFailed("User already exists")
    user = User(email=email, hashed_password=hash_password(password))
    session.add(user)
    await session.commit()
    return user

async def login(
        session: AsyncSession,
        email: str,
        password: str,
) -> dict:
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise AuthenticationFailed("Invalid password or Username")

    return {
        "access_token": create_access_token(user),
        "refresh_token": create_refresh_token(user),
    }