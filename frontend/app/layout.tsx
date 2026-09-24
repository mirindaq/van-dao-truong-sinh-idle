import "./globals.css";
import type { Metadata } from "next";
import localFont from "next/font/local";
import { MotionProvider } from "@/lib/motion";

const literary = localFont({
  src: "../public/assets/fonts/noto-serif-regular.ttf",
  variable: "--font-literary",
  weight: "400",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Vạn Đạo Trường Sinh",
  description: "Game idle tu tiên một người chơi"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi" className={literary.variable}>
      <body><MotionProvider>{children}</MotionProvider></body>
    </html>
  );
}
