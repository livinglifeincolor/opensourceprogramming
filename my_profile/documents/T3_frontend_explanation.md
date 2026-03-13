# 1. 프론트엔드 API 통신 (`src/lib/api.ts`)

프론트엔드가 백엔드 서버와 데이터를 주고받기 위한 통로(API 서비스) 역할을 하는 파일입니다. `Fetch API`를 사용하여 백엔드의 엔드포인트(URL)로 요청을 보냅니다.

### 핵심 기능 및 코드 분석 (`api.ts`)

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001";

// 1. 공통 요청(Request) 헬퍼 함수
async function request<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  // 브라우저의 내장 fetch 함수를 사용해 백엔드 서버에 비동기 네트워크 요청을 보냅니다.
  // API_BASE와 엔드포인트를 합쳐 완전한 목적지 URL을 만듭니다. (예: http://localhost:5001/api/posts?page=1)
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: { "Content-Type": "application/json" }, // JSON 형태로 통신함을 명시
    credentials: "include", // 백엔드 세션(쿠키)을 인증에 포함하기 위한 필수 설정
    ...options, // GET, POST 등 메서드 정보 및 전송 데이터를 덮어씁니다.
  });
  // 응답된 데이터를 JSON 형태로 변환하여 반환합니다.
  return res.json();
}

// 2. 게시물 목록 불러오기 (GET)
export async function getPosts(page: number = 1): Promise<PostsResponse> {
  // request 함수를 호출하여 백엔드의 `/api/posts?page=N` 주소로 GET 요청을 전송합니다.
  // 가져온 데이터는 PostsResponse 타입(인터페이스)에 맞게 반환되어 컴포넌트에서 안전하게 사용할 수 있습니다.
  return request<PostsResponse>(`/api/posts?page=${page}`);
}

// 3. 새로운 게시글 작성하기 (POST)
export async function createPost(
  title: string,
  content: string,
): Promise<MutationResponse> {
  // 사용자가 입력한 제목(title)과 내용(content)을 JSON 문자열로 묶어서
  // 백엔드의 `/api/posts` 주소로 POST(생성) 요청을 보냅니다.
  return request<MutationResponse>("/api/posts", {
    method: "POST",
    body: JSON.stringify({ title, content }),
  });
}
```

### JavaScript의 진화: 브라우저에서 서버까지

초창기의 JavaScript(JS)는 오직 **웹 브라우저 안에서만** 동작하도록 만들어진 프론트엔드 전용 언어였습니다.
하지만 2009년, 크롬 브라우저의 JS 핵심 엔진(V8)만을 따로 떼어내어 일반 프로그램처럼 실행할 수 있게 만든 **Node.js**가 등장하면서 혁명이 일어났습니다.

이 덕분에 JS는 브라우저를 벗어나 **서버(백엔드)** 등 컴퓨터 환경 어디서든 돌아갈 수 있는 범용 언어가 되었고, 개발자들은 JS 하나만으로 프론트엔드와 백엔드를 모두 개발할 수 있는 풀스택의 길을 걷게 되었습니다.

### Next.js에서의 `fetch` 동작 방식 (브라우저 vs 서버)

`lib/api.ts`에 작성된 `fetch` 함수 자체는 자바스크립트 표준(Web API) 문법을 따르지만, 이 함수가 **어디서 호출되느냐**에 따라 실제로 동작하는 주체가 다릅니다.

- **클라이언트 컴포넌트(`"use client"`가 선언된 곳)** 에서 호출할 때 (예: `src/app/posts/page.tsx`):
  해당 코드는 사용자의 브라우저에서 실행되므로, **브라우저에 내장된 기본 `fetch`** 기능이 작동합니다.
- **서버 컴포넌트(`"use client"`가 없는 곳)** 에서 호출할 때:
  해당 코드는 Next.js 서버(Node.js) 단에서 실행됩니다. 브라우저가 없기 때문에 브라우저의 `fetch`를 쓸 수 없으며, 대신 **Next.js 프레임워크가 Node.js 환경에 맞게 캐싱(Caching) 등의 기능을 더해 개조(확장)한 서버용 `fetch`** 가 작동합니다.

### 비동기 통신(`async/await`)의 작동 원리 (폴링 방식이 아님!)

위 코드에서 `await fetch(...)`는 백엔드에서 데이터가 올 때까지 코드를 멈추고 기다립니다. 하지만 자바스크립트는 주기적으로 "데이터 왔어?" 하고 계속 물어보는 **폴링(Polling) 방식을 사용하지 않습니다.** 대신 아래와 같은 **이벤트 위임(Delegation)과 콜백** 리듬으로 똑똑하게 동작합니다.

이러한 자바스크립트 특유의 동작 방식을 크게 두 가지 핵심 용어로 부릅니다:

1. **논블로킹 I/O (Non-Blocking I/O)**: 네트워크 통신(I/O) 같은 오래 걸리는 작업을 던져두고, 메인 스레드는 멈추지 않고 자기 할 일(화면 렌더링 등)을 계속하는 특성입니다.
2. **이벤트 기반 (Event-Driven) 구조**: 작업이 완료되었는지 폴링으로 묻지 않고, 백그라운드 작업이 완료되었을 때 발생하는 '이벤트(쪽지)'를 통해 작업 재개를 알리는 구조입니다.

**4단계 통신 과정**

1. **작업의 위임 (Web API)**: 메인 스레드는 네트워크 통신을 직접 하지 않고 브라우저/OS의 백그라운드(Web API)로 넘깁니다.
2. **실행 일시 정지 (Suspend)**: `await`를 만난 함수는 그 줄에서 실행 상태를 메모리에 저장해 둔 채 **일시 정지**하고, 메인 스레드를 비워줍니다. (이 덕분에 화면이 멈추거나 버벅이지 않습니다)
3. **작업 완료 및 큐 대기**: 백그라운드 통신이 끝나면, 백그라운드는 메인 스레드를 직접 깨우지 않고 **마이크로태스크 큐(Microtask Queue)**라는 대기실에 "이 작업 다 끝났음!" 이라는 쪽지(Promise 완료 이벤트)를 밀어 넣습니다.
4. **이벤트 루프에 의한 재개 (Resume)**: 자바스크립트의 감시자인 **이벤트 루프(Event Loop)**가 메인 스레드가 한가해진 틈을 타 대기실(큐)을 확인합니다. 쪽지를 발견하면 아까 정지시켜 두었던 함수를 다시 메인 스레드로 끌어올려 **`await` 다음 줄부터 코드를 다시 실행**합니다.

### 폴링(Polling)과 이벤트 기반(Event-Driven)의 차이점

- **폴링(Polling)**: "가게에 음식 나왔나요?" 하고 1초마다 계속 전화를 걸어 물어보는(Pull) 방식입니다. CPU 자원이 낭비되고 비효율적입니다(Blocking).
- **이벤트 기반(Event-Driven)**: 진동벨을 받고 내 할 일을 하다가, 음식이 완료되어 "진동벨이 울리면(Push Event)" 가서 받아오는 방식입니다. 기다리는 동안 다른 일을 할 수 있어 효율이 극대화됩니다(Non-Blocking).

### Promise 객체와 Microtask Queue의 관계

`await fetch(...)`가 어떻게 완료 시점을 알고 실행을 재개하는지의 핵심 열쇠가 바로 **Promise 객체**입니다.

**Promise의 3가지 상태**

Promise 객체는 생성 직후부터 아래 3가지 상태 중 하나를 지닙니다.

- **대기 (Pending)**: `fetch()`를 호출한 직후. 백그라운드에서 서버와 통신이 진행 중인 상태이며, 빈 상자(Promise 객체)만 먼저 반환됩니다.
- **이행 (Fulfilled)**: 서버에서 데이터를 성공적으로 받아온 상태. 이 시점에 Promise 객체 안에 성공 결과값(응답 데이터)이 담깁니다.
- **거부 (Rejected)**: 네트워크 오류나 서버 에러 등으로 통신에 실패한 상태. 이 시점에 Promise 객체 안에 에러(Error) 정보가 담깁니다.

**Promise 이행 → Microtask Queue → 실행 재개의 연결 구조**

Promise 상태가 **'대기(Pending)'에서 '이행(Fulfilled)'으로 전환되는 그 찰나**가 바로 마이크로태스크 큐와 연결되는 핵심 시점입니다.

1. 백그라운드(Web API)가 통신을 마치면 Promise 객체의 상태를 `Pending` → `Fulfilled`로 전환합니다.
2. 자바스크립트 엔진은 이 상태 전환을 감지하고, 해당 Promise에 묶여 있던 후속 작업(`await` 이후의 코드)을 **마이크로태스크 큐(Microtask Queue)** 에 등록합니다.
3. 이벤트 루프는 메인 스레드가 비는 순간, **마이크로태스크 큐를 항상 최우선으로** 처리합니다.

**Microtask Queue vs Macrotask Queue**

자바스크립트에는 대기열이 두 종류 있으며, 이벤트 루프의 처리 우선순위가 다릅니다.

| 구분          | Microtask Queue        | Macrotask Queue                                 |
| ------------- | ---------------------- | ----------------------------------------------- |
| 담기는 작업   | Promise 완료 후속 처리 | `setTimeout`, `setInterval`, DOM 클릭 이벤트 등 |
| 처리 우선순위 | 항상 먼저 처리 (VIP)   | Microtask Queue가 빈 다음에 처리                |

이 규칙 덕분에 Promise 결과를 화면에 즉시 반영하면서도, 일반 타이머나 이벤트들과 순서가 꼬이지 않고 예측 가능하게 동작하는 것입니다.

**동작 전체 흐름 요약**

```
fetch() 호출
  → Pending 상태의 Promise 반환 + await로 함수 일시 정지(Suspend)
  → 백그라운드(Web API)에서 통신 진행
  → 통신 완료 → Promise 상태 Fulfilled로 전환
  → 후속 코드가 Microtask Queue에 등록
  → 이벤트 루프가 Microtask Queue 확인
  → 일시 정지했던 함수 재개(Resume), await 아랫줄부터 실행
```

# 2. 레이아웃과 페이지 진입점 (`src/app/layout.tsx` & `page.tsx`)

Next.js 프로젝트의 전체 구조와 사이트의 첫 진입 경로를 제어하는 파일입니다.

### 전체 레이아웃 구성 (`layout.tsx`)

레이아웃은 모든 페이지에 공통으로 적용되는 뼈대(틀) 역할을 합니다. 네비게이션 바와 같은 공통 요소를 여기서 한 번만 선언하여 모든 페이지에 적용시킵니다.

```tsx
import Navbar from "./components/Navbar";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body>
        {/* 모든 페이지 상단에 공통으로 네비게이션 바(메뉴)를 배치합니다. */}
        <Navbar />

        {/* 각 페이지별 메인 콘텐츠가 children 안으로 쏙 들어가서 화면에 그려지게 됩니다. */}
        {children}
      </body>
    </html>
  );
}
```

### 진입 페이지 리다이렉션 (`page.tsx`)

마치 웹사이트에 처음 접속했을 때 메인 로비로 안내하는 역할을 합니다. 가장 처음 접속되는 `/` 경로일 때의 동작입니다.

```tsx
"use client"; // 이 파일이 브라우저에서 실행되는 클라이언트 컴포넌트임을 명시합니다.

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  // useEffect: 이 Home 컴포넌트가 처음 화면에 나타날 때(마운트될 때) 즉시 실행됩니다.
  useEffect(() => {
    // 사용자가 최상단 주소('/')로 접속하면 자동으로 게시판 목록('/posts') 주소로 위치를 옮깁니다(리다이렉션).
    router.replace("/posts");
  }, [router]);

  // 페이지 내용이 보일 필요 없이 바로 이동하므로 화면엔 아무것도 그리지 않습니다.
  return null;
}
```

# 3. 화면 구성 및 사용자 상호작용 (`src/app/posts/page.tsx`)

가져온 데이터를 실제 HTML 화면 요소로 만들고(렌더링), 사용자의 클릭 등 이벤트에 반응하는 `React` 컴포넌트입니다.

### 게시글 목록 조회 및 화면 렌더링

```tsx
"use client";

import { useEffect, useState } from "react";
import { getPosts, type Post } from "@/lib/api";

function PostsList() {
  // 1. 상태(State) 선언: 화면에 보여줄 데이터들을 컴포넌트 내부의 변수로 관리합니다.
  // 상태가 업데이트되면 React가 자동으로 파악해 화면을 다시(새롭게) 그려줍니다.
  const [posts, setPosts] = useState<Post[]>([]); // 빈 배열로 초기화
  const [loading, setLoading] = useState(true); // 데이터를 받아오는 동안은 로딩 상태로 둡니다.

  // 2. 데이터 가져오기 (사이드 이펙트 관리)
  useEffect(() => {
    // 앞서 정의한 API 통신 함수(getPosts)를 호출해 백엔드 서버에서 1페이지의 데이터를 직접 요청합니다.
    getPosts(1).then((res) => {
      // 서버에서 정상적으로 데이터가 담긴 응답배열이 도착했다면,
      // React 상태(posts)를 그 데이터로 업데이트합니다.
      if (res.posts) {
        setPosts(res.posts);
      }
      setLoading(false); // 데이터 수신이 완료되었으므로 로딩 처리를 종료합니다.
    });
  }, []); // 빈 배열([])은 컴포넌트가 화면에 처음 나타날 때 딱 한 번만 실행됨을 의미합니다.

  // 3. JSX로 화면 렌더링 (HTML 태그와 유사함)
  return (
    <div className="board-container">
      {/* 현재 데이터 통신이 진행중(loading === true)이라면 로딩 메시지를 보여주고, */}
      {loading ? (
        <div className="board-loading">불러오는 중...</div>
      ) : (
        /* 완료되었다면 posts 변수에 들어있는 배열을 map()으로 순회하면서 
           <tr>(행), <td>(열) 테이블 코드로 가공하여 화면에 나타냅니다. */
        <table className="posts-table">
          <tbody>
            {posts.map((post) => (
              <tr key={post.id}>
                {/* 각 게시물의 제목과 작성자 정보를 꺼내어 표 안에 넣습니다. */}
                <td className="col-title">{post.title}</td>
                <td className="col-author">{post.author}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
```
