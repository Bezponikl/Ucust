import type { Metadata } from "next";
import { Manrope } from "next/font/google";
import AuthModalProvider from "@/components/AuthModalProvider";
import ScrollTop from "@/components/ScrollTop";
import "./globals.css";

// Ставим тему до первой отрисовки, чтобы не было вспышки светлой темы
const themeScript = `(function(){try{var t=localStorage.getItem('theme');var d=t?t==='dark':window.matchMedia('(prefers-color-scheme: dark)').matches;if(d)document.documentElement.classList.add('dark');}catch(e){}})();`;

const manrope = Manrope({
  variable: "--font-manrope",
  subsets: ["latin", "cyrillic"],
  weight: ["400", "500", "600", "700", "800"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "UCust — ИИ-маркетолог для малого бизнеса",
  description:
    "Расскажите о бизнесе один раз — UCust сам напишет посты в вашем стиле и опубликует их в VK, Telegram, MAX, Дзене и Одноклассниках по расписанию.",
  openGraph: {
    title: "UCust — ИИ-маркетолог для малого бизнеса",
    description:
      "Соцсети вашего бизнеса ведёт ИИ. Первые посты — за 5 минут, без привязки карты.",
    type: "website",
    locale: "ru_RU",
    siteName: "UCust",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru" className={manrope.variable} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body className="min-h-screen bg-canvas text-ink antialiased">
        <AuthModalProvider>{children}</AuthModalProvider>
        <ScrollTop />
      </body>
    </html>
  );
}
