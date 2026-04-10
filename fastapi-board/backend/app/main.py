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



# Tag metadata — these descriptions appear as section headers in Swagger UI
# and act as the Flasgger-equivalent of @swag_from tag annotations.
_OPENAPI_TAGS = [
    {
        "name": "posts",
        "description": (
            "Operations on bulletin-board **posts**. "
            "Supports full CRUD (Create / Read / Update / Delete), "
            "paginated listing, and full-text keyword search."
        ),
        "externalDocs": {
            "description": "Sphinx source documentation",
            "url": "https://livinglifeincolor.github.io/opensourceprogramming/",
        },
    },
    {
        "name": "health",
        "description": "Liveness probe used by Docker and load-balancers.",
    },
]

app = FastAPI(
    title="FastAPI Board API",
    description="""
## Overview

A minimal bulletin-board REST API built with **FastAPI** and **asyncpg** (raw SQL, no ORM),
backed by **PostgreSQL 16** and served with **Uvicorn**.

## Features

| Feature | Detail |
|---------|--------|
| CRUD | Create, read, update, delete posts |
| Pagination | `page` + `size` query parameters |
| Search | Case-insensitive full-text search via PostgreSQL `ILIKE` |
| Validation | Pydantic v2 field-level constraints |
| Testing | 20 async unit tests (pytest-asyncio, no real DB needed) |

## Quick Start

```bash
docker compose up --build
```

| Service | URL |
|---------|-----|
| Frontend (Next.js) | http://localhost:3000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Sphinx Docs | https://livinglifeincolor.github.io/opensourceprogramming/ |

## Source Code

[github.com/livinglifeincolor/opensourceprogramming](https://github.com/livinglifeincolor/opensourceprogramming)
""",
    version="1.0.0",
    contact={
        "name": "livinglifeincolor",
        "url": "https://github.com/livinglifeincolor",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=_OPENAPI_TAGS,
    docs_url="/docs",
    redoc_url="/redoc",
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
