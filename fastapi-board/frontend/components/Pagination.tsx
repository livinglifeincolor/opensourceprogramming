import Link from "next/link";

interface PaginationProps {
  currentPage: number;
  totalPages: number;
}

export default function Pagination({ currentPage, totalPages }: PaginationProps) {
  if (totalPages <= 1) return null;

  const pages = Array.from({ length: totalPages }, (_, i) => i + 1);

  return (
    <nav className="flex items-center justify-center gap-1 mt-10">
      <Link
        href={`/?page=${currentPage - 1}`}
        aria-disabled={currentPage === 1}
        className={`px-3 py-2 text-sm border border-black transition-colors duration-150 ${
          currentPage === 1
            ? "opacity-30 pointer-events-none"
            : "hover:bg-black hover:text-white"
        }`}
      >
        ← 이전
      </Link>

      {pages.map((page) => (
        <Link
          key={page}
          href={`/?page=${page}`}
          className={`px-3 py-2 text-sm border border-black transition-colors duration-150 ${
            page === currentPage
              ? "bg-black text-white"
              : "hover:bg-black hover:text-white"
          }`}
        >
          {page}
        </Link>
      ))}

      <Link
        href={`/?page=${currentPage + 1}`}
        aria-disabled={currentPage === totalPages}
        className={`px-3 py-2 text-sm border border-black transition-colors duration-150 ${
          currentPage === totalPages
            ? "opacity-30 pointer-events-none"
            : "hover:bg-black hover:text-white"
        }`}
      >
        다음 →
      </Link>
    </nav>
  );
}
