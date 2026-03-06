# 📝 My Development Journal

개인 개발 기록을 위한 게시판 웹 애플리케이션입니다.

## 기술 스택

| 구성 요소    | 기술                             |
| ------------ | -------------------------------- |
| **Frontend** | Next.js 16, React 19, TypeScript |
| **Backend**  | Flask (Python 3.12)              |
| **Database** | PostgreSQL 16                    |
| **Infra**    | Docker Compose                   |

## 디렉토리 구조

```
my_profile/
├── docker-compose.yml      # 전체 서비스 오케스트레이션
├── backend/                # Flask API 서버
│   ├── Dockerfile
│   ├── app.py              # 라우트 정의 (인증 + 게시판 CRUD)
│   ├── db.py               # DB 연결 및 쿼리 헬퍼
│   ├── schema.sql          # 테이블 스키마 (users, posts)
│   └── requirements.txt    # Python 의존성
└── frontend/               # Next.js 클라이언트
    ├── Dockerfile
    ├── src/
    │   ├── app/
    │   │   ├── layout.tsx         # 루트 레이아웃 + Navbar
    │   │   ├── page.tsx           # / → /posts 리다이렉트
    │   │   ├── login/page.tsx     # 로그인 페이지
    │   │   ├── register/page.tsx  # 회원가입 페이지
    │   │   ├── posts/page.tsx     # 게시글 목록
    │   │   ├── posts/[id]/page.tsx    # 게시글 상세
    │   │   ├── posts/write/page.tsx   # 글 작성/수정
    │   │   ├── components/Navbar.tsx  # 네비게이션 바
    │   │   └── globals.css        # 전역 스타일
    │   └── lib/
    │       └── api.ts             # API 호출 함수
    └── package.json
```

## 시작하기

### 사전 준비

- [Docker](https://www.docker.com/) 및 Docker Compose 설치

### 실행

```bash
# 1. 저장소 클론
git clone https://github.com/edward-official/LectureOpenSourceProgramming.git
cd LectureOpenSourceProgramming/my_profile

# 2. 전체 서비스 빌드 및 실행
docker compose up --build
```

### 접속

| 서비스         | URL                                                     |
| -------------- | ------------------------------------------------------- |
| **프론트엔드** | http://localhost:3000                                   |
| **백엔드 API** | http://localhost:5001                                   |
| **PostgreSQL** | localhost:5432 (user: `postgres`, password: `postgres`) |

### 종료

```bash
# 서비스 중지
docker compose down

# 서비스 중지 + DB 데이터 삭제
docker compose down -v
```

## 주요 기능

### 🔐 인증

- 회원가입 / 로그인 / 로그아웃
- 세션 기반 인증

### 📋 게시판

- 게시글 목록 (페이지네이션, 비로그인 열람 가능)
- 게시글 작성 / 수정 / 삭제 (로그인 필수)
- 본인 글만 수정·삭제 가능

## API 엔드포인트

### 인증

| Method | Endpoint             | 설명             |
| ------ | -------------------- | ---------------- |
| POST   | `/api/auth/register` | 회원가입         |
| POST   | `/api/auth/login`    | 로그인           |
| POST   | `/api/auth/logout`   | 로그아웃         |
| GET    | `/api/auth/me`       | 현재 사용자 조회 |

### 게시판

| Method | Endpoint            | 설명        | 인증        |
| ------ | ------------------- | ----------- | ----------- |
| GET    | `/api/posts?page=1` | 게시글 목록 | ❌          |
| GET    | `/api/posts/:id`    | 게시글 상세 | ❌          |
| POST   | `/api/posts`        | 게시글 작성 | ✅          |
| PUT    | `/api/posts/:id`    | 게시글 수정 | ✅ (본인만) |
| DELETE | `/api/posts/:id`    | 게시글 삭제 | ✅ (본인만) |
