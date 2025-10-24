from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


def get_engine():
    if settings.database_url is None:
        raise RuntimeError("Database URL is not configured")
    connect_args: dict[str, object] | None = None
    if settings.database_url.startswith("postgresql+asyncpg"):
        import ssl

        ssl_context = ssl.create_default_context()
        connect_args = {"ssl": ssl_context}

    return create_async_engine(
        settings.database_url,
        future=True,
        echo=False,
        connect_args=connect_args,
    )


try:
    engine = get_engine()
except RuntimeError:
    engine = None
    AsyncSessionLocal: sessionmaker | None = None
else:
    AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    if AsyncSessionLocal is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not configured")
    async with AsyncSessionLocal() as session:
        yield session
