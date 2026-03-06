"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { getPost, deletePost, getMe, type Post } from "@/lib/api";

export default function PostDetailPage() {
  const params = useParams();
  const router = useRouter();
  const postId = Number(params.id);

  const [post, setPost] = useState<Post | null>(null);
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getMe().then((res) => {
      if (res.user) setCurrentUserId(res.user.id);
    });

    getPost(postId).then((res) => {
      if (res.error) {
        setError(res.error);
      } else {
        setPost(res.post);
      }
      setLoading(false);
    });
  }, [postId]);

  const handleDelete = async () => {
    if (!confirm("정말 삭제하시겠습니까?")) return;

    const res = await deletePost(postId);
    if (res.error) {
      alert(res.error);
    } else {
      router.push("/posts");
    }
  };

  const formatDate = (iso: string) => {
    const d = new Date(iso);
    return d.toLocaleDateString("ko-KR", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (loading) {
    return (
      <div className="post-detail-container">
        <div className="post-detail-loading">불러오는 중...</div>
      </div>
    );
  }

  if (error || !post) {
    return (
      <div className="post-detail-container">
        <div className="post-detail-error">
          <p>{error || "게시글을 찾을 수 없습니다."}</p>
          <Link href="/posts" className="btn-back">
            ← 목록으로
          </Link>
        </div>
      </div>
    );
  }

  const isOwner = currentUserId === post.user_id;

  return (
    <div className="post-detail-container">
      <article className="post-detail">
        <header className="post-detail-header">
          <h1>{post.title}</h1>
          <div className="post-meta">
            <span className="post-author">{post.author}</span>
            <span className="post-date">{formatDate(post.created_at)}</span>
            {post.updated_at !== post.created_at && (
              <span className="post-edited">(수정됨)</span>
            )}
          </div>
        </header>

        <div className="post-content">
          {(post.content ?? "").split("\n").map((line, i) => (
            <p key={i}>{line || "\u00A0"}</p>
          ))}
        </div>

        <footer className="post-detail-footer">
          <Link href="/posts" className="btn-back">
            ← 목록으로
          </Link>
          {isOwner && (
            <div className="post-actions">
              <Link href={`/posts/write?edit=${post.id}`} className="btn-edit">
                수정
              </Link>
              <button className="btn-delete" onClick={handleDelete}>
                삭제
              </button>
            </div>
          )}
        </footer>
      </article>
    </div>
  );
}
