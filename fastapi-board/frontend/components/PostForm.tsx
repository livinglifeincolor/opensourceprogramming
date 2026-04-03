"use client";

import { useState, FormEvent } from "react";

export const TITLE_MAX = 100;
export const CONTENT_MIN = 10;

interface PostFormProps {
  initialTitle?: string;
  initialContent?: string;
  /** title, content를 받아 제출 처리. 실패 시 Error를 throw하면 폼에 에러 메시지를 표시한다. */
  onSubmit: (title: string, content: string) => Promise<void>;
  submitLabel: string;
  loadingLabel: string;
}

export default function PostForm({
  initialTitle = "",
  initialContent = "",
  onSubmit,
  submitLabel,
  loadingLabel,
}: PostFormProps) {
  const [title, setTitle] = useState(initialTitle);
  const [content, setContent] = useState(initialContent);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const isValid =
    title.trim().length > 0 && content.trim().length >= CONTENT_MIN;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!isValid) {
      setError(`제목을 입력하고 내용을 ${CONTENT_MIN}자 이상 작성해주세요.`);
      return;
    }
    setLoading(true);
    setError("");
    try {
      await onSubmit(title, content);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "오류가 발생했습니다. 다시 시도해주세요."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6">
      {/* 제목 */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <label htmlFor="title" className="text-sm font-medium">
            제목
          </label>
          <span
            className={`text-xs ${
              title.length > TITLE_MAX ? "text-red-600" : "opacity-40"
            }`}
          >
            {title.length}/{TITLE_MAX}
          </span>
        </div>
        <input
          id="title"
          type="text"
          value={title}
          maxLength={TITLE_MAX}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="제목을 입력하세요"
          className="border border-black px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-black placeholder:opacity-30"
        />
      </div>

      {/* 내용 */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <label htmlFor="content" className="text-sm font-medium">
            내용
          </label>
          <span
            className={`text-xs ${
              content.length < CONTENT_MIN && content.length > 0
                ? "text-red-600"
                : "opacity-40"
            }`}
          >
            {content.length}자{" "}
            {content.length < CONTENT_MIN ? `(최소 ${CONTENT_MIN}자)` : ""}
          </span>
        </div>
        <textarea
          id="content"
          rows={8}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="내용을 입력하세요 (최소 10자)"
          className="border border-black px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-black resize-none placeholder:opacity-30"
        />
      </div>

      {/* 에러 메시지 */}
      {error && (
        <p className="text-sm text-red-600" role="alert">
          {error}
        </p>
      )}

      {/* 제출 버튼 */}
      <button
        type="submit"
        disabled={loading || !isValid}
        className="border border-black px-6 py-3 text-sm font-medium bg-black text-white hover:bg-white hover:text-black transition-colors duration-200 disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {loading ? loadingLabel : submitLabel}
      </button>
    </form>
  );
}
