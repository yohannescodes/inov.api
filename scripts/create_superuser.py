#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import uuid

from sqlalchemy import select

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.services.security import get_password_hash


async def create_superuser():
    email = input("Email: ").strip().lower()
    full_name = input("Full name (optional): ").strip() or None
    password = input("Password: ").strip()

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        existing = result.scalars().first()
        if existing:
            print("User already exists")
            return

        user = User(
            id=uuid.uuid4(),
            email=email,
            full_name=full_name,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=True,
        )
        session.add(user)
        await session.commit()
        print("Superuser created.")


if __name__ == "__main__":
    print(f"Using database: {settings.database_url}")
    asyncio.run(create_superuser())
