from uuid import UUID

from fastapi import APIRouter, Query, status, Depends, UploadFile, File, HTTPException
from typing import List
from datetime import datetime

from app.api.deps import get_current_user
from app.registry import Registry
from app.schemas.book import BookCreate, BookUpdate, BookResponse
from app.services.book_service import BookService

router = APIRouter()

@router.post("/books/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    data: BookCreate,
    user=Depends(get_current_user),
):
    """
    Create a new book. If the author does not exist, it will be created.
    """
    book_service = Registry.get(BookService)
    created_book = await book_service.create_book(data)
    return created_book


@router.get("/books/", response_model=List[BookResponse])
async def get_books(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    title: str | None = Query(None, description="Filter by title (case-insensitive)"),
    author: str | None = Query(None, description="Filter by author name"),
    genre: str | None = Query(None, description="Filter by genre"),
    year_from: int | None = Query(None, ge=1800, le=datetime.now().year, description="Filter by minimum published year"),
    year_to: int | None = Query(None, ge=1800, le=datetime.now().year, description="Filter by maximum published year"),
    sort_by: str = Query("title", description="Field to sort by (title, author, published_year)"),
    sort_order: str = Query("asc", description="Sort order (asc or desc)"),
):
    """
    Retrieve books with optional filtering, pagination, and sorting.
    """
    book_service = Registry.get(BookService)
    books = await book_service.get_all_books(
        skip=skip,
        limit=limit,
        title=title,
        author=author,
        genre=genre,
        year_from=year_from,
        year_to=year_to,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return books


@router.get("/books/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: UUID,
):
    """
    Retrieve a specific book by its ID.
    """
    book_service = Registry.get(BookService)
    book = await book_service.find_book(book_id)
    return book


@router.put("/books/{book_id}", response_model=BookResponse)
async def update_book(
    data: BookUpdate,
    user=Depends(get_current_user),
):
    """
    Update a book's details. If the author does not exist, it will be created.
    """
    book_service = Registry.get(BookService)
    updated_book = await book_service.update_book(data)
    return updated_book


@router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: UUID,
    user=Depends(get_current_user),
):
    """
    Delete a book. If it was the last book of an author, the author will also be deleted.
    """
    book_service = Registry.get(BookService)
    await book_service.delete_book(book_id)
    return None


@router.post("/import-csv")
async def import_books_csv(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
):
    """
    Import books from a CSV file.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be CSV")

    book_service = Registry.get(BookService)
    imported_books = await book_service.import_books_from_csv(file)
    return {"imported": len(imported_books), "books": imported_books}