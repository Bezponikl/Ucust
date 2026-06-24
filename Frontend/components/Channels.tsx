"use client";

import Image from "next/image";
import { motion, useReducedMotion } from "framer-motion";
import Reveal from "./Reveal";
import { CHANNELS, CHANNEL_ORDER } from "@/lib/channels";

function ChannelCard({ id }: { id: (typeof CHANNEL_ORDER)[number] }) {
  const channel = CHANNELS[id];

  if (channel.iconType === "wordmark" && channel.icon) {
    return (
      <div className="flex shrink-0 items-center rounded-2xl border border-border bg-card px-6 py-4 shadow-soft">
        <Image
          src={channel.icon}
          alt={channel.label}
          width={120}
          height={32}
          className="h-6 w-auto object-contain sm:h-7"
        />
      </div>
    );
  }

  return (
    <div className="flex shrink-0 items-center gap-2.5 rounded-2xl border border-border bg-card px-5 py-4 shadow-soft">
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
      </span>
    </div>
  );
}

export default function Channels() {
  const prefersReducedMotion = useReducedMotion();
  const track = [...CHANNEL_ORDER, ...CHANNEL_ORDER, ...CHANNEL_ORDER];

  return (
    <section id="channels" className="py-16 sm:py-24 lg:py-32">
      <Reveal className="mx-auto max-w-(--container-page) px-5 sm:px-6">
        <h2 className="max-w-2xl text-3xl font-extrabold leading-tight tracking-tight text-ink sm:text-4xl">
          Публикуем туда, где ваши клиенты
        </h2>
        <p className="mt-3 max-w-xl text-base leading-relaxed text-ink-muted sm:text-lg">
          Подключите аккаунты один раз — дальше UCust публикует автоматически.
        </p>
      </Reveal>

      <div className="relative mt-16 overflow-hidden sm:mt-24 lg:mt-32 [mask-image:linear-gradient(to_right,transparent,black_5%,black_95%,transparent)]">
        {prefersReducedMotion ? (
          <div className="flex flex-wrap items-center justify-center gap-3 px-5 sm:gap-4 sm:px-6">
            {CHANNEL_ORDER.map((id) => (
              <ChannelCard key={id} id={id} />
            ))}
          </div>
        ) : (
          <motion.div
            className="flex w-max items-center gap-3 sm:gap-4"
            animate={{ x: ["0%", "-33.3333%"] }}
            transition={{ duration: 32, repeat: Infinity, ease: "linear" }}
          >
            {track.map((id, i) => (
              <ChannelCard key={`${id}-${i}`} id={id} />
            ))}
          </motion.div>
        )}
      </div>
    </section>
  );
}
