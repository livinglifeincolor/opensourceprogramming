# docker-compose.yml 파일 구조 및 설명

이 문서는 프로젝트 최상단에 위치한 `docker-compose.yml` 파일의 각 서비스(컨테이너)가 어떻게 설정되어 있고 서로 어떻게 통신하는지 설명합니다.

## 전체 개요

Docker Compose는 여러 개의 컨테이너로 이루어진 애플리케이션을 하나의 명령어로 정의하고 실행할 수 있게 해주는 도구입니다.
본 프로젝트에서는 `db`(데이터베이스), `backend`(API 서버), `frontend`(클라이언트) 총 3개의 서비스로 구성되어 있습니다.

```yaml
services:
  db: ...
  backend: ...
  frontend: ...
```

## 1. db (PostgreSQL 데이터베이스)

- **image**: `postgres:16-alpine`
  경량화된 alpine 리눅스 기반의 PostgreSQL 16 버전을 사용합니다.
- **environment**:
  데이터베이스 초기 설정(DB 이름, 사용자명, 비밀번호)을 환경 변수로 주입합니다.
- **ports**: `"5432:5432"`
  호스트 컴퓨터의 5432 포트와 컨테이너 내부의 5432 포트를 연결합니다. 외부(DBeaver 등)에서 직접 DB에 접속할 수 있게 해줍니다.
- **volumes**: `pgdata:/var/lib/postgresql/data`
  컨테이너가 종료되거나 삭제되어도 데이터가 날아가지 않도록, 호스트 머신에 볼륨(`pgdata`)을 만들어 데이터를 영구 저장합니다.
- **healthcheck**:
  데이터베이스가 컨테이너로 띄워지고 나서, 실제로 연결을 받을 수 있는 상태인지 검사합니다.

## 2. backend (Flask 서버)

- **build**: `./backend`
  `backend` 폴더 안에 있는 `Dockerfile`을 이용해 이미지를 직접 빌드합니다.
- **ports**: `"5001:5001"`
  호스트 컴퓨터의 5001 포트와 컨테이너의 5001 포트를 연결합니다. (로컬에서 백엔드 API만 따로 테스트해 볼 수 있습니다)
- **environment**:
  Flask 앱 실행 파일(`app.py`), DB 접속 정보 등 백엔드가 작동하는 데 필요한 환경 변수들을 설정합니다. 여기서 `DB_HOST: db`로 설정되어 있는데, 이는 Docker 네트워크 상에서 컨테이너 이름(`db`)만으로 데이터베이스와 통신할 수 있음을 의미합니다.
- **volumes**: `./backend:/app`
  내 컴퓨터의 `./backend` 폴더와 컨테이너 내부의 `/app` 폴더를 동기화합니다. 즉 서버를 껐다 켜지 않아도 코드를 수정하면 실시간으로 반영됩니다(Hot Reload).
- **depends_on**: `db`
  데이터베이스 컨테이너가 먼저 실행되고 정상 상태(`service_healthy`)가 된 이후에 백엔드 서버를 켭니다.

## 3. frontend (Next.js 애플리케이션)

- **build**: `./frontend`
  `frontend` 폴더 안에 있는 `Dockerfile`을 이용해 이미지를 직접 빌드합니다.
- **ports**: `"3000:3000"`
  호스트 컴퓨터의 3000 포트와 웹 브라우저가 접속할 수 있는 컨테이너의 포트를 연결합니다.
- **volumes**:
  - `./frontend:/app` : 로컬의 코드를 컨테이너에 동기화합니다.
  - `/app/node_modules`, `/app/.next` : 컨테이너 내부에 생성된 의존성과 빌드 산출물을 내 컴퓨터의 파일들로 덮어쓰지 않도록(충돌 방지) 별도 볼륨으로 잡습니다.
- **depends_on**: `backend`
  백엔드 컨테이너가 먼저 실행된 후에 프론트엔드를 실행합니다.

## 볼륨 정리

```yaml
volumes:
  pgdata:
```

하단에 선언된 `volumes: pgdata:` 부분은 Docker가 관리하는 '이름 있는 볼륨(Named Volume)'을 선언하는 곳입니다. 위에서 `db` 서비스가 데이터를 영구적으로 저장하기 위해 사용합니다.
