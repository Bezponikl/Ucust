import type { Metadata } from "next";
import { Onest, Golos_Text, JetBrains_Mono } from "next/font/google";
import AuthModalProvider from "@/components/AuthModalProvider";
import "./globals.css";

const onest = Onest({
  variable: "--font-onest",
  subsets: ["latin", "cyrillic"],
  weight: ["600", "700", "800"],
  display: "swap",
});

const golos = Golos_Text({
  variable: "--font-golos",
  subsets: ["latin", "cyrillic"],
  weight: ["400", "500"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains",
  subsets: ["latin", "cyrillic"],
  weight: ["400", "500"],
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
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="ru"
      className={`${onest.variable} ${golos.variable} ${jetbrainsMono.variable}`}
    >
      <body className="min-h-screen bg-canvas text-ink antialiased">
        <AuthModalProvider>{children}</AuthModalProvider>
      </body>
    </html>
  );
}
