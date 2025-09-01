from uuid import UUID

from pydantic import BaseModel, Field


class AuthorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class AuthorCreate(AuthorBase):

    class Config:
        from_attributes = True


class AuthorResponse(AuthorBase):
    id: UUID

    class Config:
        from_attributes = True
