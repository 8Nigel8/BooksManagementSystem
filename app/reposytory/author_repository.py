import uuid
from abc import ABC
from typing import List

from sqlalchemy import text

from app.db.session import get_db
from app.schemas.author import AuthorCreate, AuthorResponse


class AuthorRepository(ABC):
    async def get_author(self, author_id: uuid.UUID) -> AuthorResponse | None:
        raise NotImplementedError()

    async def create_author(self, author: AuthorCreate) -> AuthorResponse:
        raise NotImplementedError()

    async def delete_author(self, author_id: uuid.UUID) -> AuthorResponse | None:
        raise NotImplementedError()

    async def get_all_authors(self) -> List[AuthorResponse]:
        raise NotImplementedError()

    async def get_author_by_name(self, name: str) -> AuthorResponse | None:
        raise NotImplementedError()


class AuthorRepositoryImpl(AuthorRepository):
    async def create_author(self, author: AuthorCreate) -> AuthorResponse:
        author_id = uuid.uuid4()
        async with get_db() as session:
            query = text("""
                INSERT INTO authors (id, name)
                VALUES (:id, :name)
                RETURNING id, name
            """)
            result = await session.execute(query, {"name": author.name, "id": author_id})
            await session.commit()
            row = result.first()
            return AuthorResponse(id=row.id, name=row.name)

    async def get_author(self, author_id: uuid.UUID) -> AuthorResponse | None:
        async with get_db() as session:
            query = text("""
                SELECT id, name
                FROM authors
                WHERE id = :author_id
            """)
            result = await session.execute(query, {"author_id": author_id})
            row = result.first()
            if row:
                return AuthorResponse(id=row.id, name=row.name)
            return None

    async def delete_author(self, author_id: uuid.UUID) -> AuthorResponse | None:
        async with get_db() as session:
            query = text("""
                DELETE FROM authors
                WHERE id = :author_id
                RETURNING id, name
            """)
            result = await session.execute(query, {"author_id": author_id})
            await session.commit()
            row = result.first()
            if row:
                return AuthorResponse(id=row.id, name=row.name)
            return None

    async def get_all_authors(self) -> List[AuthorResponse]:
        async with get_db() as session:
            query = text("SELECT id, name FROM authors")
            result = await session.execute(query)
            rows = result.all()
            return [AuthorResponse(id=row.id, name=row.name) for row in rows]

    async def get_author_by_name(self, name: str) -> AuthorResponse | None:
        async with get_db() as session:
            query = text("""
                SELECT id, name
                FROM authors
                WHERE name = :name
            """)
            result = await session.execute(query, {"name": name})
            row = result.first()
            if row:
                return AuthorResponse(id=row.id, name=row.name)
            return None
