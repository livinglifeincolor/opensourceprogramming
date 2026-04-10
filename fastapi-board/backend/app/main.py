"""FastAPI Board application entry point.

This module initialises the FastAPI application, configures CORS middleware,
manages the asyncpg connection-pool lifecycle via ``lifespan``, and registers
the posts router.  It also exposes a simple ``/health`` endpoint for
readiness checks.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db, close_db
from app.routers import posts


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the application lifecycle.

    Runs startup logic before the application begins serving requests, and
    teardown logic after it stops.  Specifically, it creates the asyncpg
    connection pool and initialises the database schema on startup, then
    gracefully closes the pool on shutdown.

    Args:
        app: The FastAPI application instance.

    Yields:
        None: Control is yielded to the running application.
    """
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="FastAPI Board",
    description=(
        "A minimal bulletin-board REST API built with FastAPI and asyncpg. "
        "Supports full CRUD operations on posts with cursor-based pagination "
        "and full-text search."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Allow the Next.js dev server to call the API during local development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router)


@app.get("/health", tags=["health"])
async def health():
    """Return a simple liveness status.

    Used by Docker health-checks and load-balancers to verify that the
    application process is running and able to handle requests.

    Returns:
        dict: A JSON object ``{"status": "ok"}``.
    """
    return {"status": "ok"}
