from datetime import datetime, timedelta
from jose import jwt
from app.infrastructure.config import settings

ALGORITHM = "HS256"

def create_access_token(user: str):
    expire = datetime.utcnow() + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {"sub": str(user.id), "email": user.email, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)

def create_refresh_token(user: str):
    expire = datetime.utcnow() + timedelta(
        minutes=settings.refresh_token_expire_days
    )

    payload = {"sub": str(user.id), "type": "refresh", "exp": expire}

    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)