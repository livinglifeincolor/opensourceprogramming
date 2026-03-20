"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState, FormEvent } from "react";

export default function SearchBar() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [query, setQuery] = useState(searchParams.get("q") ?? "");
  const [error, setError] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();

    // 클라이언트 측 검증: 빈 문자열 방지
    if (query.trim() === "") {
      setError("검색어를 입력해주세요.");
      return;
    }

    setError("");
    router.push(`/?q=${encodeURIComponent(query.trim())}&page=1`);
  }

  function handleClear() {
    setQuery("");
    setError("");
    router.push("/");
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-1 mb-8">
      <div className="flex gap-2">
        <input
          id="search-input"
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            if (error) setError("");
          }}
          placeholder="제목 또는 내용으로 검색..."
          className="flex-1 border border-black px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-black"
        />
        <button
          type="submit"
          className="border border-black px-4 py-2 text-sm font-medium hover:bg-black hover:text-white transition-colors duration-200"
        >
          검색
        </button>
        {searchParams.get("q") && (
          <button
            type="button"
            onClick={handleClear}
            className="border border-black px-3 py-2 text-sm hover:bg-black hover:text-white transition-colors duration-200"
          >
            ✕
          </button>
        )}
      </div>

      {/* 클라이언트 측 검증 에러 메시지 */}
      {error && (
        <p className="text-sm text-red-600" role="alert">
          {error}
        </p>
      )}
    </form>
  );
}
