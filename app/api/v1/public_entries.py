from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.entry import Entry, EntryCategory
from app.schemas.entry import EntryOut

router = APIRouter(prefix="/entries", tags=["public:entries"])


@router.get("/", response_model=list[EntryOut])
async def list_published_entries(
    category: EntryCategory | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> list[EntryOut]:
    query = select(Entry).where(Entry.is_published.is_(True)).order_by(Entry.published_at.desc())
    if category is not None:
        query = query.where(Entry.category == category)

    result = await session.execute(query)
    entries = result.scalars().all()
    return entries


@router.get("/{slug}", response_model=EntryOut)
async def fetch_entry_by_slug(
    slug: str,
    session: AsyncSession = Depends(get_session),
) -> EntryOut:
    query = select(Entry).where(Entry.slug == slug, Entry.is_published.is_(True))
    result = await session.execute(query)
    entry = result.scalars().first()
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")
    return entry
