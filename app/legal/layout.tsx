import type { Metadata } from "next";
import type { ReactNode } from "react";
import Link from "next/link";
import Image from "next/image";
import Icon from "@/components/ui/Icon";
import Footer from "@/components/Footer";

export const metadata: Metadata = { robots: { index: false, follow: true } };

export default function LegalLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-dvh flex-col bg-canvas">
      <header className="bg-canvas pt-3">
        <div className="mx-auto max-w-(--container-page) px-5 sm:px-6">
          <div className="flex h-14 items-center justify-between rounded-[24px] border border-white/10 bg-card/80 px-5 shadow-soft ring-1 ring-white/5 backdrop-blur-xl sm:px-6">
            <Link href="/" aria-label="UCust — на главную" className="inline-flex items-center">
              <Image src="/logo-wordmark.webp" alt="UCust" width={700} height={161} unoptimized className="h-6 w-auto sm:h-7 dark:hidden" />
              <Image src="/brand/logo-lighttext.webp" alt="UCust" width={700} height={161} unoptimized className="hidden h-6 w-auto sm:h-7 dark:block" />
            </Link>
            <Link href="/" className="inline-flex items-center gap-1.5 text-sm font-medium text-ink-muted transition-colors hover:text-brand">
              <Icon name="arrow-left" size={16} aria-hidden="true" /> На главную
            </Link>
          </div>
        </div>
      </header>
      <main className="flex-1">{children}</main>
      <Footer />
    </div>
  );
}
