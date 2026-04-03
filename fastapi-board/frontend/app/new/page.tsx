"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { createPost } from "@/lib/api";
import PostForm from "@/components/PostForm";

export default function NewPostPage() {
  const router = useRouter();

  async function handleSubmit(title: string, content: string) {
    try {
      await createPost({ title, content });
      router.push("/");
      router.refresh();
    } catch {
      throw new Error("게시글 등록에 실패했습니다. 다시 시도해주세요.");
    }
  }

  return (
    <main className="max-w-2xl mx-auto px-4 py-12">
      <header className="flex items-center justify-between mb-10 border-b border-black pb-6">
        <h1 className="text-2xl font-bold tracking-tight">글쓰기</h1>
        <Link
          href="/"
          className="text-sm opacity-60 hover:opacity-100 transition-opacity"
        >
          ← 목록으로
        </Link>
      </header>

      <PostForm
        onSubmit={handleSubmit}
        submitLabel="등록하기"
        loadingLabel="등록 중..."
      />
    </main>
  );
}
