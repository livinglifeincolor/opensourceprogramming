# fastapi-board

CRUD + 페이지네이션을 갖춘 미니멀 게시판 프로젝트.

## 기술 스택

| 영역 | 기술 |
|------|------|
| Backend | FastAPI, asyncpg (raw SQL), PostgreSQL 16 |
| Frontend | Next.js 14 (App Router), TailwindCSS v4, TypeScript |
| Infra | Docker Compose |

## 기능

- 게시글 **목록 조회** (10개씩 페이지네이션)
- 게시글 **작성** — 제목 100자 제한·내용 10자 이상 실시간 유효성 검사
- 게시글 **상세 조회**
- 게시글 **수정**
- 게시글 **삭제**

## 빠른 시작

```bash
docker compose up --build
```

| 서비스 | URL |
|--------|-----|
| 프론트엔드 | http://localhost:3000 |
| API 문서 (Swagger) | http://localhost:8000/docs |

## 로컬 개발

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/posts?page=1&size=10` | 게시글 목록 (페이지네이션) |
| `GET` | `/api/posts/count` | 전체 게시글 수 |
| `POST` | `/api/posts` | 게시글 생성 |
| `GET` | `/api/posts/{id}` | 게시글 상세 조회 |
| `PUT` | `/api/posts/{id}` | 게시글 수정 (부분 수정 가능) |
| `DELETE` | `/api/posts/{id}` | 게시글 삭제 |

## 프로젝트 구조

```
fastapi-board/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI 앱, CORS, lifespan
│   │   ├── database.py      # asyncpg 연결 풀, 테이블 초기화
│   │   ├── schemas.py       # Pydantic 모델 (유효성 포함)
│   │   └── routers/
│   │       └── posts.py     # CRUD 엔드포인트
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── page.tsx              # 목록 (페이지네이션)
│   │   ├── new/page.tsx          # 글쓰기
│   │   └── posts/[id]/
│   │       ├── page.tsx          # 상세
│   │       └── edit/page.tsx     # 수정
│   ├── components/
│   │   ├── PostCard.tsx
│   │   ├── PostActions.tsx       # 수정·삭제 버튼
│   │   └── Pagination.tsx
│   ├── lib/api.ts
│   └── Dockerfile
└── docker-compose.yml
```
