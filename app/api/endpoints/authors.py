from uuid import UUID

from fastapi import APIRouter
from typing import List

from app.registry import Registry
from app.reposytory.author_repository import AuthorRepository
from app.schemas.author import AuthorResponse

router = APIRouter()

@router.get("/authors/", response_model=List[AuthorResponse])
async def get_authors() -> List[AuthorResponse]:
    """
    Retrieve all authors.
    """
    author_repo = Registry.get(AuthorRepository)
    authors = await author_repo.get_all_authors()
    return authors


@router.get("/authors/{author_id}", response_model=AuthorResponse)
async def get_author(
    author_id: UUID,
):
    """
    Retrieve a specific author by its ID.
    """
    author_repo = Registry.get(AuthorRepository)
    author = await author_repo.get_author(author_id)
    return author

