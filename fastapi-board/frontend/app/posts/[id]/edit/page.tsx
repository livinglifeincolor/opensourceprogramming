"use client";

import { useState, useEffect, FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getPost, updatePost } from "@/lib/api";
import { use } from "react";

interface Props {
  params: Promise<{ id: string }>;
}

export default function EditPostPage({ params }: Props) {
  const { id } = use(params);
  const postId = Number(id);
  const router = useRouter();

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [error, setError] = useState("");

  const TITLE_MAX = 100;
  const CONTENT_MIN = 10;
  const isValid = title.trim().length > 0 && content.trim().length >= CONTENT_MIN;

  useEffect(() => {
    getPost(postId)
      .then((post) => {
        setTitle(post.title);
        setContent(post.content);
      })
      .catch(() => setError("게시글을 불러오지 못했습니다."))
      .finally(() => setFetching(false));
  }, [postId]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!isValid) {
      setError(`제목을 입력하고 내용을 ${CONTENT_MIN}자 이상 작성해주세요.`);
      return;
    }
    setLoading(true);
    setError("");
    try {
      await updatePost(postId, { title, content });
      router.push(`/posts/${postId}`);
      router.refresh();
    } catch {
      setError("수정에 실패했습니다. 다시 시도해주세요.");
    } finally {
      setLoading(false);
    }
  }

  if (fetching) {
    return (
      <main className="max-w-2xl mx-auto px-4 py-12">
        <p className="text-sm opacity-50">불러오는 중...</p>
      </main>
    );
  }

  return (
    <main className="max-w-2xl mx-auto px-4 py-12">
      <header className="flex items-center justify-between mb-10 border-b border-black pb-6">
        <h1 className="text-2xl font-bold tracking-tight">게시글 수정</h1>
        <Link
          href={`/posts/${postId}`}
          className="text-sm opacity-60 hover:opacity-100 transition-opacity"
        >
          ← 취소
        </Link>
      </header>

      <form onSubmit={handleSubmit} className="flex flex-col gap-6">
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <label htmlFor="title" className="text-sm font-medium">제목</label>
            <span className={`text-xs ${title.length > TITLE_MAX ? "text-red-600" : "opacity-40"}`}>
              {title.length}/{TITLE_MAX}
            </span>
          </div>
          <input
            id="title"
            type="text"
            value={title}
            maxLength={TITLE_MAX}
            onChange={(e) => setTitle(e.target.value)}
            className="border border-black px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-black"
          />
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <label htmlFor="content" className="text-sm font-medium">내용</label>
            <span className={`text-xs ${content.length < CONTENT_MIN && content.length > 0 ? "text-red-600" : "opacity-40"}`}>
              {content.length}자 {content.length < CONTENT_MIN ? `(최소 ${CONTENT_MIN}자)` : ""}
            </span>
          </div>
          <textarea
            id="content"
            rows={8}
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="border border-black px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-black resize-none"
          />
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={loading || !isValid}
          className="border border-black px-6 py-3 text-sm font-medium bg-black text-white hover:bg-white hover:text-black transition-colors duration-200 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {loading ? "저장 중..." : "저장하기"}
        </button>
      </form>
    </main>
  );
}
