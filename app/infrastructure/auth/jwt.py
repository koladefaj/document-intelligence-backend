from datetime import datetime, timedelta

from fastapi import Depends
from jose import jwt
from app.infrastructure.config import settings

def create_access_token(user: str):
    expire = datetime.utcnow() + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {"sub": str(user.id), "email": user.email, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)

def create_refresh_token(user: str):
    expire = datetime.utcnow() + timedelta(
        minutes=settings.refresh_token_expire_days
    )

    payload = {"sub": str(user.id), "type": "refresh", "exp": expire}

    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)

