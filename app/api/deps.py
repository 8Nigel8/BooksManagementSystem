from fastapi import HTTPException, status, Header
from jose import JWTError
from app.core.security import decode_token
from app.reposytory.user_repository import UserRepositoryImpl

async def get_current_user(authorization: str | None = Header(None)):
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    repo = UserRepositoryImpl()
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
