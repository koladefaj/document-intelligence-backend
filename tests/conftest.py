import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.infrastructure.db.models import Base
from app.infrastructure.db.session import get_session


app.state.limiter_enabled = False


# 1. SETUP TEST DATABASE (In-Memory SQLite)
# 'sqlite+aiosqlite:///:memory:' is fast and doesn't touch your hard drive
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)

@pytest.fixture(scope="session", autouse=True)
def disable_limiter():
    # This disables slowapi globally for the test session
    app.state.limiter_enabled = False

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provides a clean database session for every test."""
    async with TestingSessionLocal() as session:
        yield session
        try:
            if session.is_active:
                await session.rollback()
        except Exception:
            pass

# 2. OVERRIDE FASTAPI DEPENDENCIES
@pytest.fixture(autouse=True)
def override_get_session(db_session):
    """Replaces the real DB session with the test session in FastAPI."""
    async def _get_test_session():
        yield db_session
    app.dependency_overrides[get_session] = _get_test_session

# 3. ASYNC HTTP CLIENT
@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """The 'browser' that will call your API routes."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost", headers={"Host": "localhost"}) as ac:
        yield ac