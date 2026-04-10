"""REST API router for the posts resource.

This module defines all CRUD endpoints under the ``/api/posts`` prefix:

- ``POST   /api/posts``                – Create a new post
- ``GET    /api/posts``                – List posts (paginated)
- ``GET    /api/posts/count``          – Return the total number of posts
- ``GET    /api/posts/search``         – Search posts by keyword
- ``GET    /api/posts/{post_id}``      – Retrieve a single post
- ``PUT    /api/posts/{post_id}``      – Partially update a post
- ``DELETE /api/posts/{post_id}``      – Delete a post

All handlers depend on :func:`app.database.get_db` to obtain an asyncpg
connection pool, and use raw SQL queries via ``asyncpg`` (no ORM).

OpenAPI metadata (``summary``, ``description``, ``responses``, and
``openapi_extra``) is declared inline on every route decorator so that
the auto-generated Swagger UI (``/docs``) and ReDoc (``/redoc``) pages
display rich, interactive documentation — equivalent in scope to what
Flasgger provides for Flask applications.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from app.database import get_db
from app.schemas import PostCreate, PostUpdate, PostResponse, SearchResponse

router = APIRouter(prefix="/api/posts", tags=["posts"])

# ---------------------------------------------------------------------------
# Reusable example objects (referenced by multiple endpoints)
# ---------------------------------------------------------------------------

_EXAMPLE_POST = {
    "id": 1,
    "title": "My First Post",
    "content": "This is the body of my very first bulletin-board post.",
    "created_at": "2025-03-01T09:00:00Z",
}

_EXAMPLE_POST_2 = {
    "id": 2,
    "title": "FastAPI Tips",
    "content": "Use Pydantic v2 models and asyncpg for blazing-fast async APIs.",
    "created_at": "2025-03-02T10:30:00Z",
}

_ERROR_404 = {"detail": "Post not found"}
_ERROR_422 = {
    "detail": [
        {
            "type": "string_too_short",
            "loc": ["body", "content"],
            "msg": "String should have at least 10 characters",
            "input": "too short",
        }
    ]
}


# ---------------------------------------------------------------------------
# POST /api/posts — Create
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=PostResponse,
    status_code=201,
    summary="Create a new post",
    description=(
        "Inserts a new post into the database and returns the persisted "
        "record including its auto-generated ``id`` and ``created_at`` "
        "timestamp.\n\n"
        "**Validation rules**\n"
        "- `title`: 1–100 characters\n"
        "- `content`: at least 10 characters"
    ),
    response_description="The newly created post",
    responses={
        422: {
            "description": "Validation Error — title or content failed constraints",
            "content": {
                "application/json": {
                    "example": _ERROR_422,
                }
            },
        },
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "typical_post": {
                            "summary": "A typical post",
                            "value": {
                                "title": "My First Post",
                                "content": "This is the body of my very first bulletin-board post.",
                            },
                        },
                        "long_post": {
                            "summary": "A post with a longer title",
                            "value": {
                                "title": "FastAPI + asyncpg: Building High-Performance APIs",
                                "content": (
                                    "FastAPI leverages Python type hints and Pydantic for "
                                    "automatic validation, while asyncpg gives direct "
                                    "access to PostgreSQL over an async connection pool."
                                ),
                            },
                        },
                    },
                }
            }
        }
    },
)
async def create_post(post: PostCreate, pool=Depends(get_db)):
    """Create a new bulletin-board post.

    Args:
        post: Validated request body containing ``title`` and ``content``.
        pool: asyncpg connection pool injected by FastAPI's DI system.

    Returns:
        PostResponse: The persisted post record.
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO posts (title, content) VALUES ($1, $2) RETURNING *",
            post.title,
            post.content,
        )
    return dict(row)


# ---------------------------------------------------------------------------
# GET /api/posts/count — Count
# ---------------------------------------------------------------------------

@router.get(
    "/count",
    summary="Get total post count",
    description="Returns the total number of posts currently stored in the database.",
    response_description="An object with a single integer field `total`",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"total": 42},
                }
            }
        }
    },
)
async def get_posts_count(pool=Depends(get_db)):
    """Return the total number of posts in the database.

    Args:
        pool: asyncpg connection pool injected by FastAPI's DI system.

    Returns:
        dict: ``{"total": <int>}`` where ``total`` is the post count.
    """
    async with pool.acquire() as conn:
        total = await conn.fetchval("SELECT COUNT(*) FROM posts")
    return {"total": total}


# ---------------------------------------------------------------------------
# GET /api/posts — List (paginated)
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=list[PostResponse],
    summary="List posts",
    description=(
        "Returns a paginated list of posts ordered by creation date "
        "(newest first).\n\n"
        "**Query parameters**\n"
        "- `page` (default `1`): 1-based page number\n"
        "- `size` (default `10`): number of posts per page"
    ),
    response_description="A list of post objects for the requested page",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [_EXAMPLE_POST_2, _EXAMPLE_POST],
                }
            }
        }
    },
)
async def list_posts(page: int = 1, size: int = 10, pool=Depends(get_db)):
    """Retrieve a paginated list of posts.

    Args:
        page: 1-based page number (default: ``1``).
        size: Maximum number of posts to return per page (default: ``10``).
        pool: asyncpg connection pool injected by FastAPI's DI system.

    Returns:
        list[PostResponse]: Posts for the requested page, sorted by
            ``created_at`` descending.
    """
    offset = (page - 1) * size
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM posts ORDER BY created_at DESC LIMIT $1 OFFSET $2",
            size,
            offset,
        )
    return [dict(row) for row in rows]


# ---------------------------------------------------------------------------
# GET /api/posts/search — Search
# ---------------------------------------------------------------------------

@router.get(
    "/search",
    response_model=SearchResponse,
    summary="Search posts",
    description=(
        "Performs a **case-insensitive** keyword search (`ILIKE`) across "
        "post titles and content.\n\n"
        "**Query parameters**\n"
        "- `q` (required): keyword string, min length 1\n"
        "- `page` (default `1`): 1-based page number\n"
        "- `size` (default `10`): results per page\n\n"
        "The response includes `total` (total number of matches across all "
        "pages) and `results` (posts for the current page)."
    ),
    response_description="Matching posts for the current page and the total match count",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "total": 1,
                        "results": [_EXAMPLE_POST_2],
                    },
                }
            }
        }
    },
)
async def search_posts(
    q: str = Query(..., min_length=1, description="Keyword to search for"),
    page: int = 1,
    size: int = 10,
    pool=Depends(get_db),
):
    """Search posts by keyword in title or content.

    Performs a case-insensitive ``ILIKE`` match against both the ``title``
    and ``content`` columns.  Results are paginated.

    Args:
        q: The search keyword (URL query parameter, min length 1).
        page: 1-based page number (default: ``1``).
        size: Maximum number of results to return per page (default: ``10``).
        pool: asyncpg connection pool injected by FastAPI's DI system.

    Returns:
        SearchResponse: An object containing the total number of matches and
            the list of post objects for the current page.
    """
    offset = (page - 1) * size
    keyword = f"%{q}%"
    async with pool.acquire() as conn:
        total = await conn.fetchval(
            "SELECT COUNT(*) FROM posts WHERE title ILIKE $1 OR content ILIKE $1",
            keyword,
        )
        rows = await conn.fetch(
            """
            SELECT * FROM posts
            WHERE title ILIKE $1 OR content ILIKE $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
            """,
            keyword,
            size,
            offset,
        )
    return {"total": total, "results": [dict(row) for row in rows]}


# ---------------------------------------------------------------------------
# GET /api/posts/{post_id} — Read one
# ---------------------------------------------------------------------------

@router.get(
    "/{post_id}",
    response_model=PostResponse,
    summary="Get a single post",
    description="Retrieves a single post by its integer ``post_id``.",
    response_description="The requested post object",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": _EXAMPLE_POST,
                }
            }
        },
        404: {
            "description": "Post not found",
            "content": {
                "application/json": {
                    "example": _ERROR_404,
                }
            },
        },
    },
)
async def get_post(post_id: int, pool=Depends(get_db)):
    """Retrieve a single post by ID.

    Args:
        post_id: The integer primary key of the post to retrieve.
        pool: asyncpg connection pool injected by FastAPI's DI system.

    Returns:
        PostResponse: The requested post.

    Raises:
        HTTPException: 404 if no post with ``post_id`` exists.
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM posts WHERE id = $1", post_id
        )
    if not row:
        raise HTTPException(status_code=404, detail="Post not found")
    return dict(row)


# ---------------------------------------------------------------------------
# PUT /api/posts/{post_id} — Update
# ---------------------------------------------------------------------------

@router.put(
    "/{post_id}",
    response_model=PostResponse,
    summary="Update a post",
    description=(
        "Partially updates an existing post.  Only the fields included in "
        "the request body are modified; omitted fields retain their current "
        "values.\n\n"
        "**Constraint**: at least one field (`title` or `content`) must be "
        "provided; an empty body returns **422**."
    ),
    response_description="The updated post object",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {**_EXAMPLE_POST, "title": "Updated Title"},
                }
            }
        },
        404: {
            "description": "Post not found",
            "content": {"application/json": {"example": _ERROR_404}},
        },
        422: {
            "description": "Validation Error — empty body or invalid field values",
        },
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "update_title_only": {
                            "summary": "Change only the title",
                            "value": {"title": "Updated Title"},
                        },
                        "update_content_only": {
                            "summary": "Change only the content",
                            "value": {
                                "content": "Revised content that is at least ten characters long."
                            },
                        },
                        "update_both": {
                            "summary": "Change both fields",
                            "value": {
                                "title": "Revised Title",
                                "content": "Revised content that is at least ten characters long.",
                            },
                        },
                    }
                }
            }
        }
    },
)
async def update_post(post_id: int, post: PostUpdate, pool=Depends(get_db)):
    """Partially update an existing post.

    Uses :meth:`PostUpdate.apply_to` to merge only the explicitly provided
    fields onto the existing row, then persists the result.

    Args:
        post_id: The integer primary key of the post to update.
        post: Validated request body.  At least one of ``title`` or
            ``content`` must be present (enforced by ``PostUpdate``'s
            model validator).
        pool: asyncpg connection pool injected by FastAPI's DI system.

    Returns:
        PostResponse: The post as it exists after the update.

    Raises:
        HTTPException: 404 if no post with ``post_id`` exists.
    """
    async with pool.acquire() as conn:
        # 1. Verify the post exists before attempting an update.
        existing = await conn.fetchrow(
            "SELECT * FROM posts WHERE id = $1", post_id
        )
        if not existing:
            raise HTTPException(status_code=404, detail="Post not found")

        # 2. Merge only the explicitly sent fields onto the existing row.
        merged = post.apply_to(dict(existing))

        # 3. Persist the merged values.
        row = await conn.fetchrow(
            "UPDATE posts SET title = $1, content = $2 WHERE id = $3 RETURNING *",
            merged["title"],
            merged["content"],
            post_id,
        )
    return dict(row)


# ---------------------------------------------------------------------------
# DELETE /api/posts/{post_id} — Delete
# ---------------------------------------------------------------------------

@router.delete(
    "/{post_id}",
    status_code=204,
    summary="Delete a post",
    description=(
        "Permanently deletes the post identified by ``post_id``.  "
        "Returns **204 No Content** on success."
    ),
    responses={
        204: {"description": "Post deleted successfully — no response body"},
        404: {
            "description": "Post not found",
            "content": {"application/json": {"example": _ERROR_404}},
        },
    },
)
async def delete_post(post_id: int, pool=Depends(get_db)):
    """Delete a post by ID.

    Args:
        post_id: The integer primary key of the post to delete.
        pool: asyncpg connection pool injected by FastAPI's DI system.

    Raises:
        HTTPException: 404 if no post with the given ``post_id`` exists,
            detected when asyncpg returns ``"DELETE 0"``.
    """
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM posts WHERE id = $1", post_id
        )
    # asyncpg returns "DELETE <count>" — "DELETE 0" means nothing was removed.
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Post not found")
