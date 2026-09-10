"use client";

import Image from "next/image";
import { authorizeUrl } from "@/lib/api/oauth";

const providers = [
  { id: "yandex", name: "Яндекс", icon: "/yandex.svg", label: "Войти через Яндекс" },
  { id: "vk", name: "ВКонтакте", icon: "/vk.svg", label: "Войти через ВКонтакте" },
] as const;

type SocialAuthProps = {
  label?: string;
};

export default function SocialAuth({ label = "или войдите с помощью" }: SocialAuthProps) {
  return (
    <>
      <div className="my-6 flex items-center gap-3 text-xs text-ink-muted">
        <span className="h-px flex-1 bg-border" aria-hidden="true" />
        {label}
        <span className="h-px flex-1 bg-border" aria-hidden="true" />
      </div>

      <div className="flex items-center justify-center gap-4">
        {providers.map((provider) => (
          <button
            key={provider.id}
            type="button"
            aria-label={provider.label}
            onClick={() => {
              window.location.href = authorizeUrl(provider.id);
            }}
            className="flex h-16 w-16 items-center justify-center rounded-full bg-surface-soft transition-all hover:bg-card dark:hover:bg-white/5"
          >
            <Image
              src={provider.icon}
              alt=""
              width={32}
              height={32}
              className="h-8 w-8 shrink-0"
              aria-hidden="true"
            />
          </button>
        ))}
      </div>
    </>
  );
}