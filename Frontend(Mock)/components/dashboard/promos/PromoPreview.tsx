"use client";

import Image from "next/image";
import Icon from "@/components/ui/Icon";
import { CHANNELS, type ChannelId } from "@/lib/channels";
import {
  PROMO_STATUS_LABEL,
  PROMO_TYPE,
  type PromoStatus,
  type PromoType,
} from "@/lib/dashboard/promos";

/* Плотная подложка, а не прозрачная: на светлом фото полупрозрачный бейдж не читался */
export const STATUS_BADGE: Record<PromoStatus, string> = {
  active:    "border-white/15 bg-black/55 text-white",
  scheduled: "border-white/15 bg-black/55 text-white",
  finished:  "border-white/15 bg-black/55 text-white/80",
};

export const STATUS_DOT: Record<PromoStatus, string> = {
  active:    "bg-success",
  scheduled: "bg-brand",
  finished:  "bg-white/50",
};

/** Обложка акции. Без фото — фирменная подложка в цвет механики,
 *  чтобы карточка оставалась читаемой (название и оффер не теряются). */
export function PromoCover({
  image,
  type,
  discount,
  status,
  title,
  className = "",
  sizes = "480px",
}: {
  image?: string;
  type: PromoType;
  discount?: string;
  status?: PromoStatus;
  title?: string;
  className?: string;
  sizes?: string;
}) {
  const t = PROMO_TYPE[type];
  const onPhoto = Boolean(image);

  return (
    <div className={`relative overflow-hidden ${className}`}>
      {image ? (
        <>
          <Image
            src={image}
            alt=""
            fill
            sizes={sizes}
            className="object-cover transition-transform duration-300 group-hover:scale-[1.02]"
            unoptimized={image.startsWith("blob:")}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/75 via-black/25 to-black/10" />
        </>
      ) : (
        <div className={`absolute inset-0 grid place-items-center bg-surface-soft bg-gradient-to-br ${t.cover}`}>
          <Icon name={t.icon} size={64} className="opacity-25" aria-hidden="true" />
        </div>
      )}

      {/* Механика — всегда видна, даже без фото */}
      <span
        className={`absolute left-3 top-3 inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[0.6875rem] font-semibold backdrop-blur-md ${
          onPhoto ? "border border-white/15 bg-black/55 text-white" : t.chip
        }`}
      >
        <Icon name={t.icon} size={12} aria-hidden="true" />
        {t.label}
      </span>

      {status && (
        <span
          className={`absolute right-3 top-3 inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium backdrop-blur-md ${
            onPhoto ? STATUS_BADGE[status] : "border-border bg-card/80 text-ink"
          }`}
        >
          <span className={`h-1.5 w-1.5 rounded-full ${STATUS_DOT[status]}`} />
          {PROMO_STATUS_LABEL[status]}
        </span>
      )}

      {discount && (
        <span
          className={`absolute bottom-3 right-4 font-display text-4xl font-black leading-none ${
            onPhoto ? "text-white drop-shadow-lg" : t.tint
          }`}
        >
          {discount}
        </span>
      )}

      {title && (
        <span
          className={`absolute bottom-3 left-4 right-24 truncate font-display text-lg font-bold ${
            onPhoto ? "text-white drop-shadow-md" : t.tint
          }`}
        >
          {title}
        </span>
      )}
    </div>
  );
}

/** Живое превью карточки акции — общий компонент для создания и редактирования. */
export default function PromoPreview({
  title,
  description,
  discount,
  code,
  image,
  type,
  goal,
  period,
  channels,
  status = "active",
}: {
  title: string;
  description: string;
  discount?: string;
  code?: string;
  image?: string;
  type: PromoType;
  goal?: number;
  period?: string;
  channels?: ChannelId[];
  status?: PromoStatus;
}) {
  return (
    <div className="group overflow-hidden rounded-[24px] border border-border bg-card shadow-soft">
      <PromoCover
        className="h-44 shrink-0"
        image={image}
        type={type}
        discount={discount}
        status={status}
      />

      <div className="flex flex-col gap-3 p-5">
        <p className="font-display text-lg font-bold leading-snug text-ink">
          {title || <span className="font-normal italic opacity-40">Название акции</span>}
        </p>

        <p className="min-h-10 text-sm leading-relaxed text-ink-muted">
          {description || <span className="italic opacity-40">Описание акции появится здесь</span>}
        </p>

        {code && (
          <span className="inline-block w-fit rounded-lg border border-border bg-surface-soft px-3 py-1 font-mono text-xs font-bold tracking-widest text-ink">
            {code}
          </span>
        )}

        <div className="border-t border-border pt-3">
          {goal != null ? (
            <div>
              <div className="flex items-end justify-between">
                <p className="text-xs text-ink-muted">Цель</p>
                <p className="font-display text-2xl font-extrabold leading-none text-ink">
                  — / {goal}
                </p>
              </div>
              <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-border">
                <div className="h-full w-0 rounded-full bg-success" />
              </div>
            </div>
          ) : (
            <p className="text-xs text-ink-muted">{period || "Период не задан"}</p>
          )}
        </div>

        {channels && channels.length > 0 && (
          <div className="flex items-center justify-between gap-2 border-t border-border pt-3">
            <p className="text-xs text-ink-muted">{period || "—"}</p>
            <span className="flex items-center gap-1.5">
              {channels.map((id) => {
                const ch = CHANNELS[id];
                return ch?.icon && ch.iconType !== "wordmark" ? (
                  <Image
                    key={id}
                    src={ch.icon}
                    alt={ch.label}
                    width={16}
                    height={16}
                    className="h-4 w-4 object-contain"
                  />
                ) : null;
              })}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
