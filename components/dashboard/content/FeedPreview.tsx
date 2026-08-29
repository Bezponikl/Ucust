"use client";

import Image from "next/image";
import Icon from "@/components/ui/Icon";

export type PreviewMedia =
  | { kind: "none" }
  | { kind: "image"; src: string }
  | { kind: "video"; src: string };

interface PreviewProps {
  brand: string;
  title: string;
  text: string;
  tags: string[];
  media: PreviewMedia;
  time: string;
}

/** Медиа поста в превью: одинаковая логика для обеих сетей. */
function Media({ media, ratio = "aspect-[4/3]" }: { media: PreviewMedia; ratio?: string }) {
  if (media.kind === "none") return null;
  return (
    <div className={`relative w-full ${ratio} bg-black/20`}>
      {media.kind === "image" ? (
        <Image
          key={media.src}
          src={media.src}
          alt=""
          fill
          sizes="360px"
          unoptimized={media.src.startsWith("blob:")}
          className="uc-fade-in object-cover"
        />
      ) : (
        <video src={media.src} className="h-full w-full object-cover" />
      )}
    </div>
  );
}

const body = (title: string, text: string, tags: string[]) => {
  const parts = [title, text].filter(Boolean);
  return { head: parts[0] ?? "Заголовок публикации", rest: parts[1] ?? "", tags };
};

/* ── ВКонтакте: шапка сообщества → фото → текст → реакции ── */
function VkPost({ brand, title, text, tags, media, time }: PreviewProps) {
  const initial = brand.replace(/[«»"']/g, "").charAt(0).toUpperCase() || "U";
  const { head, rest } = body(title, text, tags);

  return (
    <div className="overflow-hidden rounded-xl border border-black/10 bg-white text-[#000000] shadow-sm dark:border-white/10 dark:bg-[#19191a] dark:text-[#e1e3e6]">
      <div className="flex items-center gap-2.5 px-3 py-2.5">
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#2787f5] text-sm font-bold text-white">
          {initial}
        </span>
        <div className="min-w-0 flex-1">
          <p className="flex items-center gap-1 truncate text-[0.8125rem] font-semibold">
            {brand}
            <svg viewBox="0 0 24 24" className="h-3.5 w-3.5 shrink-0 fill-[#2787f5]" aria-hidden="true">
              <path d="M12 2l2.4 1.8 3-.3 1 2.8 2.6 1.5-1 2.9 1 2.9-2.6 1.5-1 2.8-3-.3L12 22l-2.4-1.8-3 .3-1-2.8L3 16.2l1-2.9-1-2.9 2.6-1.5 1-2.8 3 .3L12 2zm-1.1 12.9l5-5-1.3-1.3-3.7 3.7-1.8-1.8L7.8 12l3.1 2.9z" />
            </svg>
          </p>
          <p className="text-[0.6875rem] text-[#818c99] dark:text-[#828282]">{time} · Ростов-на-Дону</p>
        </div>
        <span className="shrink-0 text-lg leading-none text-[#818c99]">⋯</span>
      </div>

      <Media media={media} />

      <div className="px-3 pt-2.5 text-[0.8125rem] leading-[1.35]">
        <p className="font-medium">{head}</p>
        {rest && (
          <p className="mt-1 line-clamp-3 whitespace-pre-line">
            {rest}
          </p>
        )}
        {tags.length > 0 && (
          <p className="mt-1 text-[#2787f5]">{tags.map((t) => `#${t}`).join(" ")}</p>
        )}
        {(rest.length > 140 || tags.length > 3) && (
          <span className="mt-0.5 inline-block text-[#818c99]">Показать ещё</span>
        )}
      </div>

      <div className="flex items-center gap-3 px-3 py-2.5 text-[0.8125rem] text-[#818c99] dark:text-[#828282]">
        <span className="inline-flex items-center gap-1.5 rounded-full bg-black/5 px-2.5 py-1 dark:bg-white/8">
          <Icon name="heart" size={14} aria-hidden="true" /> 1,8K
        </span>
        <span className="inline-flex items-center gap-1.5 rounded-full bg-black/5 px-2.5 py-1 dark:bg-white/8">
          <Icon name="message" size={14} aria-hidden="true" /> 62
        </span>
        <span className="inline-flex items-center gap-1.5 rounded-full bg-black/5 px-2.5 py-1 dark:bg-white/8">
          <Icon name="send" size={14} aria-hidden="true" /> 503
        </span>
        <span className="ml-auto text-[0.6875rem]">{time}</span>
      </div>
    </div>
  );
}

/* ── Telegram: макет готов, включим вместе с остальными сетями ── */
export function TgPost({ brand, title, text, tags, media, time }: PreviewProps) {
  const { head, rest } = body(title, text, tags);

  return (
    <div className="rounded-xl bg-[#0e1621] p-3">
      <div className="overflow-hidden rounded-xl rounded-bl-md bg-[#182533] text-[#e9eef5]">
        <p className="px-3 pt-2.5 text-[0.8125rem] font-semibold text-[#e77fbf]">{brand}</p>

        <div className="mt-2">
          <Media media={media} ratio="aspect-[16/10]" />
        </div>

        <div className="px-3 pb-2 pt-2 text-[0.8125rem] leading-[1.4]">
          <p className="font-medium">{head}</p>
          {rest && <p className="mt-1 line-clamp-4 whitespace-pre-line text-[#e9eef5]/90">{rest}</p>}
          {tags.length > 0 && (
            <p className="mt-1 text-[#6ab3f3]">{tags.map((t) => `#${t}`).join(" ")}</p>
          )}
          <p className="mt-1 flex items-center justify-end gap-1.5 text-[0.6875rem] text-[#7d8b99]">
            <Icon name="eye" size={12} aria-hidden="true" /> 233.5K
            <span>{time}</span>
          </p>
        </div>

        <button
          type="button"
          className="flex w-full items-center gap-2 border-t border-white/8 px-3 py-2 text-[0.8125rem] text-[#6ab3f3]"
        >
          <Icon name="message" size={14} aria-hidden="true" /> Прокомментировать
          <Icon name="chevron-right" size={14} className="ml-auto" aria-hidden="true" />
        </button>
      </div>
    </div>
  );
}

/**
 * Предпросмотр публикации так, как её увидят в ленте.
 * Пока одна сеть — ВКонтакте; остальные добавим, когда появятся их макеты.
 */
export default function FeedPreview(props: PreviewProps) {
  return (
    <div>
      <p className="mb-2.5 text-xs font-medium uppercase tracking-wider text-ink-muted">Предпросмотр</p>

      <div className="uc-fade-in">
        <VkPost {...props} />
      </div>
    </div>
  );
}
