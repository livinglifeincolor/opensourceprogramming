"""
검색 API 테스트: GET /api/posts/search?q={keyword}
"""
from datetime import datetime, timezone


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

async def test_search_by_title(client, db_override):
    """title에 키워드가 포함된 게시글이 검색 결과에 포함되어야 한다"""
    db_override(rows=[POST_PYTHON], val=1)

    response = await client.get("/api/posts/search?q=Python")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["results"]) == 1
    assert "Python" in data["results"][0]["title"]


async def test_search_by_content(client, db_override):
    """content에 키워드가 포함된 게시글이 검색 결과에 포함되어야 한다"""
    db_override(rows=[POST_FASTAPI], val=1)

    response = await client.get("/api/posts/search?q=framework")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert "framework" in data["results"][0]["content"]


async def test_search_no_match(client, db_override):
    """매칭되는 게시글이 없으면 results는 빈 리스트, total은 0이어야 한다"""
    db_override(rows=[], val=0)

    response = await client.get("/api/posts/search?q=존재하지않는키워드zzz")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["results"] == []


async def test_search_empty_query(client):
    """q가 빈 문자열이면 422 Unprocessable Entity를 반환해야 한다"""
    response = await client.get("/api/posts/search?q=")

    assert response.status_code == 422


async def test_search_case_insensitive(client, db_override):
    """검색은 대소문자를 구분하지 않아야 한다 (ILIKE)"""
    db_override(rows=[POST_PYTHON], val=1)

    response = await client.get("/api/posts/search?q=python")  # 소문자로 검색

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    # title에 Python(대문자)이 있어도 소문자 검색으로 찾혀야 한다
    assert data["results"][0]["title"] == "Python is great"


async def test_search_pagination(client, db_override):
    """page, size 파라미터가 동작해야 한다"""
    db_override(rows=[POST_PYTHON], val=5)

    response = await client.get("/api/posts/search?q=Python&page=2&size=1")

    assert response.status_code == 200
    data = response.json()
    # total은 전체 매칭 수(5), results는 한 페이지(1개)
    assert data["total"] == 5
    assert len(data["results"]) == 1


async def test_search_response_schema(client, db_override):
    """응답은 반드시 total(int)과 results(list) 키를 포함해야 한다"""
    db_override(rows=[POST_OTHER], val=1)

    response = await client.get("/api/posts/search?q=Hello")

    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "results" in data
    assert isinstance(data["total"], int)
    assert isinstance(data["results"], list)
