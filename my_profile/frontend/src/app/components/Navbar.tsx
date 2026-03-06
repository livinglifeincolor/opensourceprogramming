"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { getMe, logout } from "@/lib/api";

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<{
    id: number;
    username: string;
  } | null>(null);

  useEffect(() => {
    getMe().then((res) => {
      if (res.user) {
        setUser({ id: res.user.id, username: res.user.username });
      } else {
        setUser(null);
      }
    });
  }, [pathname]);

  const handleLogout = async () => {
    await logout();
    setUser(null);
    router.push("/login");
  };

  // 로그인/회원가입 페이지에서는 네비게이션 바 숨기기
  if (pathname === "/login" || pathname === "/register") {
    return null;
  }

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link href="/posts" className="navbar-logo">
          📝 Dev Journal
        </Link>

        <div className="navbar-links">
          <Link
            href="/posts"
            className={`navbar-link ${pathname === "/posts" ? "active" : ""}`}
          >
            게시판
          </Link>
        </div>

        <div className="navbar-auth">
          {user ? (
            <>
              <span className="navbar-user">{user.username}</span>
              <button className="navbar-btn" onClick={handleLogout}>
                로그아웃
              </button>
            </>
          ) : (
            <Link href="/login" className="navbar-btn">
              로그인
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}
