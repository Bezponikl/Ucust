import type { Metadata } from "next";
import { Manrope } from "next/font/google";
import AuthModalProvider from "@/components/AuthModalProvider";
import ScrollTop from "@/components/ScrollTop";
import { SessionProvider } from "@/lib/session/SessionProvider";
import "./globals.css";

// Тема идёт за системной настройкой устройства — ручного переключателя нет.
// Класс ставим до первой отрисовки (иначе вспышка светлой темы) и подписываемся
// на смену системной темы, чтобы страница переключалась без перезагрузки.
// Старый ключ localStorage чистим: иначе у тех, кто раньше переключал вручную,
// осталась бы залипшая тема поверх системной.
const themeScript = `(function(){try{localStorage.removeItem('theme')}catch(e){}try{var m=window.matchMedia('(prefers-color-scheme: dark)');var a=function(d){document.documentElement.classList.toggle('dark',d)};a(m.matches);var h=function(e){a(e.matches)};if(m.addEventListener)m.addEventListener('change',h);else m.addListener(h)}catch(e){}})();`;

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
    <html lang="ru" className={`${manrope.variable} overflow-x-clip`} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
        {/* Литеральные семейства для анимированных сцен возможностей (Caveat — рукопись) */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Caveat:wght@400;600;700&family=Manrope:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen overflow-x-clip bg-canvas text-ink antialiased">
        <SessionProvider>
          <AuthModalProvider>{children}</AuthModalProvider>
        </SessionProvider>
        <ScrollTop />
      </body>
    </html>
  );
}
