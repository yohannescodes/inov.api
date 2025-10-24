from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.entry import EntryCategory


class EntryBase(BaseModel):
    title: str
    subtitle: str | None = None
    slug: str
    category: EntryCategory
    summary: str | None = None
    content_html: str
    content_markdown: str | None = None
    is_published: bool = False
    published_at: datetime | None = None


class EntryCreate(EntryBase):
    pass


class EntryUpdate(BaseModel):
    title: str | None = None
    subtitle: str | None = None
    slug: str | None = None
    category: EntryCategory | None = None
    summary: str | None = None
    content_html: str | None = None
    content_markdown: str | None = None
    is_published: bool | None = None
    published_at: datetime | None = None


class EntryPublicResponse(BaseModel):
    id: str | None = None
    title: str
    subtitle: str | None = None
    slug: str
    category: str | None = None
    summary: str | None = None
    content_html: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    published_at: datetime | None = None

    class Config:
        allow_population_by_field_name = True


class EntryOut(EntryBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    author_id: uuid.UUID | None = Field(default=None, alias="authorId")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
