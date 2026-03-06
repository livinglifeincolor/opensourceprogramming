"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { getPosts, getMe, type Post } from "@/lib/api";

function PostsList() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const currentPage = Number(searchParams.get("page")) || 1;

  const [posts, setPosts] = useState<Post[]>([]);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [loggedIn, setLoggedIn] = useState(false);

  useEffect(() => {
    getMe().then((res) => setLoggedIn(!!res.user));
  }, []);

  useEffect(() => {
    getPosts(currentPage).then((res) => {
      if (res.posts) {
        setPosts(res.posts);
        setTotalPages(res.total_pages);
        setTotal(res.total);
      }
      setLoading(false);
    });
  }, [currentPage]);

  const goToPage = (page: number) => {
    router.push(`/posts?page=${page}`);
  };

  const formatDate = (iso: string) => {
    const d = new Date(iso);
    return d.toLocaleDateString("ko-KR", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    });
  };

  const getPostNumber = (index: number) => {
    return total - (currentPage - 1) * 10 - index;
  };

  return (
    <div className="board-container">
      <div className="board-header">
        <h1>게시판</h1>
        {loggedIn && (
          <Link href="/posts/write" className="btn-write">
            ✏️ 글쓰기
          </Link>
        )}
      </div>

      {loading ? (
        <div className="board-loading">불러오는 중...</div>
      ) : posts.length === 0 ? (
        <div className="board-empty">
          <p>아직 게시글이 없습니다.</p>
          {loggedIn && (
            <Link href="/posts/write" className="btn-write-first">
              첫 글을 작성해보세요!
            </Link>
          )}
        </div>
      ) : (
        <>
          <table className="posts-table">
            <thead>
              <tr>
                <th className="col-no">번호</th>
                <th className="col-title">제목</th>
                <th className="col-author">작성자</th>
                <th className="col-date">날짜</th>
              </tr>
            </thead>
            <tbody>
              {posts.map((post, i) => (
                <tr
                  key={post.id}
                  onClick={() => router.push(`/posts/${post.id}`)}
                >
                  <td className="col-no">{getPostNumber(i)}</td>
                  <td className="col-title">
                    <Link href={`/posts/${post.id}`}>{post.title}</Link>
                  </td>
                  <td className="col-author">{post.author}</td>
                  <td className="col-date">{formatDate(post.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {totalPages > 1 && (
            <div className="pagination">
              <button
                className="page-btn"
                disabled={currentPage <= 1}
                onClick={() => goToPage(currentPage - 1)}
              >
                ‹ 이전
              </button>
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
                <button
                  key={p}
                  className={`page-btn ${p === currentPage ? "active" : ""}`}
                  onClick={() => goToPage(p)}
                >
                  {p}
                </button>
              ))}
              <button
                className="page-btn"
                disabled={currentPage >= totalPages}
                onClick={() => goToPage(currentPage + 1)}
              >
                다음 ›
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default function PostsPage() {
  return (
    <Suspense fallback={<div className="board-loading">불러오는 중...</div>}>
      <PostsList />
    </Suspense>
  );
}
