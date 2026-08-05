"use client";

import { useEffect, useMemo, useRef, useState, type ChangeEvent } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import Icon from "@/components/ui/Icon";
import EmojiPicker from "@/components/ui/EmojiPicker";
import { toast } from "@/lib/toast";
import type { ChannelId } from "@/lib/channels";
import { STATUS_LABEL, type Post, type PostType } from "@/lib/dashboard/content";
import { dayToIso, fmtDayMonth } from "@/lib/dashboard/date";
import { TEXT_AI_ACTIONS, applyTextAi } from "@/lib/dashboard/textAi";
import type { PostStatus } from "@/lib/dashboard/types";
import { useDashboard } from "@/components/dashboard/DashboardProvider";
import FeedPreview, { type PreviewMedia } from "./FeedPreview";
import {
  ActionMenu,
  AutoGrowTextarea,
  ChannelSelect,
  ControlRow,
  DateTimeField,
  SoftSelect,
  type SelectOption,
} from "./EditorControls";

const IMAGE_POOL = [
  "/content/drinks.jpg", "/content/barista.jpg", "/content/interior.jpg", "/content/beans.jpg",
  "/content/newdrink.jpg", "/content/latteart.jpg", "/content/pastry.jpg",
];

const TYPE_OPTIONS: SelectOption<PostType>[] = [
  { id: "post",  label: "Публикация", icon: "file-text" },
  { id: "promo", label: "Акция",      icon: "gift" },
  { id: "video", label: "Видео",      icon: "clapperboard" },
];

const STATUS_OPTIONS: SelectOption<PostStatus>[] = [
  { id: "published", label: STATUS_LABEL.published, dot: "bg-success" },
  { id: "scheduled", label: STATUS_LABEL.scheduled, dot: "bg-brand" },
  { id: "draft",     label: STATUS_LABEL.draft,     dot: "bg-ink-muted" },
];

type Media = PreviewMedia;

export default function PostEditView({ post }: { post: Post }) {
  const router = useRouter();
  const { data } = useDashboard();
  const brand = data?.businessName ?? "Ваш бизнес";

  const initialMedia: Media = post.image ? { kind: "image", src: post.image } : { kind: "none" };
  const [title, setTitle] = useState(post.title);
  const [text, setText] = useState(post.excerpt);
  const [media, setMedia] = useState<Media>(initialMedia);
  const [channels, setChannels] = useState<ChannelId[]>(post.channels);
  const [status, setStatus] = useState<PostStatus>(post.status === "none" ? "draft" : post.status);
  const [type, setType] = useState<PostType>(post.type);
  const [date, setDate] = useState(dayToIso(post.day));
  const [time, setTime] = useState(post.time === "—" ? "12:00" : post.time);
  const [tags, setTags] = useState<string[]>(["кофейня", "утро", "эспрессо"]);

  const [busy, setBusy] = useState<null | "text" | "image">(null);
  const [saved, setSaved] = useState(true);
  const [addingTag, setAddingTag] = useState(false);
  const [newTag, setNewTag] = useState("");

  const textRef = useRef<HTMLTextAreaElement>(null);
  const fileInput = useRef<HTMLInputElement>(null);
  const objectUrls = useRef<string[]>([]);
  useEffect(() => { const u = objectUrls.current; return () => u.forEach((x) => URL.revokeObjectURL(x)); }, []);

  const snapshot = useMemo(
    () => JSON.stringify({ title, text, media, channels, status, type, date, time, tags }),
    [title, text, media, channels, status, type, date, time, tags],
  );
  const savedSnapshot = useRef(snapshot);
  useEffect(() => { setSaved(snapshot === savedSnapshot.current); }, [snapshot]);

  /* ── Действия ── */
  const pickFile = () => fileInput.current?.click();
  const onFile = (e: ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) {
      const url = URL.createObjectURL(f);
      objectUrls.current.push(url);
      setMedia({ kind: f.type.startsWith("video") ? "video" : "image", src: url });
    }
    e.target.value = "";
  };

  const nextImage = () => {
    setBusy("image");
    setTimeout(() => {
      const cur = media.kind === "image" ? IMAGE_POOL.indexOf(media.src) : -1;
      setMedia({ kind: "image", src: IMAGE_POOL[(cur + 1) % IMAGE_POOL.length] });
      setBusy(null);
    }, 700);
  };
  /** Действия ИИ над текстом — общий список с экраном создания. */
  const AI_ITEMS = TEXT_AI_ACTIONS.map((a) => ({
    id: a.key,
    label: a.label,
    icon: a.icon,
    onSelect: () => {
      // Берём значение прямо из поля: пользователь мог править текст только что
      const r = applyTextAi(a.key, textRef.current?.value ?? text);
      setBusy("text");
      setTimeout(() => {
        setText(r.text);
        setBusy(null);
        if (r.note) toast(r.note);
      }, 700);
    },
  }));

  const addTag = () => {
    const t = newTag.trim().replace(/^#/, "");
    if (t) setTags((prev) => [...new Set([...prev, t])]);
    setNewTag("");
    setAddingTag(false);
  };

  const save = () => {
    savedSnapshot.current = snapshot;
    setSaved(true);
    toast("Изменения сохранены");
  };
  const publish = () => { toast("Публикация отправлена"); router.push("/dashboard/content"); };

  return (
    <div className="flex flex-col">
      {/* ── Панель редактора: всегда сверху ── */}
      <header className="sticky -top-5 z-30 -mx-6 -mt-5 mb-8 flex items-center gap-2 border-b border-border/60 bg-card px-4 pb-3 pt-8 backdrop-blur-xl sm:px-6 lg:-top-6 lg:-mt-6 lg:rounded-t-3xl lg:pt-9">
        <button
          type="button"
          onClick={() => router.push("/dashboard/content")}
          aria-label="Назад к контент-плану"
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-ink-muted transition duration-150 hover:bg-surface-soft hover:text-ink"
        >
          <Icon name="arrow-left" size={18} aria-hidden="true" />
        </button>

        <span className="hidden min-w-0 truncate text-sm font-semibold text-ink sm:block">Редактирование</span>

        <span className="ml-1 hidden shrink-0 items-center gap-1.5 rounded-full bg-surface-soft px-2.5 py-1 text-xs text-ink-muted md:inline-flex">
          <span
            className={`h-1.5 w-1.5 rounded-full transition duration-200 ${saved ? "bg-success" : "bg-brand-orange"}`}
            aria-hidden="true"
          />
          {saved ? "Сохранено" : "Не сохранено"}
        </span>

        <div className="ml-auto flex shrink-0 items-center gap-1.5">
          <button
            type="button"
            onClick={() => toast("История версий скоро появится")}
            className="hidden rounded-full px-3 py-2 text-sm font-medium text-ink-muted transition duration-150 hover:bg-surface-soft hover:text-ink sm:block"
          >
            История
          </button>

          <button
            type="button"
            onClick={save}
            className="btn-glass inline-flex items-center px-4 py-2 text-[0.8125rem] font-semibold sm:text-sm"
          >
            Сохранить
          </button>
          <button
            type="button"
            onClick={publish}
            className="btn-glass-blue inline-flex items-center gap-2 px-4 py-2 text-[0.8125rem] font-semibold sm:px-5 sm:text-sm"
          >
            <Icon name="send" size={15} aria-hidden="true" /> Опубликовать
          </button>
        </div>
      </header>

      <div className="grid gap-10 lg:grid-cols-[minmax(0,1fr)_340px] xl:gap-14">
        {/* ── Редактор: фото, заголовок, текст, теги — одним потоком ── */}
        <section className="mx-auto w-full max-w-2xl">
          {media.kind === "none" ? (
            <button
              type="button"
              onClick={pickFile}
              className="grid aspect-[2/1] max-h-64 w-full place-items-center rounded-[20px] border border-dashed border-border text-ink-muted transition duration-200 hover:border-brand/50 hover:text-ink"
            >
              <span className="inline-flex items-center gap-2 text-sm">
                <Icon name="image-plus" size={18} aria-hidden="true" /> Добавить изображение
              </span>
            </button>
          ) : (
            <div className="relative aspect-[2/1] max-h-64 w-full overflow-hidden rounded-[20px] bg-surface-soft">
              {media.kind === "image" ? (
                <Image
                  key={media.src}
                  src={media.src}
                  alt=""
                  fill
                  sizes="(max-width: 1024px) 100vw, 640px"
                  unoptimized={media.src.startsWith("blob:")}
                  className="uc-fade-in object-cover"
                />
              ) : (
                <video src={media.src} controls className="h-full w-full bg-ink object-cover" />
              )}
              {busy === "image" && (
                <div className="absolute inset-0 grid place-items-center bg-ink/40 backdrop-blur-sm">
                  <Icon name="refresh" size={24} className="animate-spin text-white" aria-hidden="true" />
                </div>
              )}
            </div>
          )}

          <div className="mt-2.5 flex items-center gap-1">
            <button
              type="button"
              onClick={pickFile}
              className="rounded-lg px-2.5 py-1.5 text-xs font-medium text-ink-muted transition duration-150 hover:bg-surface-soft hover:text-ink"
            >
              Заменить
            </button>
            <button
              type="button"
              onClick={nextImage}
              className="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium text-brand transition duration-150 hover:bg-brand/10"
            >
              <Icon name="sparkles" size={12} aria-hidden="true" /> Сгенерировать
            </button>
            {media.kind !== "none" && (
              <button
                type="button"
                onClick={() => setMedia({ kind: "none" })}
                className="rounded-lg px-2.5 py-1.5 text-xs font-medium text-ink-muted transition duration-150 hover:bg-surface-soft hover:text-[#e5484d]"
              >
                Удалить
              </button>
            )}
          </div>

          {/* Поля подписаны и имеют подложку — сразу видно, что текст редактируемый */}
          <div className="mt-6 max-w-lg">
            <label htmlFor="post-title" className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-ink-muted">
              Заголовок
            </label>
            <div className="cursor-text rounded-2xl border border-border/60 bg-surface-soft/40 px-4 py-2.5 transition duration-150 hover:border-border focus-within:border-brand focus-within:bg-card focus-within:ring-2 focus-within:ring-brand/20">
              <AutoGrowTextarea
                id="post-title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="О чём публикация в двух словах"
                className="w-full resize-none overflow-hidden bg-transparent font-display text-xl font-bold leading-tight text-ink outline-none placeholder:font-normal placeholder:text-ink-muted/40 sm:text-2xl"
              />
            </div>
          </div>

          <div className="mt-4">
            <div className="mb-1.5 flex items-end justify-between gap-3">
              <label htmlFor="post-text" className="text-xs font-medium uppercase tracking-wider text-ink-muted">
                Текст публикации
              </label>
              <div className="flex items-center gap-1">
                {/* Главный инструмент экрана — держим на виду, рядом с текстом */}
                <ActionMenu
                  trigger={
                    busy ? (
                      <><Icon name="refresh" size={14} className="animate-spin" aria-hidden="true" /> Генерирую…</>
                    ) : (
                      "Переписать с AI"
                    )
                  }
                  items={AI_ITEMS}
                  width="w-64"
                  emphasis
                />
              </div>
            </div>
            <div className="cursor-text rounded-2xl border border-border/60 bg-surface-soft/40 px-4 py-3 transition duration-150 hover:border-border focus-within:border-brand focus-within:bg-card focus-within:ring-2 focus-within:ring-brand/20">
              {/* Растёт под содержимое — без «дыры» под коротким постом */}
              <AutoGrowTextarea
                id="post-text"
                innerRef={textRef}
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Напишите текст или попросите ИИ — кнопка «Переписать с AI»"
                className={`min-h-28 w-full resize-none overflow-hidden bg-transparent text-base leading-relaxed text-ink outline-none transition duration-200 placeholder:text-ink-muted/40 ${
                  busy === "text" ? "animate-pulse opacity-50" : ""
                }`}
              />
              {/* Счётчик слева, эмодзи — в самом поле, у правого нижнего угла */}
              <div className="mt-2 flex items-center justify-between gap-2">
                <span className="text-xs text-ink-muted/70">{text.length} символов</span>
                <EmojiPicker targetRef={textRef} value={text} onChange={setText} />
              </div>
            </div>
          </div>

          <span className="mt-5 block text-xs font-medium uppercase tracking-wider text-ink-muted">Хэштеги</span>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            {tags.map((t) => (
              <span
                key={t}
                className="uc-pop-in group inline-flex items-center gap-1 rounded-full bg-surface-soft px-3 py-1.5 text-xs font-medium text-ink transition duration-150 hover:bg-brand/10"
              >
                #{t}
                <button
                  type="button"
                  onClick={() => setTags((prev) => prev.filter((x) => x !== t))}
                  aria-label={`Убрать #${t}`}
                  className="text-ink-muted opacity-0 transition duration-150 hover:text-ink group-hover:opacity-100"
                >
                  <Icon name="close" size={11} aria-hidden="true" />
                </button>
              </span>
            ))}

            {addingTag ? (
              <input
                autoFocus
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onBlur={addTag}
                onKeyDown={(e) => {
                  if (e.key === "Enter") { e.preventDefault(); addTag(); }
                  if (e.key === "Escape") { setNewTag(""); setAddingTag(false); }
                }}
                placeholder="тег"
                aria-label="Новый хэштег"
                className="w-24 rounded-full bg-surface-soft px-3 py-1.5 text-xs text-ink outline-none ring-1 ring-brand/40 placeholder:text-ink-muted/50"
              />
            ) : (
              <button
                type="button"
                onClick={() => setAddingTag(true)}
                className="inline-flex items-center gap-1 rounded-full px-3 py-1.5 text-xs font-medium text-ink-muted transition duration-150 hover:bg-surface-soft hover:text-ink"
              >
                <Icon name="plus" size={12} aria-hidden="true" /> Хэштег
              </button>
            )}
          </div>
        </section>

        {/* ── Предпросмотр и одна карточка публикации ── */}
        <aside className="min-w-0">
          <div className="lg:sticky lg:top-20">
            <FeedPreview
              brand={brand}
              title={title}
              text={text}
              tags={tags}
              media={media}
              time={`${fmtDayMonth(date)}, ${time}`}
            />

            <div className="mt-4 rounded-[20px] border border-border/60 bg-card/50 px-4 py-1">
              <ControlRow label="Тип">
                <SoftSelect value={type} options={TYPE_OPTIONS} onChange={setType} ariaLabel="Тип публикации" />
              </ControlRow>
              <ControlRow label="Статус">
                <SoftSelect value={status} options={STATUS_OPTIONS} onChange={setStatus} ariaLabel="Статус публикации" />
              </ControlRow>
              <ControlRow label="Дата">
                <DateTimeField
                  date={date}
                  time={time}
                  originalDate={dayToIso(post.day)}
                  onDate={setDate}
                  onTime={setTime}
                />
              </ControlRow>
              <ControlRow label="Каналы">
                <ChannelSelect value={channels} onChange={setChannels} />
              </ControlRow>
            </div>
          </div>
        </aside>
      </div>

      <input ref={fileInput} type="file" accept="image/*,video/*" hidden onChange={onFile} />
    </div>
  );
}
