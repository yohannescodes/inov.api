from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.entry import EntryPublicResponse
from app.services.sanity import fetch_entries, fetch_entry_by_slug

router = APIRouter(prefix="/entries", tags=["public:entries"])


@router.get("/", response_model=list[EntryPublicResponse])
async def list_published_entries(
    category: str | None = Query(default=None, description="Filter by category slug"),
) -> list[EntryPublicResponse]:
    entries = await fetch_entries(category=category)
    return [EntryPublicResponse(**entry) for entry in entries]


@router.get("/{slug}", response_model=EntryPublicResponse)
async def read_entry_by_slug(slug: str) -> EntryPublicResponse:
    entry = await fetch_entry_by_slug(slug)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")
    return EntryPublicResponse(**entry)
