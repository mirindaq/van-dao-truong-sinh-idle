import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Vạn Đạo Trường Sinh",
  description: "Game idle tu tiên một người chơi"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi">
      <body>{children}</body>
    </html>
  );
}
