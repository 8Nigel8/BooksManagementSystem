# app/reposytory/user_repository.py
from abc import ABC
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import UserCreate, UserResponse
from app.core.security import hash_password

class UserRepository(ABC):
    async def create_user(self, user: UserCreate) -> UserResponse:
        raise NotImplementedError()

    async def get_by_username(self, username: str) -> dict | None:
        raise NotImplementedError()

    async def get_by_id(self, user_id: str) -> UserResponse | None:
        raise NotImplementedError()

    async def add_refresh_token(self, user_id: str, token: str, expires_at: datetime):
        raise NotImplementedError()

    async def revoke_refresh_token(self, token: str):
        raise NotImplementedError()

    async def get_refresh_token(self, token: str):
        raise NotImplementedError()

class UserRepositoryImpl(UserRepository):
    async def create_user(self, user: UserCreate) -> UserResponse:
        async with get_db() as session:  # AsyncSession
            pwd = hash_password(user.password)
            new_id = str(uuid.uuid4())
            q = text("""
                INSERT INTO users (id, username, password_hash)
                VALUES (:id, :username, :pwd)
                RETURNING id, username, is_active
            """)
            result = await session.execute(q, {"id": new_id, "username": user.username, "pwd": pwd})
            await session.commit()
            row = result.mappings().first()
            return UserResponse(
                id=str(row["id"]),
                username=row["username"],
                is_active=row["is_active"],
            )

    async def get_by_username(self, username: str) -> dict | None:
        async with get_db() as session:
            q = text("SELECT id, username, password_hash, is_active FROM users WHERE username = :username")
            result = await session.execute(q, {"username": username})
            row = result.mappings().first()
            if not row:
                return None
            return {
                "id": str(row["id"]),
                "username": row["username"],
                "password_hash": row["password_hash"],
                "is_active": row["is_active"],
            }

    async def get_by_id(self, user_id: str) -> UserResponse | None:
        async with get_db() as session:
            q = text("SELECT id, username, is_active FROM users WHERE id = :id")
            result = await session.execute(q, {"id": user_id})
            row = result.mappings().first()
            if not row:
                return None
            return UserResponse(
                id=str(row["id"]),
                username=row["username"],
                is_active=row["is_active"],
            )

    async def add_refresh_token(self, user_id: str, token: str, expires_at: datetime):
        async with get_db() as session:
            q = text("""
                INSERT INTO refresh_tokens (user_id, token, expires_at)
                VALUES (:user_id, :token, :expires_at)
                RETURNING id
            """)
            await session.execute(q, {"user_id": user_id, "token": token, "expires_at": expires_at})
            await session.commit()

    async def revoke_refresh_token(self, token: str):
        async with get_db() as session:
            q = text("DELETE FROM refresh_tokens WHERE token = :token")
            await session.execute(q, {"token": token})
            await session.commit()

    async def get_refresh_token(self, token: str):
        async with get_db() as session:
            q = text("SELECT id, user_id, token, expires_at FROM refresh_tokens WHERE token = :token")
            result = await session.execute(q, {"token": token})
            return result.mappings().first()
