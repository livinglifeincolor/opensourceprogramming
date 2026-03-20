import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock

from app.main import app
from app.database import get_db


# ─────────────────────────────────────────────
# Fake asyncpg Pool / Connection
# ─────────────────────────────────────────────

class FakeConn:
    """asyncpg Connection을 흉내 내는 Fake 객체"""

    def __init__(self, rows=None, val=None, execute_result="DELETE 1"):
        self._rows = rows or []
        self._val = val
        self._execute_result = execute_result

    async def fetchrow(self, query, *args):
        return self._rows[0] if self._rows else None

    async def fetch(self, query, *args):
        return self._rows

    async def fetchval(self, query, *args):
        return self._val

    async def execute(self, query, *args):
        return self._execute_result


class FakePool:
    """asyncpg Pool을 흉내 내는 컨텍스트 매니저 Fake 객체"""

    def __init__(self, rows=None, val=None, execute_result="DELETE 1"):
        self._rows = rows
        self._val = val
        self._execute_result = execute_result

    def acquire(self):
        return self

    async def __aenter__(self):
        return FakeConn(
            rows=self._rows,
            val=self._val,
            execute_result=self._execute_result,
        )

    async def __aexit__(self, *args):
        pass


# ─────────────────────────────────────────────
# 공통 픽스처
# ─────────────────────────────────────────────

@pytest_asyncio.fixture
async def client():
    """
    실제 DB 없이 FastAPI 앱을 테스트하는 AsyncClient.
    각 테스트에서 app.dependency_overrides 를 직접 설정한다.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


def override_db(rows=None, val=None, execute_result="DELETE 1"):
    """
    get_db 의존성을 FakePool로 교체하는 헬퍼 함수.
    각 테스트에서 필요한 데이터로 커스터마이즈한다.

    Usage:
        app.dependency_overrides[get_db] = override_db(rows=[...])
    """
    def _override():
        return FakePool(rows=rows, val=val, execute_result=execute_result)
    return _override
