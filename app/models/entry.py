from __future__ import annotations

import enum
import uuid

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class EntryCategory(str, enum.Enum):
    doctrine = "doctrine"
    creed = "creed"
    ritual = "ritual"
    prayer = "prayer"
    event = "event"
    testimony = "testimony"
    other = "other"


class Entry(Base):
    __tablename__ = "entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(String(160), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    subtitle = Column(String(280))
    category = Column(Enum(EntryCategory, name="entry_category"), nullable=False)
    summary = Column(Text)
    content_html = Column(Text, nullable=False)
    content_markdown = Column(Text)
    is_published = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    published_at = Column(DateTime(timezone=True))

    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    author = relationship("User", back_populates="entries")
