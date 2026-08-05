"use client";

import Image from "next/image";
import Icon from "@/components/ui/Icon";
import ThemeToggle from "@/components/ThemeToggle";

export default function OnboardingTopBar() {
  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-border/60 bg-card/70 px-4 backdrop-blur-xl sm:px-6">
      <div className="flex items-center gap-3 sm:gap-5">
        <Image
          src="/logo-wordmark.webp"
          alt="UCust"
          width={700}
          height={161}
          unoptimized
          className="h-7 w-auto dark:hidden"
        />
        <Image
          src="/brand/logo-lighttext.webp"
          alt="UCust"
          width={700}
          height={161}
          unoptimized
          className="hidden h-7 w-auto dark:block"
        />
      </div>
      <div className="flex items-center gap-2 sm:gap-3">
        <ThemeToggle />
        <button
          type="button"
          aria-label="Уведомления"
          className="relative flex h-9 w-9 items-center justify-center rounded-full text-ink-muted transition-colors hover:bg-surface-soft hover:text-ink"
        >
          <Icon name="bell" size={18} aria-hidden="true" />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-brand" />
        </button>
        <div className="flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-full bg-brand text-sm font-semibold text-white">
            АИ
          </span>
          <span className="hidden text-sm font-medium text-ink sm:block">Анна Иванова</span>
        </div>
      </div>
    </header>
  );
}
