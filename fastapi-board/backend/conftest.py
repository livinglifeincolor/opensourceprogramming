"""Pytest configuration and shared fixtures for the fastapi-board test suite.

This module provides:

* :class:`FakeConn` – an in-memory stand-in for an ``asyncpg`` connection.
* :class:`FakePool` – an async context-manager stand-in for an ``asyncpg``
  pool, compatible with the ``pool.acquire()`` pattern used in routers.
* :func:`client` – a pytest-asyncio fixture that provides an
  ``httpx.AsyncClient`` wired directly to the FastAPI ASGI app (no real
  network or database required).
* :func:`override_db` – a helper that builds a FastAPI dependency-override
  function pre-loaded with the test data you supply.
* :func:`db_override` – a pytest fixture that automatically installs and
  clears ``app.dependency_overrides`` around each test to prevent state
  leakage between tests.

Usage example::

    async def test_list_posts(client, db_override):
        db_override(rows=[{"id": 1, "title": "Hi", "content": "Hello world!", ...}])
        resp = await client.get("/api/posts")
        assert resp.status_code == 200
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.database import get_db


# ---------------------------------------------------------------------------
# Fake asyncpg Pool / Connection
# ---------------------------------------------------------------------------

class FakeConn:
    """Fake asyncpg connection for unit tests.

    Simulates the subset of the ``asyncpg.Connection`` interface used by the
    routers: ``fetchrow``, ``fetch``, ``fetchval``, and ``execute``.  Results
    are provided at construction time so tests remain fully deterministic.

    Attributes:
        _rows: Sequence of fake rows returned by ``fetch`` / ``fetchrow``.
        _val: Scalar value returned by ``fetchval``.
        _execute_result: String returned by ``execute`` (e.g. ``"DELETE 1"``).
    """

    def __init__(self, rows=None, val=None, execute_result="DELETE 1"):
        """Initialise the fake connection with canned responses.

        Args:
            rows: List of row-like objects to return from ``fetch`` /
                ``fetchrow``.  Defaults to an empty list.
            val: Scalar value to return from ``fetchval``.  Defaults to
                ``None``.
            execute_result: String to return from ``execute``.  Defaults to
                ``"DELETE 1"``.
        """
        self._rows = rows or []
        self._val = val
        self._execute_result = execute_result

    async def fetchrow(self, query, *args):
        """Return the first row, or ``None`` if no rows were provided.

        Args:
            query: SQL query string (ignored).
            *args: Query parameters (ignored).

        Returns:
            The first element of ``_rows``, or ``None``.
        """
        return self._rows[0] if self._rows else None

    async def fetch(self, query, *args):
        """Return all pre-loaded rows.

        Args:
            query: SQL query string (ignored).
            *args: Query parameters (ignored).

        Returns:
            list: All elements in ``_rows``.
        """
        return self._rows

    async def fetchval(self, query, *args):
        """Return the pre-loaded scalar value.

        Args:
            query: SQL query string (ignored).
            *args: Query parameters (ignored).

        Returns:
            The value passed as ``val`` at construction time.
        """
        return self._val

    async def execute(self, query, *args):
        """Return the pre-loaded execute result string.

        Args:
            query: SQL query string (ignored).
            *args: Query parameters (ignored).

        Returns:
            str: The value passed as ``execute_result`` at construction time.
        """
        return self._execute_result


class FakePool:
    """Async context-manager fake for an ``asyncpg`` connection pool.

    Mimics the ``pool.acquire()`` pattern so that router code that calls
    ``async with pool.acquire() as conn:`` works transparently in tests
    without a real database.

    Attributes:
        _rows: Forwarded to the underlying :class:`FakeConn`.
        _val: Forwarded to the underlying :class:`FakeConn`.
        _execute_result: Forwarded to the underlying :class:`FakeConn`.
    """

    def __init__(self, rows=None, val=None, execute_result="DELETE 1"):
        """Initialise the fake pool with the data to expose via a connection.

        Args:
            rows: List of rows to return from connection fetch methods.
            val: Scalar to return from ``fetchval``.
            execute_result: String to return from ``execute``.
        """
        self._rows = rows
        self._val = val
        self._execute_result = execute_result

    def acquire(self):
        """Return ``self`` so it can be used as an async context manager.

        Returns:
            FakePool: This object (acts as its own context manager).
        """
        return self

    async def __aenter__(self):
        """Enter the context and return a :class:`FakeConn`.

        Returns:
            FakeConn: A fake connection pre-loaded with the pool's data.
        """
        return FakeConn(
            rows=self._rows,
            val=self._val,
            execute_result=self._execute_result,
        )

    async def __aexit__(self, *args):
        """Exit the context; no teardown needed for a fake pool."""
        pass


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def client():
    """Provide an async HTTP client connected directly to the FastAPI app.

    Uses ``httpx.AsyncClient`` with ``ASGITransport`` so tests exercise the
    full ASGI stack (routing, middleware, serialisation) without a real
    network or database connection.

    Yields:
        httpx.AsyncClient: A client scoped to a single test.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


def override_db(rows=None, val=None, execute_result="DELETE 1"):
    """Build a FastAPI dependency-override that returns a :class:`FakePool`.

    This is an internal helper used by the :func:`db_override` fixture.
    You can also call it directly when you need fine-grained control over
    ``app.dependency_overrides``.

    Args:
        rows: List of row-like objects to return from the fake connection.
        val: Scalar value to return from ``fetchval``.
        execute_result: String to return from ``execute`` (default
            ``"DELETE 1"``).

    Returns:
        Callable: A zero-argument function that returns a :class:`FakePool`.
    """
    def _override():
        return FakePool(rows=rows, val=val, execute_result=execute_result)
    return _override


@pytest.fixture
def db_override():
    """Fixture that installs and auto-clears a fake ``get_db`` dependency.

    Yields a callable that accepts the same keyword arguments as
    :func:`override_db`.  Call it inside the test body to configure the fake
    database response.  After the test completes (pass or fail), the fixture
    automatically clears ``app.dependency_overrides`` so that no state leaks
    into subsequent tests.

    Yields:
        Callable: A function with signature
            ``(rows=None, val=None, execute_result="DELETE 1") -> None``
            that installs the override.

    Example:
        .. code-block:: python

            async def test_something(client, db_override):
                db_override(rows=[...], val=5)
                response = await client.get(...)
                assert response.status_code == 200
    """
    def _set(rows=None, val=None, execute_result="DELETE 1"):
        app.dependency_overrides[get_db] = override_db(
            rows=rows, val=val, execute_result=execute_result
        )

    yield _set

    # Teardown: always clean up regardless of test outcome.
    app.dependency_overrides.clear()
