import Image from "next/image";
import Link from "next/link";
import type { ReactNode } from "react";
import Icon from "@/components/ui/Icon";
import Toaster from "@/components/ui/Toaster";

export default function AuthPageChrome({ children }: { children: ReactNode }) {
  return (
    <div className="uc-brand-canvas relative min-h-dvh">
      <Link
        href="/"
        aria-label="UCust — на главную"
        className="fixed left-5 top-5 z-10 inline-flex items-center sm:left-8 sm:top-8"
      >
        <Image
          src="/logo-wordmark.webp"
          alt="UCust"
          width={700}
          height={161}
          unoptimized
          className="h-7 w-auto sm:h-8 dark:hidden"
        />
        <Image
          src="/brand/logo-lighttext.webp"
          alt="UCust"
          width={700}
          height={161}
          unoptimized
          className="hidden h-7 w-auto sm:h-8 dark:block"
        />
      </Link>

      <Link
        href="/"
        aria-label="Закрыть и вернуться на главную"
        className="fixed right-5 top-5 z-10 flex h-10 w-10 items-center justify-center rounded-full border border-border/60 bg-card/60 text-ink-muted backdrop-blur-md transition-colors hover:bg-card hover:text-ink sm:right-8 sm:top-8"
      >
        <Icon name="close" size={20} aria-hidden="true" />
      </Link>

      <div className="relative z-0 flex min-h-dvh items-center justify-center px-4 py-24 sm:px-6">
        <div className="w-full max-w-md rounded-[32px] border border-border bg-card/85 p-8 shadow-lift backdrop-blur-xl sm:p-10">
          {children}
        </div>
      </div>

      <Toaster />
    </div>
  );
}
