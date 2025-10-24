from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.entry import Entry
from app.schemas.entry import EntryCreate, EntryOut, EntryUpdate
from app.services.security import get_current_active_superuser

router = APIRouter(prefix="/admin/entries", tags=["admin:entries"])


@router.get("/", response_model=list[EntryOut])
async def list_entries(
    session: AsyncSession = Depends(get_session),
    _: None = Depends(get_current_active_superuser),
) -> list[EntryOut]:
    result = await session.execute(select(Entry).order_by(Entry.created_at.desc()))
    entries = result.scalars().all()
    return entries


@router.post("/", response_model=EntryOut, status_code=status.HTTP_201_CREATED)
async def create_entry(
    data: EntryCreate,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_superuser),
) -> EntryOut:
    entry = Entry(**data.dict())
    entry.author_id = current_user.id
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry


@router.put("/{entry_id}", response_model=EntryOut)
async def update_entry(
    entry_id: uuid.UUID,
    data: EntryUpdate,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_superuser),
) -> EntryOut:
    result = await session.execute(select(Entry).where(Entry.id == entry_id))
    entry = result.scalars().first()
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(entry, key, value)

    entry.author_id = current_user.id

    await session.commit()
    await session.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(
    entry_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(get_current_active_superuser),
) -> None:
    result = await session.execute(select(Entry).where(Entry.id == entry_id))
    entry = result.scalars().first()
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")

    await session.delete(entry)
    await session.commit()
    return None
