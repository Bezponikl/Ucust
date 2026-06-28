"use client";

import Link from "next/link";
import { Sparkles } from "lucide-react";

export default function OverviewHeader({ businessName }: { businessName: string }) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h1 className="text-2xl font-bold text-ink sm:text-3xl">Добрый день!</h1>
        <p className="mt-1 text-sm text-ink-muted sm:text-base">
          Вот что происходит с бизнесом «{businessName}»
        </p>
      </div>
      <Link
        href="/dashboard/create"
        className="btn-glass-blue inline-flex items-center justify-center gap-2 rounded-xl px-5 py-3 text-sm font-semibold"
      >
        <Sparkles size={16} aria-hidden="true" />
        Создать контент
      </Link>
    </div>
  );
}
