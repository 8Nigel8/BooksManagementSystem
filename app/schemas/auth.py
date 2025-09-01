from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=150)
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: str
    username: str
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str
    exp: int
