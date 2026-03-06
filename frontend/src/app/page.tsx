"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getMe, logout } from "@/lib/api";

export default function Home() {
  const router = useRouter();
  const [user, setUser] = useState<{
    username: string;
    email: string;
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMe().then((res) => {
      if (res.user) {
        setUser(res.user);
      } else {
        router.replace("/login");
      }
      setLoading(false);
    });
  }, [router]);

  const handleLogout = async () => {
    await logout();
    router.replace("/login");
  };

  if (loading) {
    return (
      <div className="welcome-container">
        <div className="welcome-card">
          <p>로딩 중...</p>
        </div>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="welcome-container">
      <div className="welcome-card">
        <div className="avatar">{user.username.charAt(0).toUpperCase()}</div>
        <h1>환영합니다, {user.username}님!</h1>
        <p>{user.email}</p>
        <button className="btn-logout" onClick={handleLogout}>
          로그아웃
        </button>
      </div>
    </div>
  );
}
