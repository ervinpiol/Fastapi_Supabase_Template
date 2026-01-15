import logging
from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.base import Base

logger = logging.getLogger(__name__)


# ===== Synchronous Database =====
sync_engine = create_engine(
    settings.DATABASE_URI,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    echo=settings.ENVIRONMENT == "local",
)

SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)


def get_db() -> Generator[Session, None, None]:
    """Dependency for synchronous database sessions."""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ===== Async Database =====
async_engine: AsyncEngine = create_async_engine(
    settings.ASYNC_DATABASE_URI,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    echo=settings.ENVIRONMENT == "local",
)

AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for async database sessions."""
    async with AsyncSessionLocal() as session:
        yield session


async def warm_up_connections(num_connections: int = 10) -> None:
    """Warm up database connection pool on startup."""
    logger.info(f"Warming up {num_connections} database connections...")

    connections = []
    for _ in range(num_connections):
        conn = await async_engine.connect()
        connections.append(conn)

    for conn in connections:
        await conn.execute(text("SELECT 1"))

    for conn in connections:
        await conn.close()

    logger.info(f"Successfully warmed up {num_connections} connections")


def init_db() -> None:
    """Initialize database (create tables if needed). Use Alembic in production."""
    Base.metadata.create_all(bind=sync_engine)