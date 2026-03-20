"""
STEP 5 — 회귀 테스트 (Regression Tests)
기존 CRUD 라우트가 검색 기능 추가 이후에도 정상 동작하는지 확인한다.
"""
from datetime import datetime, timezone
from app.main import app
from app.database import get_db
from conftest import override_db


FAKE_TIME = datetime(2026, 3, 20, 0, 0, 0, tzinfo=timezone.utc)

FAKE_POST = {
    "id": 1,
    "title": "Test Title",
    "content": "Test content here",
    "created_at": FAKE_TIME,
}


# ─────────────────────────────────────────────────────────────────
# POST /api/posts — 게시글 생성
# ─────────────────────────────────────────────────────────────────

async def test_create_post(client):
    """유효한 데이터로 게시글을 생성하면 201과 생성된 게시글을 반환해야 한다"""
    app.dependency_overrides[get_db] = override_db(rows=[FAKE_POST])

    response = await client.post(
        "/api/posts",
        json={"title": "Test Title", "content": "Test content here"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Title"
    assert data["content"] == "Test content here"
    assert "id" in data
    assert "created_at" in data

    app.dependency_overrides.clear()


async def test_create_post_title_too_short(client):
    """title이 빈 문자열이면 422를 반환해야 한다"""
    response = await client.post(
        "/api/posts",
        json={"title": "", "content": "Test content here"},
    )
    assert response.status_code == 422
    app.dependency_overrides.clear()


async def test_create_post_content_too_short(client):
    """content가 10자 미만이면 422를 반환해야 한다"""
    response = await client.post(
        "/api/posts",
        json={"title": "Valid Title", "content": "short"},
    )
    assert response.status_code == 422
    app.dependency_overrides.clear()


# ─────────────────────────────────────────────────────────────────
# GET /api/posts — 게시글 목록
# ─────────────────────────────────────────────────────────────────

async def test_list_posts(client):
    """게시글 목록을 조회하면 200과 리스트를 반환해야 한다"""
    app.dependency_overrides[get_db] = override_db(rows=[FAKE_POST])

    response = await client.get("/api/posts")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == 1

    app.dependency_overrides.clear()


async def test_list_posts_empty(client):
    """게시글이 없으면 빈 리스트를 반환해야 한다"""
    app.dependency_overrides[get_db] = override_db(rows=[])

    response = await client.get("/api/posts")

    assert response.status_code == 200
    assert response.json() == []

    app.dependency_overrides.clear()


# ─────────────────────────────────────────────────────────────────
# GET /api/posts/{id} — 게시글 단건 조회
# ─────────────────────────────────────────────────────────────────

async def test_get_post(client):
    """존재하는 게시글 조회 시 200과 해당 게시글을 반환해야 한다"""
    app.dependency_overrides[get_db] = override_db(rows=[FAKE_POST])

    response = await client.get("/api/posts/1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Test Title"

    app.dependency_overrides.clear()


async def test_get_post_not_found(client):
    """존재하지 않는 게시글 조회 시 404를 반환해야 한다"""
    app.dependency_overrides[get_db] = override_db(rows=[])

    response = await client.get("/api/posts/999")

    assert response.status_code == 404

    app.dependency_overrides.clear()


# ─────────────────────────────────────────────────────────────────
# PUT /api/posts/{id} — 게시글 수정
# ─────────────────────────────────────────────────────────────────

async def test_update_post(client):
    """존재하는 게시글 수정 시 200과 수정된 게시글을 반환해야 한다"""
    updated = {**FAKE_POST, "title": "Updated Title"}
    app.dependency_overrides[get_db] = override_db(rows=[updated])

    response = await client.put(
        "/api/posts/1",
        json={"title": "Updated Title"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"

    app.dependency_overrides.clear()


async def test_update_post_not_found(client):
    """존재하지 않는 게시글 수정 시 404를 반환해야 한다"""
    app.dependency_overrides[get_db] = override_db(rows=[])

    response = await client.put(
        "/api/posts/999",
        json={"title": "Updated Title"},
    )

    assert response.status_code == 404

    app.dependency_overrides.clear()


# ─────────────────────────────────────────────────────────────────
# DELETE /api/posts/{id} — 게시글 삭제
# ─────────────────────────────────────────────────────────────────

async def test_delete_post(client):
    """존재하는 게시글 삭제 시 204를 반환해야 한다"""
    app.dependency_overrides[get_db] = override_db(execute_result="DELETE 1")

    response = await client.delete("/api/posts/1")

    assert response.status_code == 204

    app.dependency_overrides.clear()


async def test_delete_post_not_found(client):
    """존재하지 않는 게시글 삭제 시 404를 반환해야 한다"""
    app.dependency_overrides[get_db] = override_db(execute_result="DELETE 0")

    response = await client.delete("/api/posts/999")

    assert response.status_code == 404

    app.dependency_overrides.clear()


# ─────────────────────────────────────────────────────────────────
# GET /api/posts/count — 게시글 수
# ─────────────────────────────────────────────────────────────────

async def test_get_posts_count(client):
    """게시글 수 조회 시 200과 total 필드를 반환해야 한다"""
    app.dependency_overrides[get_db] = override_db(val=5)

    response = await client.get("/api/posts/count")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5

    app.dependency_overrides.clear()
