from fastapi import APIRouter, Depends, HTTPException, Query
from app.database import get_db
from app.schemas import PostCreate, PostUpdate, PostResponse, SearchResponse

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.post("", response_model=PostResponse, status_code=201)
async def create_post(post: PostCreate, pool=Depends(get_db)):
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO posts (title, content) VALUES ($1, $2) RETURNING *",
            post.title,
            post.content,
        )
    return dict(row)


@router.get("/count")
async def get_posts_count(pool=Depends(get_db)):
    async with pool.acquire() as conn:
        total = await conn.fetchval("SELECT COUNT(*) FROM posts")
    return {"total": total}


@router.get("", response_model=list[PostResponse])
async def list_posts(page: int = 1, size: int = 10, pool=Depends(get_db)):
    offset = (page - 1) * size
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM posts ORDER BY created_at DESC LIMIT $1 OFFSET $2",
            size,
            offset,
        )
    return [dict(row) for row in rows]


@router.get("/search", response_model=SearchResponse)
async def search_posts(
    q: str = Query(..., min_length=1),
    page: int = 1,
    size: int = 10,
    pool=Depends(get_db),
):
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


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, pool=Depends(get_db)):
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM posts WHERE id = $1", post_id
        )
    if not row:
        raise HTTPException(status_code=404, detail="Post not found")
    return dict(row)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post: PostUpdate, pool=Depends(get_db)):
    async with pool.acquire() as conn:
        # 1. 존재 확인
        existing = await conn.fetchrow(
            "SELECT * FROM posts WHERE id = $1", post_id
        )
        if not existing:
            raise HTTPException(status_code=404, detail="Post not found")

        # 2. 필드 병합 — 요청에 포함된 필드만 덮어씀 (PostUpdate.apply_to)
        merged = post.apply_to(dict(existing))

        # 3. DB 업데이트
        row = await conn.fetchrow(
            "UPDATE posts SET title = $1, content = $2 WHERE id = $3 RETURNING *",
            merged["title"],
            merged["content"],
            post_id,
        )
    return dict(row)


@router.delete("/{post_id}", status_code=204)
async def delete_post(post_id: int, pool=Depends(get_db)):
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM posts WHERE id = $1", post_id
        )
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Post not found")

