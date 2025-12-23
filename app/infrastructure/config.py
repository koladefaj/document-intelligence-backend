from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    app_env: str = Field(default="local")
    app_name: str = Field(default="document-intelligence-backend")

    database_url: str
    database_sync_url: str
    database_username: str
    database_password: str
    redis_url: str

    secret_key: str
    access_token_expire_minutes: int = 20
    refresh_token_expire_days: int = 7

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()