"""Database connection management using asyncpg.

This module owns the global asyncpg connection pool (``_pool``).  It exposes
three coroutines that are called by the FastAPI ``lifespan`` context manager:

* :func:`init_db` – creates the pool and ensures the ``posts`` table exists.
* :func:`close_db` – drains and closes the pool gracefully.
* :func:`get_db` – FastAPI dependency that returns the pool so routers can
  acquire connections.

The ``DATABASE_URL`` is read from the environment (or ``.env``) so that the
same code works both inside Docker Compose and in local development.
"""

import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/boarddb",
)

# Module-level pool variable; populated by init_db() and consumed by get_db().
_pool: asyncpg.Pool | None = None


async def init_db() -> None:
    """Create the connection pool and initialise the database schema.

    Reads ``DATABASE_URL`` from the environment and establishes an asyncpg
    connection pool.  Then runs a ``CREATE TABLE IF NOT EXISTS`` statement
    to ensure the ``posts`` table is present before the application starts
    serving requests.

    Raises:
        asyncpg.PostgresConnectionError: If the database is unreachable.
    """
    global _pool
    _pool = await asyncpg.create_pool(DATABASE_URL)
    async with _pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id         SERIAL PRIMARY KEY,
                title      VARCHAR(255) NOT NULL,
                content    TEXT         NOT NULL,
                created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
            )
            """
        )


async def close_db() -> None:
    """Close the asyncpg connection pool.

    Waits for all active connections to be released, then terminates the pool.
    Safe to call even if ``init_db`` was never invoked (e.g. during testing).
    """
    global _pool
    if _pool:
        await _pool.close()


async def get_db() -> asyncpg.Pool:
    """FastAPI dependency that provides the asyncpg connection pool.

    Routers obtain the pool via ``Depends(get_db)`` and call
    ``pool.acquire()`` themselves to check out individual connections.

    Returns:
        asyncpg.Pool: The application-wide connection pool.
    """
    return _pool
