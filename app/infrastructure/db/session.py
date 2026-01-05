import logging
import os
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Initialize logger for async database events
logger = logging.getLogger(__name__)


# --- 1. ASYNC ENGINE CONFIGURATION ---
# Dev Note: This uses 'database_url' (which should start with postgresql+asyncpg://)
# echo=True is helpful in development to see the SQL being generated in your Docker logs.

db_url = os.getenv("DATABASE_URL")
aysnc_db = db_url.replace('postgresql://', 'postgresql+asyncpg://')

engine = create_async_engine(
    aysnc_db,
    echo=False,  # Set to True for SQL debugging
    pool_pre_ping=True,  # Vital for Docker container stability
)

# --- 2. ASYNC SESSION FACTORY ---
# expire_on_commit=False is crucial for FastAPI. 
# It prevents SQLAlchemy from trying to re-fetch data after a commit, 
# which would fail in an async environment.
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# --- 3. DEPENDENCY INJECTION ---
async def get_session() -> AsyncSession:
    """
    FastAPI Dependency that provides an asynchronous database session.
    
    Workflow:
    1. Opens a connection from the pool.
    2. Yields the session to the path operation function.
    3. Automatically closes the session when the request is finished.
    """
    async with AsyncSessionLocal() as session:
        try:
            logger.debug("Database: New async session yielded for API request.")
            yield session
        except Exception as e:
            logger.error(f"Database: Async session error: {e}")
            await session.rollback()
            raise
        finally:
            # Closing the session returns the connection to the engine pool
            await session.close()