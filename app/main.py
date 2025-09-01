from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.middlewares.error_handler import error_handling_middleware
from app.registry import init_registry


from app.api.endpoints.books import router as books_router
from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.authors import router as authors_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_registry()
    yield

app = FastAPI(title="Books API", lifespan=lifespan)

app.middleware("http")(error_handling_middleware)
app.include_router(books_router, prefix="/api/v1", tags=["books"])
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
app.include_router(authors_router, prefix="/api/v1", tags=["authors"])