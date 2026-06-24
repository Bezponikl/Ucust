"use client";

import Reveal from "./Reveal";
import { useAuthModal } from "./AuthModalProvider";

export default function FinalCta() {
  const { openSignup } = useAuthModal();

  return (
    <section className="px-4 pb-16 pt-4 sm:px-6 sm:pb-24 sm:pt-6 lg:pb-32">
      <Reveal className="relative mx-auto max-w-(--container-page) overflow-hidden rounded-[28px] bg-gradient-to-br from-hero-from via-hero-via to-hero-to px-6 py-16 text-center shadow-soft sm:rounded-[32px] sm:px-10 sm:py-20 lg:py-24">
        <div aria-hidden="true" className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="absolute -left-24 -top-24 h-[360px] w-[360px] rotate-[18deg] rounded-[56px] bg-[var(--hero-chevron)] sm:h-[440px] sm:w-[440px]" />
          <div className="absolute -bottom-24 -right-16 h-[280px] w-[280px] rotate-[18deg] rounded-[48px] bg-[var(--hero-chevron-soft)] sm:h-[340px] sm:w-[340px]" />
        </div>

        <div className="relative">
          <h2 className="mx-auto max-w-2xl text-3xl font-extrabold leading-tight tracking-tight text-white sm:text-4xl">
            Маркетинг на автопилоте — начните сегодня
          </h2>
          <p className="mx-auto mt-4 max-w-md text-base leading-relaxed text-white/80 sm:text-lg">
            Первые посты будут готовы через 5 минут.
          </p>
          <button
            type="button"
            onClick={openSignup}
            className="mt-8 inline-flex items-center justify-center rounded-xl bg-white px-8 py-4 text-base font-medium text-brand shadow-soft transition-all hover:-translate-y-0.5 hover:bg-white/90"
          >
            Попробовать бесплатно
          </button>
          <p className="mt-4 text-sm text-white/70">
            Без привязки карты · Первые посты за 5 минут
          </p>
        </div>
      </Reveal>
    </section>
  );
}
