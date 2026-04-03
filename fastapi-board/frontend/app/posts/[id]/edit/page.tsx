"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { use } from "react";
import { getPost, updatePost } from "@/lib/api";
import PostForm from "@/components/PostForm";

interface Props {
  params: Promise<{ id: string }>;
}

export default function EditPostPage({ params }: Props) {
  const { id } = use(params);
  const postId = Number(id);
  const router = useRouter();

  const [initialTitle, setInitialTitle] = useState("");
  const [initialContent, setInitialContent] = useState("");
  const [fetching, setFetching] = useState(true);
  const [fetchError, setFetchError] = useState("");

  useEffect(() => {
    getPost(postId)
      .then((post) => {
        setInitialTitle(post.title);
        setInitialContent(post.content);
      })
      .catch(() => setFetchError("게시글을 불러오지 못했습니다."))
      .finally(() => setFetching(false));
  }, [postId]);

  async function handleSubmit(title: string, content: string) {
    try {
      await updatePost(postId, { title, content });
      router.push(`/posts/${postId}`);
      router.refresh();
    } catch {
      throw new Error("수정에 실패했습니다. 다시 시도해주세요.");
    }
  }

  if (fetching) {
    return (
      <main className="max-w-2xl mx-auto px-4 py-12">
        <p className="text-sm opacity-50">불러오는 중...</p>
      </main>
    );
  }

  if (fetchError) {
    return (
      <main className="max-w-2xl mx-auto px-4 py-12">
        <p className="text-sm text-red-600">{fetchError}</p>
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

      {/* fetching이 false가 된 후에 마운트되므로 initialTitle/initialContent가 올바르게 주입된다 */}
      <PostForm
        initialTitle={initialTitle}
        initialContent={initialContent}
        onSubmit={handleSubmit}
        submitLabel="저장하기"
        loadingLabel="저장 중..."
      />
    </main>
  );
}
