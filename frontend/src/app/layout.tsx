import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "My Development Journal",
  description: "개인 개발 기록 플랫폼",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
