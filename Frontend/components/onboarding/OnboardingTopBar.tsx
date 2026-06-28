"use client";

import Image from "next/image";
import { Bell } from "lucide-react";
import ThemeToggle from "@/components/ThemeToggle";

export default function OnboardingTopBar() {
  return (
    <header className="flex h-16 items-center justify-between border-b border-border bg-card px-4 sm:px-6">
      <div className="flex items-center gap-3 sm:gap-5">
        <Image
          src="/logo-wordmark.webp"
          alt="UCust"
          width={700}
          height={161}
          className="h-6 w-auto dark:hidden"
        />
        <Image
          src="/brand/logo-lighttext.webp"
          alt="UCust"
          width={700}
          height={161}
          className="hidden h-6 w-auto dark:block"
        />
      </div>
      <div className="flex items-center gap-2 sm:gap-3">
        <ThemeToggle />
        <button
          type="button"
          aria-label="Уведомления"
          className="relative flex h-9 w-9 items-center justify-center rounded-full text-ink-muted transition-colors hover:bg-surface-soft hover:text-ink"
        >
          <Bell size={18} aria-hidden="true" />
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
