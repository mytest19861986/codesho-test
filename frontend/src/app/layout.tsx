import type { Metadata } from "next";
import localFont from "next/font/local";
import type { ReactNode } from "react";

import "./styles.css";
import "./ui-001.css";

const vazirmatn = localFont({
  src: "./fonts/Vazirmatn[wght].woff2",
  variable: "--font-vazirmatn",
  display: "swap",
  weight: "100 900",
  fallback: ["Tahoma", "Arial", "sans-serif"],
});

export const metadata: Metadata = {
  title: "کدشو",
  description: "محیط یادگیری پروژه‌محور برنامه‌نویسی",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="fa" dir="rtl" className={vazirmatn.variable}>
      <body>{children}</body>
    </html>
  );
}
