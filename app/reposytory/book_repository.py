import uuid
from abc import ABC
from uuid import UUID

from sqlalchemy import text

from app.db.session import get_db
from app.exceptions.not_found import BookNotFound
from app.reposytory.author_repository import AuthorRepository
from app.schemas.book import BookCreate, BookResponse, BookUpdate
from app.schemas.enums import GenreEnum


class BookRepository(ABC):
    async def get_book(self, book_id: UUID) -> BookResponse | None:
        raise NotImplementedError()

    async def create_book(self, book: BookCreate) -> BookResponse:
        raise NotImplementedError()

    async def update_book(self, book: BookUpdate) -> BookResponse | None:
        raise NotImplementedError()

    async def delete_book(self, book_id: UUID) -> BookResponse | None:
        raise NotImplementedError()

    async def get_all_books(
        self,
        skip: int,
        limit: int,
        title: str | None,
        author: str | None,
        genre: str | None,
        year_from: int | None,
        year_to: int | None,
        sort_by: str,
        sort_order: str,
    ) -> list[BookResponse]:
        raise NotImplementedError()

    async def get_books_by_author(self, author_id: UUID) -> list[BookResponse]:
        raise NotImplementedError()


class BookRepositoryImpl(BookRepository):
    def __init__(self, author_repo: AuthorRepository) -> None:
        self._author_repo = author_repo

    async def create_book(self, book_data: BookCreate) -> BookResponse:
        async with get_db() as session:  # AsyncSession
            author = await self._author_repo.get_author_by_name(book_data.author.name)
            if author is None:
                author = await self._author_repo.create_author(book_data.author)

            book_id = uuid.uuid4()
            query = text("""
                INSERT INTO books (id, title, published_year, author_id, genres)
                VALUES (:id, :title, :year, :author_id, :genres)
                RETURNING id, title, published_year, author_id, genres
            """)
            result = await session.execute(query, {
                "id": book_id,
                "title": book_data.title,
                "year": book_data.published_year,
                "author_id": author.id,
                "genres": [g.value for g in book_data.genres]
            })
            await session.commit()
            row = result.first()
            return BookResponse(
                id=row.id,
                title=row.title,
                published_year=row.published_year,
                author_id=row.author_id,
                genres=row.genres
            )

    async def get_book(self, book_id: UUID) -> BookResponse | None:
        async with get_db() as session:
            query = text("""
                SELECT id, title, published_year, author_id, genres
                FROM books WHERE id = :book_id
            """)
            result = await session.execute(query, {"book_id": book_id})
            row = result.first()
            if row:
                return BookResponse(
                    id=row.id,
                    title=row.title,
                    published_year=row.published_year,
                    author_id=row.author_id,
                    genres=row.genres
                )
            return None

    async def update_book(self, book_data: BookUpdate) -> BookResponse | None:
        old_book = await self.get_book(book_data.id)
        if not old_book:
            raise BookNotFound(book_id=book_data.id)

        async with get_db() as session:
            if book_data.author:
                author = await self._author_repo.create_author(book_data.author)
                author_id = author.id
            else:
                author_id = old_book.author_id

            query = text("""
                UPDATE books
                SET title = :title, published_year = :year, author_id = :author_id, genres = :genres
                WHERE id = :book_id
                RETURNING id, title, published_year, author_id, genres
            """)
            result = await session.execute(query, {
                "title": book_data.title or old_book.title,
                "year": book_data.published_year or old_book.published_year,
                "author_id": author_id,
                "genres": book_data.genres or old_book.genres,
                "book_id": book_data.id
            })
            await session.commit()
            row = result.first()
            if row:
                return BookResponse(
                    id=row.id,
                    title=row.title,
                    published_year=row.published_year,
                    author_id=row.author_id,
                    genres=row.genres
                )
            return None

    async def delete_book(self, book_id: UUID) -> BookResponse | None:
        book = await self.get_book(book_id)
        if book is None:
            raise BookNotFound(book_id)

        async with get_db() as session:
            query = text("""
                DELETE FROM books
                WHERE id = :book_id
                RETURNING id, title, published_year, author_id, genres
            """)
            result = await session.execute(query, {"book_id": book_id})
            await session.commit()
            row = result.first()
            if row:
                return BookResponse(
                    id=row.id,
                    title=row.title,
                    published_year=row.published_year,
                    author_id=row.author_id,
                    genres=row.genres
                )
            return None

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
        sort_order: str = "asc"
    ) -> list[BookResponse]:
        async with get_db() as session:
            query_text = """
                SELECT b.id, b.title, b.published_year, a.id AS author_id, a.name AS author_name, b.genres
                FROM books b
                JOIN authors a ON b.author_id = a.id
            """

            filters = []
            params = {}

            if title:
                filters.append("b.title ILIKE :title")
                params["title"] = f"%{title}%"
            if author:
                filters.append("a.name ILIKE :author")
                params["author"] = f"%{author}%"
            if genre:
                if genre not in [g.value for g in GenreEnum]:
                    raise ValueError(f"Invalid genre: {genre}")
                filters.append(":genre = ANY(b.genres)")
                params["genre"] = genre
            if year_from:
                filters.append("b.published_year >= :year_from")
                params["year_from"] = year_from
            if year_to:
                filters.append("b.published_year <= :year_to")
                params["year_to"] = year_to

            if filters:
                query_text += " WHERE " + " AND ".join(filters)

            if sort_by not in {"title", "author", "published_year"}:
                sort_by = "title"
            if sort_order.lower() not in {"asc", "desc"}:
                sort_order = "asc"
            query_text += f" ORDER BY {sort_by} {sort_order.upper()}"

            query_text += " OFFSET :skip LIMIT :limit"
            params.update({"skip": skip, "limit": limit})

            query = text(query_text)
            result = await session.execute(query, params)
            rows = result.all()

            return [
                BookResponse(
                    id=row.id,
                    title=row.title,
                    author_id=row.author_id,
                    published_year=row.published_year,
                    genres=row.genres
                )
                for row in rows
            ]

    async def get_books_by_author(self, author_id: UUID) -> list[BookResponse]:
        async with get_db() as session:
            query = text("""
                SELECT id, title, published_year, author_id, genres
                FROM books
                WHERE author_id = :author_id
            """)
            result = await session.execute(query, {"author_id": author_id})
            rows = result.all()
            return [
                BookResponse(
                    id=row.id,
                    title=row.title,
                    published_year=row.published_year,
                    author_id=row.author_id,
                    genres=row.genres
                )
                for row in rows
            ]
