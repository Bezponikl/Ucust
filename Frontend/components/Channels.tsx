"use client";

import { useEffect, useRef, useState } from "react";
import Image from "next/image";
import { motion, useReducedMotion } from "framer-motion";
import SectionHeading from "./SectionHeading";
import { CHANNELS, CHANNEL_ORDER } from "@/lib/channels";
import { staggerContainer, fadeUp, viewportOnce } from "@/lib/motion";

// Единый «магнитный» отклик на hover для всех карточек каналов.
const CARD_HOVER =
  "transition-[box-shadow,border-color] duration-300 ease-out hover:border-brand/40 hover:shadow-lift";

function ChannelCard({ id }: { id: (typeof CHANNEL_ORDER)[number] }) {
  const channel = CHANNELS[id];

  if (channel.iconType === "wordmark" && channel.icon) {
    return (
      <div className={`flex shrink-0 items-center rounded-[20px] border border-border bg-card px-6 py-4 shadow-soft ${CARD_HOVER}`}>
        <Image
          src={channel.icon}
          alt={channel.label}
          width={120}
          height={32}
          className={`h-6 w-auto object-contain sm:h-7 ${channel.iconDark ? "dark:hidden" : ""}`}
        />
        {channel.iconDark && (
          <Image
            src={channel.iconDark}
            alt={channel.label}
            width={120}
            height={32}
            className="hidden h-6 w-auto object-contain sm:h-7 dark:block"
          />
        )}
      </div>
    );
  }

  return (
    <div className={`flex shrink-0 items-center gap-2.5 rounded-[20px] border border-border bg-card px-5 py-4 shadow-soft ${CARD_HOVER}`}>
      {channel.icon ? (
        <span className="flex h-9 w-9 shrink-0 items-center justify-center overflow-hidden rounded-lg">
          <Image
            src={channel.icon}
            alt=""
            width={36}
            height={36}
            className="h-9 w-9 object-contain"
            aria-hidden="true"
          />
        </span>
      ) : (
        <span
          className="font-display flex h-9 w-9 items-center justify-center rounded-lg text-xs font-bold text-white"
          style={{ backgroundColor: channel.colorVar }}
          aria-hidden="true"
        >
          {channel.short}
        </span>
      )}
      <span className="whitespace-nowrap text-sm font-medium text-ink sm:text-base">
        {channel.label}
        {channel.id === "instagram" && (
          <>
            <sup className="ml-0.5 text-ink-muted" aria-hidden="true">*</sup>
            <span className="sr-only">
              {" "}— принадлежит Meta, признанной экстремистской организацией и запрещённой на территории РФ.
            </span>
          </>
        )}
      </span>
    </div>
  );
}

export default function Channels() {
  const prefersReducedMotion = useReducedMotion();
  // На сервере и при первой гидрации всегда рендерим бегущую ленту,
  // чтобы разметка совпадала; на статичную раскладку переключаемся
  // уже после монтирования, если пользователь просит меньше движения.
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  const reduceMotion = mounted && prefersReducedMotion;
  const track = [...CHANNEL_ORDER, ...CHANNEL_ORDER, ...CHANNEL_ORDER];

  // Пауза бегущей ленты, когда секция вне вьюпорта — не гоняем анимацию впустую.
  const viewportRef = useRef<HTMLDivElement>(null);
  const [inView, setInView] = useState(true);
  useEffect(() => {
    const el = viewportRef.current;
    if (!el || typeof IntersectionObserver === "undefined") return;
    const io = new IntersectionObserver(([e]) => setInView(e.isIntersecting), {
      threshold: 0,
    });
    io.observe(el);
    return () => io.disconnect();
  }, []);

  return (
    <section id="channels" className="py-12 sm:py-16 lg:py-20">
      <SectionHeading
        kicker="Каналы"
        className="mx-auto max-w-(--container-page) px-5 sm:px-6"
        subtitle="Подключите аккаунты один раз — дальше UCust публикует автоматически."
      >
        Публикуем туда, где ваши клиенты
      </SectionHeading>

      <div ref={viewportRef} className="relative mt-16 overflow-hidden sm:mt-24 lg:mt-32 [mask-image:linear-gradient(to_right,transparent,black_5%,black_95%,transparent)]">
        {reduceMotion ? (
          <motion.div
            variants={staggerContainer(0.08)}
            initial="hidden"
            whileInView="visible"
            viewport={viewportOnce}
            className="flex flex-wrap items-stretch justify-center gap-3 px-5 sm:gap-4 sm:px-6"
          >
            {CHANNEL_ORDER.map((id) => (
              <motion.div key={id} variants={fadeUp}>
                <ChannelCard id={id} />
              </motion.div>
            ))}
          </motion.div>
        ) : (
          <div className={`uc-marquee flex w-max items-stretch gap-3 sm:gap-4 ${inView ? "" : "is-paused"}`}>
            {track.map((id, i) => (
              <ChannelCard key={`${id}-${i}`} id={id} />
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
