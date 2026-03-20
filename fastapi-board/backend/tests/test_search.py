"""
STEP 3 — RED Phase
검색 API 테스트: GET /api/posts/search?q={keyword}

아직 엔드포인트가 구현되지 않았으므로 모든 테스트가 FAIL해야 한다.
"""
from datetime import datetime, timezone
import pytest
from app.main import app
from app.database import get_db
from conftest import override_db


# ─────────────────────────────────────────────────────────────────
# 테스트용 가짜 게시글 데이터
# ─────────────────────────────────────────────────────────────────

FAKE_TIME = datetime(2026, 3, 20, 0, 0, 0, tzinfo=timezone.utc)

POST_PYTHON = {
    "id": 1,
    "title": "Python is great",
    "content": "This post is about programming",
    "created_at": FAKE_TIME,
}

POST_FASTAPI = {
    "id": 2,
    "title": "FastAPI Tutorial",
    "content": "Learn how to use Python web framework",
    "created_at": FAKE_TIME,
}

POST_OTHER = {
    "id": 3,
    "title": "Hello World",
    "content": "This is a simple post",
    "created_at": FAKE_TIME,
}


# ─────────────────────────────────────────────────────────────────
# 테스트 케이스
# ─────────────────────────────────────────────────────────────────

async def test_search_by_title(client):
    """title에 키워드가 포함된 게시글이 검색 결과에 포함되어야 한다"""
    app.dependency_overrides[get_db] = override_db(rows=[POST_PYTHON], val=1)

    response = await client.get("/api/posts/search?q=Python")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["results"]) == 1
    assert "Python" in data["results"][0]["title"]

    app.dependency_overrides.clear()


async def test_search_by_content(client):
    """content에 키워드가 포함된 게시글이 검색 결과에 포함되어야 한다"""
    app.dependency_overrides[get_db] = override_db(rows=[POST_FASTAPI], val=1)

    response = await client.get("/api/posts/search?q=framework")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert "framework" in data["results"][0]["content"]

    app.dependency_overrides.clear()


async def test_search_no_match(client):
    """매칭되는 게시글이 없으면 results는 빈 리스트, total은 0이어야 한다"""
    app.dependency_overrides[get_db] = override_db(rows=[], val=0)

    response = await client.get("/api/posts/search?q=존재하지않는키워드zzz")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["results"] == []

    app.dependency_overrides.clear()


async def test_search_empty_query(client):
    """q가 빈 문자열이면 422 Unprocessable Entity를 반환해야 한다"""
    response = await client.get("/api/posts/search?q=")

    assert response.status_code == 422

    app.dependency_overrides.clear()


async def test_search_case_insensitive(client):
    """검색은 대소문자를 구분하지 않아야 한다 (ILIKE)"""
    app.dependency_overrides[get_db] = override_db(rows=[POST_PYTHON], val=1)

    response = await client.get("/api/posts/search?q=python")  # 소문자로 검색

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    # title에 Python(대문자)이 있어도 소문자 검색으로 찾혀야 한다
    assert data["results"][0]["title"] == "Python is great"

    app.dependency_overrides.clear()


async def test_search_pagination(client):
    """page, size 파라미터가 동작해야 한다"""
    app.dependency_overrides[get_db] = override_db(rows=[POST_PYTHON], val=5)

    response = await client.get("/api/posts/search?q=Python&page=2&size=1")

    assert response.status_code == 200
    data = response.json()
    # total은 전체 매칭 수(5), results는 한 페이지(1개)
    assert data["total"] == 5
    assert len(data["results"]) == 1

    app.dependency_overrides.clear()


async def test_search_response_schema(client):
    """응답은 반드시 total(int)과 results(list) 키를 포함해야 한다"""
    app.dependency_overrides[get_db] = override_db(rows=[POST_OTHER], val=1)

    response = await client.get("/api/posts/search?q=Hello")

    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "results" in data
    assert isinstance(data["total"], int)
    assert isinstance(data["results"], list)

    app.dependency_overrides.clear()
