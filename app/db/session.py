from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


def get_engine():
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


engine = get_engine()

AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
