import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

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
    """실제 DB 없이 FastAPI 앱을 테스트하는 AsyncClient."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


def override_db(rows=None, val=None, execute_result="DELETE 1"):
    """get_db 의존성을 FakePool로 교체하는 헬퍼 함수 (내부용)."""
    def _override():
        return FakePool(rows=rows, val=val, execute_result=execute_result)
    return _override


@pytest.fixture
def db_override():
    """
    get_db 의존성을 FakePool로 자동 교체·해제하는 fixture.

    테스트 성공/실패 여부와 무관하게 teardown에서 dependency_overrides를
    자동으로 clear하므로 테스트 간 상태 오염이 발생하지 않는다.

    Usage:
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

    app.dependency_overrides.clear()
