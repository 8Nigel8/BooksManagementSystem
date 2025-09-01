from __future__ import annotations
from typing import TypeVar, Type

from app.reposytory.author_repository import AuthorRepository, AuthorRepositoryImpl
from app.reposytory.book_repository import BookRepository, BookRepositoryImpl
from app.reposytory.user_repository import UserRepository, UserRepositoryImpl
from app.services.auth_service import AuthService, AuthServiceImpl
from app.services.book_service import BookServiceImpl, BookService

T = TypeVar("T")


class Registry:
    _instances: dict[Type, object] = {}

    @classmethod
    def register(cls, key: Type[T], value: T) -> None:
        cls._instances[key] = value

    @classmethod
    def get(cls, interface: Type[T]) -> T:
        instance = cls._instances.get(interface)
        if instance is None:
            raise ValueError(f"No implementation registered for {interface}")
        return instance


def init_registry() -> None:
    Registry.register(AuthorRepository, AuthorRepositoryImpl())
    Registry.register(BookRepository, BookRepositoryImpl(Registry.get(AuthorRepository)))
    Registry.register(BookService, BookServiceImpl(Registry.get(BookRepository), Registry.get(AuthorRepository)))

    Registry.register(UserRepository, UserRepositoryImpl())
    Registry.register(AuthService, AuthServiceImpl(Registry.get(UserRepository)))