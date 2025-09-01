from abc import ABC
from datetime import datetime, timedelta
from app.core.security import create_access_token, create_refresh_token, verify_password, decode_token
from app.reposytory.user_repository import UserRepository
from app.schemas.auth import UserCreate, Token
from app.core.config import settings


class AuthService(ABC):
    async def register(self, user_in: UserCreate):
        raise NotImplementedError()

    async def login(self, user_in: UserCreate) -> Token:
        raise NotImplementedError()

    async def refresh(self, refresh_token: str) -> Token:
        raise NotImplementedError()

    async def logout(self, refresh_token: str):
        raise NotImplementedError()


class AuthServiceImpl(AuthService):
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, user_in: UserCreate):
        existing = await self.user_repo.get_by_username(user_in.username)
        if existing:
            raise ValueError("username already exists")
        return await self.user_repo.create_user(user_in)

    async def login(self, user_in: UserCreate) -> Token:
        user_row = await self.user_repo.get_by_username(user_in.username)
        if not user_row:
            raise ValueError("invalid credentials")
        if not verify_password(user_in.password, user_row["password_hash"]):
            raise ValueError("invalid credentials")

        user_id = user_row["id"]
        access = create_access_token(user_id, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        refresh = create_refresh_token(user_id, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.user_repo.add_refresh_token(user_id, refresh, expires_at)
        return Token(access_token=access, refresh_token=refresh)

    async def refresh(self, refresh_token: str) -> Token:
        db_row = await self.user_repo.get_refresh_token(refresh_token)
        if not db_row:
            raise ValueError("invalid refresh token")
        payload = decode_token(refresh_token)
        user_id = payload.get("sub")
        access = create_access_token(user_id, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        new_refresh = create_refresh_token(user_id, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.user_repo.revoke_refresh_token(refresh_token)
        await self.user_repo.add_refresh_token(user_id, new_refresh, expires_at)
        return Token(access_token=access, refresh_token=new_refresh)

    async def logout(self, refresh_token: str):
        await self.user_repo.revoke_refresh_token(refresh_token)
