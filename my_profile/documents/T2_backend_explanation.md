# 1. 데이터 모델링 이해 (`schema.sql`)

백엔드 개발의 시작은 데이터를 어떻게 저장하고 연관 지을지 구조를 설계하는 것입니다. 이 과정을 **데이터 모델링**이라고 합니다.

### 데이터베이스, SQL, 그리고 PostgreSQL

- **데이터베이스 (Database)**: 수많은 데이터를 안전하고 체계적으로 저장, 관리하는 가상의 창고입니다.
- **SQL (Structured Query Language)**: 데이터베이스와 대화하기 위한 표준 언어입니다. "회원 정보를 추가해 줘", "특정 게시물을 가져와 줘"와 같은 명령을 내릴 때 사용합니다.
- **PostgreSQL**: 안정성과 강력한 기능을 자랑하는 대표적인 오픈 소스 관계형 데이터베이스 관리 시스템(RDBMS)입니다. 정보를 엑셀 시트와 같은 '테이블' 형태로 저장하며, 데이터 간의 연결(관계)을 엄격하고 정확하게 다룰 수 있어 현업에서 매우 널리 쓰입니다.

이 프로젝트는 PostgreSQL 데이터베이스를 사용하며, 아래와 같이 프로젝트 루트의 `backend/schema.sql` 파일을 실행하여 초기 테이블을 생성합니다.

### 테이블 명세 및 코드 분석 (`schema.sql`)

```sql
-- 1. 사용자 테이블 (users)
CREATE TABLE IF NOT EXISTS users (
    -- id: 각 사용자를 구별하는 고유 식별자.
    -- SERIAL: 데이터가 추가될 때 자동으로 1, 2, 3... 번호를 부여함
    -- PRIMARY KEY: 테이블 내에서 유일하고 필수적인 값(기본 키)으로 지정
    id SERIAL PRIMARY KEY,

    -- username, email: 사용자 이름과 이메일.
    -- UNIQUE: 동일한 값이 중복되어 가입되는 것을 시스템적으로 차단
    -- NOT NULL: 필수 입력 데이터로 빈 값을 허용하지 않음
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,

    -- password_hash: 사용자의 평문 비밀번호 대신 안전하게 해싱(암호화)된 값을 저장
    password_hash VARCHAR(256) NOT NULL,

    -- created_at: 회원가입 시간. 별도 입력이 없어도 저장 시점의 시간이 기본으로 들어감
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 게시글 테이블 (posts)
CREATE TABLE IF NOT EXISTS posts (
    -- id, title, content: 게시글 식별 아이디, 제목, 본문
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,

    -- user_id: 이 게시글의 작성자를 가리키는 고유 식별자 (users 테이블의 id)
    -- REFERENCES users(id): users 테이블의 id를 가리키는 외래 키(Foreign Key) 설정
    -- ON DELETE CASCADE: 작성자(users 레코드)가 탈퇴(삭제)되면, 해당 게시물도 연쇄적으로 삭제됨
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- created_at, updated_at: 게시글 생성 및 최근 수정 시간
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

# 2. 데이터베이스 연동 로직 (`db.py`)

파이썬 백엔드(`Flask`)가 PostgreSQL 데이터베이스와 어떻게 연결되고 통신하는지를 담당하는 코어 파일입니다.

### 핵심 기능 및 코드 분석 (`db.py`)

```python
import os
import psycopg2
import psycopg2.extras
from flask import g

def get_db():
    """현재 요청에 대한 DB 연결을 반환 (Flask g 객체에 캐싱)"""
    # g는 Flask에서 제공하는 글로벌 전용 저장소입니다. 한 번 접속한 DB 파이프를
    # 매번 새로 만들지 않고 g 객체에 임시 저장(캐싱)해 둔 뒤 재사용합니다.
    if "db" not in g:
        g.db = psycopg2.connect(
            # os.environ.get을 통해 도커(docker-compose) 설정에 주입된 환경 변수를 가져와 연결합니다.
            host=os.environ.get("DB_HOST", "localhost"),
            port=os.environ.get("DB_PORT", "5432"),
            dbname=os.environ.get("DB_NAME", "knu_open"),
            user=os.environ.get("DB_USER", "postgres"),
            password=os.environ.get("DB_PASSWORD", "postgres"),
        )
        # 쿼리가 실행될 때마다 자동으로 결과가 저장(commit)되도록 설정합니다.
        g.db.autocommit = True
    return g.db

def close_db(e=None):
    """요청 종료 시 DB 연결 닫기"""
    # 사용자의 단일 요청(API 호출)이 완전히 끝나면 연결을 안전하게 끊어줍니다.
    # 사용하지 않는 DB 접속이 누적되어 자원(메모리 등)이 낭비되는 것을 방지합니다.
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db(app):
    """schema.sql을 실행하여 테이블 초기화"""
    # 앱이 처음 켜질 때 자동으로 데이터베이스 뼈대(테이블)를 만드는 함수입니다.
    with app.app_context():
        db = get_db()
        cur = db.cursor()
        # db.py 파일이 위치한 현재 폴더 경로를 찾아 "schema.sql"을 연결합니다.
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        with open(schema_path, "r") as f:
            # 파일 안의 모든 SQL 명령어를 DB로 전송하여 실행합니다.
            cur.execute(f.read())
        cur.close()

def query_db(query, args=(), one=False):
    """SQL 쿼리 실행 후 딕셔너리 형태로 결과 반환"""
    db = get_db()
    # RealDictCursor를 사용해 데이터베이스 쿼리 파싱 결과를 단순 리스트가 아닌
    # 파이썬의 딕셔너리(Dictionary) 형태로 조립합니다. (예: row['username'])
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(query, args)

    # 만약 데이터베이스에서 정보를 가져오는 "SELECT" 명령어라면 결과를 반환하고,
    if query.strip().upper().startswith("SELECT"):
        rv = cur.fetchall()
        cur.close()
        # one=True면 결과 중 맨 첫 번째 1개만 반환, 아니면 전체 목록 반환
        if one:
            return rv[0] if rv else None
        return rv
    else:
        # 정보를 삽입/수정/삭제하는 명령어(INSERT, UPDATE 등)라면 반환값 없이 끝냅니다.
        cur.close()
        return None
```

# 3. 비즈니스 로직 및 API 분석 (`app.py`)

클라이언트(프론트엔드)의 요청에 따라 실제 기능을 수행하는 핵심 로직입니다.

- **인증 및 보안 (Auth)**:
  - **회원가입**: `generate_password_hash`를 사용해 비밀번호를 안전하게 암호화하여 저장합니다.
  - **로그인 및 세션**: `check_password_hash`로 비밀번호를 확인하고, 성공 시 `session["user_id"]`에 사용자 정보를 저장하여 이후 요청에서도 로그인 상태를 유지합니다.

- **게시판 기능 (CRUD)**:
  - **목록 조회 (Read)**: `LIMIT`와 `OFFSET`을 사용하여 페이지별로 10개씩 글을 가져오는 페이지네이션이 구현되어 있습니다.
  - **권한 체크 (Update/Delete)**: 글을 수정하거나 삭제할 때, `session`의 `user_id`와 게시글의 `user_id`를 비교하여 본인의 글인지 확인하는 권한 로직이 포함되어 있습니다.
