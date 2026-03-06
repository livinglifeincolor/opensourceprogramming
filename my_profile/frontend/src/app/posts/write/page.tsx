"use client";

import { Suspense, useEffect, useState, FormEvent } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { createPost, updatePost, getPost, getMe } from "@/lib/api";

function WriteForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const editId = searchParams.get("edit");

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [pageLoading, setPageLoading] = useState(true);

  const isEdit = !!editId;

  useEffect(() => {
    getMe().then((res) => {
      if (!res.user) {
        router.replace("/login");
        return;
      }

      if (editId) {
        getPost(Number(editId)).then((postRes) => {
          if (postRes.error || !postRes.post) {
            router.replace("/posts");
            return;
          }
          if (postRes.post.user_id !== res.user!.id) {
            router.replace(`/posts/${editId}`);
            return;
          }
          setTitle(postRes.post.title);
          setContent(postRes.post.content || "");
          setPageLoading(false);
        });
      } else {
        setPageLoading(false);
      }
    });
  }, [editId, router]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const res = isEdit
      ? await updatePost(Number(editId), title, content)
      : await createPost(title, content);

    if (res.error) {
      setError(res.error);
      setLoading(false);
    } else {
      router.push(isEdit ? `/posts/${editId}` : "/posts");
    }
  };

  if (pageLoading) {
    return <div className="write-loading">불러오는 중...</div>;
  }

  return (
    <div className="write-card">
      <h1>{isEdit ? "글 수정" : "새 글 작성"}</h1>

      {error && <div className="message error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="post-title">제목</label>
          <input
            id="post-title"
            type="text"
            placeholder="제목을 입력하세요"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            maxLength={200}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="post-content">내용</label>
          <textarea
            id="post-content"
            placeholder="내용을 입력하세요"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={15}
            required
          />
        </div>

        <div className="write-actions">
          <button
            type="button"
            className="btn-cancel"
            onClick={() => router.back()}
          >
            취소
          </button>
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading
              ? isEdit
                ? "수정 중..."
                : "작성 중..."
              : isEdit
                ? "수정하기"
                : "작성하기"}
          </button>
        </div>
      </form>
    </div>
  );
}

export default function WritePostPage() {
  return (
    <div className="write-container">
      <Suspense fallback={<div className="write-loading">불러오는 중...</div>}>
        <WriteForm />
      </Suspense>
    </div>
  );
}
