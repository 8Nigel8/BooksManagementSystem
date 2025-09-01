from uuid import UUID

from pydantic import BaseModel, Field, field_validator, ValidationError
from datetime import datetime

from app.schemas.author import AuthorCreate
from app.schemas.enums import GenreEnum


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    published_year: int = Field(..., ge=1800, le=datetime.now().year)
    genres: list[GenreEnum] = Field()

    @field_validator("genres", mode="before")
    def validate_genres(cls, v):
        if not v:
            raise ValidationError("Genres cannot be empty")
        if isinstance(v, list):
            return [GenreEnum(item) if isinstance(item, str) else item for item in v]
        return v


class BookCreate(BookBase):
    author: AuthorCreate


class BookUpdate(BaseModel):
    id: UUID = Field(...)
    title: str | None = Field(None, min_length=1, max_length=255)
    author: AuthorCreate | None = Field(None, min_length=1, max_length=255)
    published_year: int | None = Field(None, ge=1800, le=datetime.now().year)
    genres: list[GenreEnum] | None = Field(None)

    @field_validator("genres", mode="before")
    def validate_genres(cls, v):
        if v is not None and len(v) == 0:
            raise ValidationError("Genres cannot be empty")
        if isinstance(v, list):
            return [GenreEnum(item) if isinstance(item, str) else item for item in v]
        return v


class BookResponse(BookBase):
    id: UUID
    author_id: UUID | None

    class Config:
        from_attributes = True
