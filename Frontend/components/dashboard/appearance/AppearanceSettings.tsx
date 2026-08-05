"use client";

import { useRef, useState, type ChangeEvent, type ReactNode } from "react";
import Image from "next/image";
import Icon from "@/components/ui/Icon";
import { SettingsCard } from "@/components/dashboard/settings/primitives";
import { useDashboard } from "@/components/dashboard/DashboardProvider";
import { BACKGROUND_PRESETS } from "@/lib/dashboard/appearance";
import { toast } from "@/lib/toast";

const MAX_UPLOAD_BYTES = 4 * 1024 * 1024; // 4 МБ

function Tile({
  selected,
  onClick,
  label,
  children,
}: {
  selected: boolean;
  onClick: () => void;
  label: string;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={selected}
      className={`group relative flex aspect-video w-full overflow-hidden rounded-2xl border-2 shadow-soft transition hover:-translate-y-0.5 hover:shadow-lift ${
        selected ? "border-brand" : "border-border hover:border-brand/40"
      }`}
    >
      {children}
      {selected && (
        <span className="absolute right-2 top-2 flex h-6 w-6 items-center justify-center rounded-full bg-brand text-white shadow">
          <Icon name="check" size={14} aria-hidden="true" />
        </span>
      )}
      <span className="absolute inset-x-0 bottom-0 bg-black/45 px-2 py-1.5 text-left text-xs font-medium text-white">
        {label}
      </span>
    </button>
  );
}

const SURFACE_OPTIONS: { id: "solid" | "glass"; label: string; hint: string }[] = [
  { id: "solid", label: "Стандартная заливка", hint: "Сплошной непрозрачный фон окон" },
  { id: "glass", label: "Жидкое стекло", hint: "Полупрозрачные окна с размытием — фон просвечивает" },
];

export default function AppearanceSettings() {
  const { background, setBackground, surfaceStyle, setSurfaceStyle } = useDashboard();
  const [customSrc, setCustomSrc] = useState<string | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);

  const onUpload = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    if (file.size > MAX_UPLOAD_BYTES) {
      toast("Файл слишком большой, максимум 4 МБ");
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result as string;
      setCustomSrc(dataUrl);
      setBackground(dataUrl);
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="flex flex-col gap-5">
      <div>
        <h1 className="text-xl font-bold text-ink sm:text-2xl">Оформление</h1>
        <p className="mt-0.5 text-sm text-ink-muted">Фон дашборда — пресеты или своё изображение</p>
      </div>

      <SettingsCard title="Фон">
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
          <Tile selected={background === null} onClick={() => setBackground(null)} label="Без фона">
            <div className="h-full w-full bg-canvas" />
          </Tile>

          {BACKGROUND_PRESETS.map((p) => (
            <Tile key={p.id} selected={background === p.src} onClick={() => setBackground(p.src)} label={p.label}>
              <Image src={p.src} alt="" fill sizes="200px" className="object-cover" />
            </Tile>
          ))}

          {customSrc && (
            <Tile selected={background === customSrc} onClick={() => setBackground(customSrc)} label="Свой фон">
              <Image src={customSrc} alt="" fill unoptimized className="object-cover" />
            </Tile>
          )}

          <button
            type="button"
            onClick={() => fileInput.current?.click()}
            className="flex aspect-video w-full flex-col items-center justify-center gap-1.5 rounded-2xl border-2 border-dashed border-border text-ink-muted shadow-soft transition hover:-translate-y-0.5 hover:border-brand/40 hover:text-ink hover:shadow-lift"
          >
            <Icon name="image-plus" size={22} aria-hidden="true" />
            <span className="text-xs font-medium">{customSrc ? "Заменить свой фон" : "Добавить свой"}</span>
          </button>
          <input ref={fileInput} type="file" accept="image/*" hidden onChange={onUpload} />
        </div>
      </SettingsCard>

      <SettingsCard title="Заливка окон" desc="Как выглядят окна страниц на десктопе">
        <div className="flex flex-col gap-3 sm:flex-row">
          {SURFACE_OPTIONS.map((opt) => {
            const selected = surfaceStyle === opt.id;
            return (
              <button
                key={opt.id}
                type="button"
                onClick={() => setSurfaceStyle(opt.id)}
                aria-pressed={selected}
                className={`flex-1 rounded-2xl border-2 px-4 py-3 text-left shadow-soft transition hover:-translate-y-0.5 hover:shadow-lift ${
                  selected ? "border-brand bg-brand/5" : "border-border hover:border-brand/40"
                }`}
              >
                <span className="flex items-center gap-2 text-sm font-semibold text-ink">
                  {selected && <Icon name="check-bold" size={14} className="shrink-0 text-brand" aria-hidden="true" />}
                  {opt.label}
                </span>
                <span className="mt-0.5 block text-xs text-ink-muted">{opt.hint}</span>
              </button>
            );
          })}
        </div>
      </SettingsCard>
    </div>
  );
}
