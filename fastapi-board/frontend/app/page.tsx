import { Suspense } from "react";
import Link from "next/link";
import { getPosts, getPostsCount, searchPosts, Post } from "@/lib/api";
import PostCard from "@/components/PostCard";
import Pagination from "@/components/Pagination";
import SearchBar from "@/components/SearchBar";

const PAGE_SIZE = 10;

interface Props {
  searchParams: Promise<{ page?: string; q?: string }>;
}

export const dynamic = "force-dynamic";

export default async function HomePage({ searchParams }: Props) {
  const { page: pageParam, q } = await searchParams;
  const currentPage = Math.max(1, Number(pageParam) || 1);
  const isSearchMode = typeof q === "string" && q.trim().length > 0;

  let posts: Post[] = [];
  let totalPages = 1;
  let searchTotal = 0;
  let fetchError: string | null = null;

  try {
    if (isSearchMode) {
      // 검색 모드: /api/posts/search?q=...
      const result = await searchPosts(q, currentPage, PAGE_SIZE);
      posts = result.results;
      searchTotal = result.total;
      totalPages = Math.max(1, Math.ceil(searchTotal / PAGE_SIZE));
    } else {
      // 일반 목록 모드
      const [data, countData] = await Promise.all([
        getPosts(currentPage, PAGE_SIZE),
        getPostsCount(),
      ]);
      posts = data;
      totalPages = Math.max(1, Math.ceil(countData.total / PAGE_SIZE));
    }
  } catch (err) {
    console.error("[HomePage] Failed to load posts:", err);
    fetchError = "게시글을 불러오는 데 실패했습니다. 잠시 후 다시 시도해주세요.";
  }

  return (
    <main className="max-w-2xl mx-auto px-4 py-12">
      <header className="flex items-center justify-between mb-6 border-b border-black pb-6">
        <h1 className="text-2xl font-bold tracking-tight">게시판</h1>
        <Link
          href="/new"
          className="border border-black px-4 py-2 text-sm font-medium hover:bg-black hover:text-white transition-colors duration-200"
        >
          글쓰기
        </Link>
      </header>

      {/* 검색창 — useSearchParams 사용으로 Suspense 필요 */}
      <Suspense fallback={<div className="h-12 mb-8" />}>
        <SearchBar />
      </Suspense>

      {/* 검색 결과 헤더 */}
      {isSearchMode && (
        <p className="text-sm opacity-60 mb-4">
          &ldquo;{q}&rdquo; 검색 결과 {searchTotal}건
        </p>
      )}

      {/* 게시글 목록 */}
      {fetchError ? (
        <p className="text-center text-sm text-red-600 py-20" role="alert">
          {fetchError}
        </p>
      ) : posts.length === 0 ? (
        <p className="text-center text-sm opacity-50 py-20">
          {isSearchMode ? "검색 결과가 없습니다." : "아직 게시글이 없습니다."}
        </p>
      ) : (
        <ul className="flex flex-col gap-4">
          {posts.map((post) => (
            <li key={post.id}>
              <PostCard post={post} />
            </li>
          ))}
        </ul>
      )}

      <Pagination currentPage={currentPage} totalPages={totalPages} />
    </main>
  );
}
