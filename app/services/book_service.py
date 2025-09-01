from abc import ABC
from uuid import UUID
import pandas as pd

from app.exceptions.book_not_found import BookNotFound
from app.reposytory.book_repository import BookRepository
from app.reposytory.author_repository import AuthorRepository
from app.schemas.author import AuthorCreate
from app.schemas.book import BookCreate, BookResponse, BookUpdate


class BookService(ABC):
    async def find_book(self, book_id: UUID) -> BookResponse:
        raise NotImplementedError()

    async def create_book(self, book: BookCreate) -> BookResponse:
        raise NotImplementedError()

    async def delete_book(self, book_id: UUID) -> BookResponse:
        raise NotImplementedError()

    async def update_book(self, book: BookUpdate) -> BookResponse:
        raise NotImplementedError()

    async def get_all_books(
            self,
            skip: int = 0,
            limit: int = 100,
            title: str | None = None,
            author: str | None = None,
            genre: str | None = None,
            year_from: int | None = None,
            year_to: int | None = None,
            sort_by: str = "title",
            sort_order: str = "asc",
    ) -> list[BookResponse]:
        raise NotImplementedError()

    async def import_books_from_csv(self, file) -> dict:
        raise NotImplementedError()


class BookServiceImpl(BookService):
    def __init__(self, book_repo: BookRepository, author_repo: AuthorRepository):
        self._book_repo = book_repo
        self._author_repo = author_repo

    async def import_books_from_csv(self, file) -> dict:
        try:
            df = pd.read_csv(file.file)
        except Exception as e:
            raise ValueError(f"Error reading CSV: {e}")

        required_columns = {"title", "published_year", "author_name", "genres"}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"CSV must contain columns: {', '.join(required_columns)}")

        imported_books = []
        failed_rows = []

        for idx, row in df.iterrows():
            try:
                genres_list = [g.strip() for g in str(row["genres"]).split(",")]

                book_create = BookCreate(
                    title=row["title"],
                    published_year=int(row["published_year"]),
                    genres=genres_list,
                    author=AuthorCreate(name=row["author_name"]),
                )

                book = await self._book_repo.create_book(book_create)
                imported_books.append(book)
            except Exception as e:
                failed_rows.append({"row": idx + 1, "error": str(e)})

        return {
            "imported_count": len(imported_books),
            "failed_count": len(failed_rows),
            "failed_rows": failed_rows,
            "books": imported_books
        }

    async def find_book(self, book_id: UUID) -> BookResponse:
        book = await self._book_repo.get_book(book_id)
        if book is None:
            raise BookNotFound(book_id)
        return book

    async def create_book(self, book_data: BookCreate) -> BookResponse:
        return await self._book_repo.create_book(book_data)

    async def update_book(self, book: BookUpdate) -> BookResponse:
        return await self._book_repo.update_book(book)

    async def delete_book(self, book_id: UUID) -> BookResponse:
        deleted_book = await self._book_repo.delete_book(book_id)

        author_books = await self._book_repo.get_books_by_author(deleted_book.author_id)
        if len(author_books) == 0:
            await self._author_repo.delete_author(deleted_book.author_id)

        return deleted_book

    async def get_all_books(
            self,
            skip: int = 0,
            limit: int = 100,
            title: str | None = None,
            author: str | None = None,
            genre: str | None = None,
            year_from: int | None = None,
            year_to: int | None = None,
            sort_by: str = "title",
            sort_order: str = "asc",
    ) -> list[BookResponse]:
        return await self._book_repo.get_all_books(
            skip=skip,
            limit=limit,
            title=title,
            author=author,
            genre=genre,
            year_from=year_from,
            year_to=year_to,
            sort_by=sort_by,
            sort_order=sort_order,
        )
