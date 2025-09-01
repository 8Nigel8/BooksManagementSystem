from fastapi import APIRouter, status

from app.registry import Registry
from app.schemas.auth import UserCreate, UserResponse, Token
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate):
    auth_service = Registry.get(AuthService)
    created = await auth_service.register(user_in)
    return created

@router.post("/auth/login", response_model=Token)
async def login(user_in: UserCreate):
    auth_service = Registry.get(AuthService)
    token = await auth_service.login(user_in)
    return token

@router.post("/auth/refresh", response_model=Token)
async def refresh(refresh_token: str):
    auth_service = Registry.get(AuthService)
    token = await   auth_service.refresh(refresh_token)
    return token

@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(refresh_token: str):
    auth_service = Registry.get(AuthService)
    await auth_service.logout(refresh_token)
    return None
