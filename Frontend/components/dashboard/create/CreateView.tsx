"use client";

import { useEffect, useRef, useState, type ChangeEvent, type RefObject } from "react";
import { createPortal } from "react-dom";
import { useRouter } from "next/navigation";
import Image from "next/image";
import Icon from "@/components/ui/Icon";
import EmojiPicker from "@/components/ui/EmojiPicker";
import AnchoredPopover from "@/components/ui/AnchoredPopover";
import { toast } from "@/lib/toast";
import type { IconName } from "@/lib/icons/solar";
import { CHANNELS, CHANNEL_ORDER, type ChannelId } from "@/lib/channels";
import PromptComposer from "@/components/dashboard/PromptComposer";
import { useAttachments } from "@/lib/dashboard/attachments";
import { DateField } from "@/components/dashboard/content/EditorControls";
import TimeInput from "@/components/ui/TimeInput";
import { fmtDayMonth, isoOffset } from "@/lib/dashboard/date";
import { TEXT_AI_ACTIONS, applyTextAi } from "@/lib/dashboard/textAi";
import { submitAiTask } from "@/lib/api/ai";
import { AI_GATEWAY_URL } from "@/lib/api/client";
import { loadOnboarding } from "@/lib/onboarding/storage";

type Format = "post" | "video";
type ImgSource = "none" | "upload" | "ai";
type VidSource = "upload" | "ai";
type Mode = "create" | "generating" | "edit";

const VOICES = ["Автоматически", "Дружелюбный", "Тёплый", "С заботой", "Экспертный"];
const LENGTHS = ["Автоматически", "Короткий", "Средний", "Длинный"];
const REVEAL_AT = 1; // настройки раскрываются сразу с первого символа

// Контекстные подсказки-идеи для поля описания
const IDEAS: { label: string; text: string }[] = [
  { label: "Новинка в меню", text: "Расскажи о новой позиции в меню — что это, какой вкус, для кого, и пригласи попробовать." },
  { label: "Акция или скидка", text: "Анонсируй акцию: что предлагаем, на каких условиях и до какого числа она действует." },
  { label: "Анонс события", text: "Анонсируй событие: что будет, когда, где и почему стоит прийти." },
  { label: "История бренда", text: "Расскажи историю бренда — как всё начиналось и что для нас важно." },
  { label: "Атмосфера", text: "Опиши атмосферу заведения так, чтобы захотелось зайти именно сегодня." },
  { label: "Отзыв гостя", text: "Поделись тёплым отзывом гостя и поблагодари за доверие." },
];

const AI_STEPS = [
  "Анализируем бренд",
  "Определяем тон сообщения",
  "Создаем структуру публикации",
  "Подбираем медиа и хештеги",
  "Проверяем текст"
];
const PHOTO_STEP = "Анализируем прикреплённые фото через Moondream";


const IMAGE_POOL = ["/content/drinks.jpg", "/content/barista.jpg", "/content/interior.jpg", "/content/beans.jpg", "/content/newdrink.jpg", "/content/latteart.jpg", "/content/pastry.jpg"];

type Media =
  | { kind: "none" }
  | { kind: "image"; src: string }
  | { kind: "video-ai"; poster: string }
  | { kind: "video-file"; src: string; poster?: string };

const cap = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

function generateBody(topic: string, format: Format, refCount = 0): string {
  const subject = topic.trim() || "У нас новинка";
  const opener = format === "video" ? "🎬 Смотрите наше новое видео!" : "☕ Друзья, у нас новость!";
  // Мок: с прикреплёнными фото ИИ «описывает кадр». В проде фото уходят в запрос
  // вместе с текстом — меняется только тело этой функции.
  const fromPhoto = refCount
    ? `\n\nНа снимке — то, что мы приготовили сегодня: тёплый свет, аромат свежей обжарки и наши любимые детали.`
    : "";
  return `${opener}\n\n${cap(subject)}.${fromPhoto} Готовили с заботой о вас — заходите попробовать и поделитесь впечатлениями!\n\nЖдём вас в гости 🤍`;
}

function deriveHashtags(topic: string): string[] {
  const words = topic.toLowerCase().match(/[\p{L}]{4,}/gu) ?? [];
  const picked = [...new Set(words)].slice(0, 2);
  return [...new Set([...picked, "кофейня", "уют", "нашбренд"])].slice(0, 4);
}

function useClickOutside(ref: RefObject<HTMLElement | null>, onClose: () => void) {
  useEffect(() => {
    const h = (e: MouseEvent) => { if (ref.current && !ref.current.contains(e.target as Node)) onClose(); };
    document.addEventListener("mousedown", h);
    return () => document.removeEventListener("mousedown", h);
  }, [ref, onClose]);
}

const channelIcon = (id: ChannelId, size = 16) => {
  const ch = CHANNELS[id];
  return ch.icon && ch.iconType !== "wordmark"
    ? <Image key={id} src={ch.icon} alt="" width={size} height={size} style={{ width: size, height: size }} className="object-contain" aria-hidden="true" />
    : <span key={id} className="rounded-full" style={{ width: size, height: size, backgroundColor: ch.colorVar }} aria-hidden="true" />;
};

/* ── Радио-пилюли (формат / источник медиа) ── */
function RadioPills<T extends string>({ value, options, onChange }: { value: T; options: { id: T; label: string; icon?: IconName }[]; onChange: (v: T) => void }) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((o) => (
        <button key={o.id} type="button" onClick={() => onChange(o.id)} aria-pressed={value === o.id}
          className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition ${value === o.id ? "bg-brand text-white" : "bg-surface-soft text-ink-muted hover:text-ink"}`}>
          {o.icon && <Icon name={o.icon} size={15} aria-hidden="true" />} {o.label}
        </button>
      ))}
    </div>
  );
}

/* ── Компактный селект (голос) ── */
function MiniSelect({ value, options, onChange }: { value: string; options: string[]; onChange: (v: string) => void }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(220);

  // Ширину берём у кнопки, позицию считает поповер — иначе список уезжает за экран
  const toggle = () => {
    setWidth(ref.current?.offsetWidth ?? 220);
    setOpen((v) => !v);
  };

  return (
    <div ref={ref} className="relative">
      <button type="button" onClick={toggle} aria-haspopup="listbox" aria-expanded={open}
        className={`flex w-full items-center justify-between gap-2 rounded-2xl border bg-surface-soft px-4 py-3 text-left text-sm text-ink transition ${open ? "border-brand/50" : "border-transparent hover:border-border"}`}>
        <span className="truncate">{value}</span>
        <Icon name="chevron-down" size={16} className={`shrink-0 text-ink-muted transition-transform ${open ? "rotate-180" : ""}`} aria-hidden="true" />
      </button>

      <AnchoredPopover
        anchorRef={ref}
        open={open}
        onClose={() => setOpen(false)}
        width={width}
        align="left"
        className="overflow-hidden rounded-2xl border border-border bg-card p-1.5 shadow-lift"
      >
        <div role="listbox">
          {options.map((o) => (
            <button key={o} type="button" role="option" aria-selected={o === value} onClick={() => { onChange(o); setOpen(false); }}
              className={`flex w-full items-center justify-between gap-2 rounded-xl px-3 py-2 text-left text-sm transition hover:bg-surface-soft ${o === value ? "font-medium text-brand" : "text-ink"}`}>
              <span className="truncate">{o}</span>
              {o === value && <Icon name="check" size={15} className="shrink-0 text-brand" aria-hidden="true" />}
            </button>
          ))}
        </div>
      </AnchoredPopover>
    </div>
  );
}

/* ── Медиа-блок в редакторе (hover-меню) ── */
function MediaEditor({ media, onChange, onGenerate, onUpload, onRemove }: { media: Media; onChange: () => void; onGenerate: () => void; onUpload: () => void; onRemove: () => void }) {
  if (media.kind === "none") {
    return (
      <button type="button" onClick={onUpload} className="grid h-56 w-full sm:h-64 lg:h-full place-items-center rounded-2xl border border-dashed border-border bg-surface-soft text-ink-muted transition hover:border-brand/40 hover:text-ink">
        <span className="inline-flex items-center gap-2 text-sm"><Icon name="image-plus" size={18} aria-hidden="true" /> Добавить изображение</span>
      </button>
    );
  }
  return (
    <div className="group relative h-56 w-full sm:h-64 lg:h-full overflow-hidden rounded-2xl bg-surface-soft">
      {media.kind === "image" && <Image src={media.src} alt="" fill unoptimized={media.src.startsWith("blob:")} sizes="(max-width:1024px) 100vw, 640px" className="object-cover" />}
      {media.kind === "video-file" && (
        // eslint-disable-next-line jsx-a11y/media-has-caption
        <video src={media.src} poster={media.poster} controls className="h-full w-full bg-ink object-cover" />
      )}
      {media.kind === "video-ai" && (
        <>
          <Image src={media.poster} alt="" fill sizes="640px" className="object-cover" />
          <div className="absolute inset-0 grid place-items-center bg-ink/25"><span className="flex h-12 w-12 items-center justify-center rounded-full bg-white/90 text-ink"><Icon name="play" size={20} className="ml-0.5" aria-hidden="true" /></span></div>
          <span className="absolute bottom-3 left-3 inline-flex items-center gap-1 rounded-full bg-ink/60 px-2 py-0.5 text-[0.6875rem] font-medium text-white backdrop-blur-sm"><Icon name="sparkles" size={11} aria-hidden="true" /> AI-видео · 0:15</span>
        </>
      )}
      <div className="absolute inset-x-0 top-0 flex items-center justify-end gap-2 bg-gradient-to-b from-black/50 to-transparent p-3 opacity-0 transition-opacity group-hover:opacity-100">
        <button type="button" onClick={onChange} className="inline-flex items-center gap-1.5 rounded-xl border border-white/20 bg-black/40 px-3 py-1.5 text-xs font-medium text-white backdrop-blur-md transition hover:bg-black/60"><Icon name="image-plus" size={13} aria-hidden="true" /> Изменить</button>
        <button type="button" onClick={onGenerate} className="inline-flex items-center gap-1.5 rounded-xl border border-white/20 bg-black/40 px-3 py-1.5 text-xs font-medium text-white backdrop-blur-md transition hover:bg-black/60"><Icon name="sparkles" size={13} aria-hidden="true" /> Сгенерировать заново</button>
        <button type="button" onClick={onRemove} aria-label="Удалить" className="inline-flex items-center justify-center rounded-xl border border-white/20 bg-black/40 px-2.5 py-1.5 text-white backdrop-blur-md transition hover:bg-red-500/70"><Icon name="trash" size={13} aria-hidden="true" /></button>
      </div>
    </div>
  );
}

export default function CreateView() {
  const router = useRouter();

  const [mode, setMode] = useState<Mode>("create");
  const [topic, setTopic] = useState("");
  const [settingsShown, setSettingsShown] = useState(false);
  const [format, setFormat] = useState<Format>("post");
  const [imgSource, setImgSource] = useState<ImgSource>("ai");
  const [vidSource, setVidSource] = useState<VidSource>("ai");
  const [channels, setChannels] = useState<ChannelId[]>(["vk", "telegram"]);
  const [voice, setVoice] = useState(VOICES[0]);
  const [length, setLength] = useState(LENGTHS[0]);
  const [publishMode, setPublishMode] = useState<null | "publish" | "schedule">(null);

  const [media, setMedia] = useState<Media>({ kind: "none" });
  const photos = useAttachments(); // фото к запросу (контекст для ИИ)
  const [doneSteps, setDoneSteps] = useState(0);

  // результат
  const [text, setText] = useState("");
  const [hashtags, setHashtags] = useState<string[]>([]);
  const [newTag, setNewTag] = useState("");
  const [aiOpen, setAiOpen] = useState(false);

  const photoInput = useRef<HTMLInputElement>(null);
  const videoInput = useRef<HTMLInputElement>(null);
  const textRef = useRef<HTMLTextAreaElement>(null);
  const aiRef = useRef<HTMLDivElement>(null);
  const objectUrls = useRef<string[]>([]);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);
  useClickOutside(aiRef, () => setAiOpen(false));
  useEffect(() => () => { objectUrls.current.forEach((u) => URL.revokeObjectURL(u)); if (timer.current) clearInterval(timer.current); }, []);

  useEffect(() => {
    try {
      const p = sessionStorage.getItem("uc_ai_prompt");
      if (p) { setTopic(p); setSettingsShown(true); sessionStorage.removeItem("uc_ai_prompt"); }
    } catch {}
  }, []);

  const onTopic = (v: string) => { setTopic(v); if (v.trim().length >= REVEAL_AT) setSettingsShown(true); };
  const trackUrl = (u: string) => { objectUrls.current.push(u); return u; };
  const aiImage = () => setMedia({ kind: "image", src: IMAGE_POOL[Math.floor(Math.random() * IMAGE_POOL.length)] });
  const aiVideo = () => setMedia({ kind: "video-ai", poster: IMAGE_POOL[0] });
  const onPhoto = (e: ChangeEvent<HTMLInputElement>) => { const f = e.target.files?.[0]; if (f) setMedia({ kind: "image", src: trackUrl(URL.createObjectURL(f)) }); e.target.value = ""; };
  const onVideo = (e: ChangeEvent<HTMLInputElement>) => { const f = e.target.files?.[0]; if (f) setMedia({ kind: "video-file", src: trackUrl(URL.createObjectURL(f)) }); e.target.value = ""; };


  const aiSteps = photos.items.length > 0 ? [PHOTO_STEP, ...AI_STEPS] : AI_STEPS;
  const canCreate = topic.trim().length > 0 || photos.items.length > 0;

  const resolveMedia = (generatedUrl?: string): Media => {
    if (format === "video") return vidSource === "ai" ? { kind: "video-ai", poster: IMAGE_POOL[0] } : media.kind === "video-file" ? media : { kind: "none" };
    if (generatedUrl) return { kind: "image", src: generatedUrl };
    if (imgSource === "none") return { kind: "none" };
    if (imgSource === "upload" && media.kind === "image") return media;
    return { kind: "image", src: IMAGE_POOL[0] };
  };

  const runGeneration = async () => {
    if (!canCreate) return;
    setMode("generating");
    setDoneSteps(0);
    let done = 0;

    timer.current = setInterval(() => {
      done = Math.min(done + 1, aiSteps.length - 1);
      setDoneSteps(done);
    }, 550);

    const savedState = loadOnboarding();
    const activeCompanyName = savedState?.profile?.name || savedState?.input?.name || "UCust";
    const activeNiche = savedState?.profile?.field || savedState?.input?.activity || "Бизнес и услуги";
    const activeCity = savedState?.profile?.market?.geography || "Москва";

    try {
      const res = await submitAiTask({
        task_type: "generate_post",
        payload: {
          prompt: topic,
          format: format,
          tone: voice,
          company_name: activeCompanyName,
          niche: activeNiche,
          city: activeCity,
          generate_image: true,
          aspect_ratio: "1:1",
          refCount: photos.items.length,
        },
      });

      if (!res?.data || !res.data.post_text) {
        throw new Error("Не получен сгенерированный текст от AI-шлюза");
      }

      const generatedPhoto = res?.data?.image_url || res?.data?.photo_url;
      if (!generatedPhoto) {
        throw new Error("Фотография не была сформирована генератором");
      }

      if (timer.current) clearInterval(timer.current);
      setDoneSteps(aiSteps.length);

      const gatewayBase = AI_GATEWAY_URL.replace(/\/api\/v1\/?$/, "");
      const fullPhotoUrl = generatedPhoto.startsWith("http")
        ? generatedPhoto
        : `${gatewayBase}${generatedPhoto}`;

      // Финальное окно открывается ТОЛЬКО когда фото и текст реально получены от генератора
      setTimeout(() => {
        setText(res.data.post_text);
        setHashtags(deriveHashtags(topic));
        setMedia({ kind: "image", src: fullPhotoUrl });
        setMode("edit");
      }, 400);
    } catch (err) {
      console.error("Ошибка при генерации публикации:", err);
      if (timer.current) clearInterval(timer.current);
      toast("Не удалось завершить генерацию: проверьте работу AI-шлюза.");
      setMode("create");
    }
  };

  const runTextAi = (key: string) => {
    setAiOpen(false);
    const r = applyTextAi(key, text);
    setText(r.text);
    if (r.note) toast(r.note);
  };
  const addTag = () => { const t = newTag.trim().replace(/^#/, ""); if (t) { setHashtags((h) => [...new Set([...h, t])]); setNewTag(""); } };

  const publish = () => setPublishMode("publish");
  const schedule = () => setPublishMode("schedule");
  const draft = () => { toast("Сохранено в черновики"); router.push("/dashboard/content"); };
  const startNew = () => { setMode("create"); setTopic(""); setSettingsShown(false); setText(""); setHashtags([]); setMedia({ kind: "none" }); photos.clear(); };

  return (
    <div className="flex flex-col gap-6 lg:min-h-[calc(100dvh-150px)]">
      {/* Заголовок сверху, отделён от контента (как во Входящих) */}
      <div className="border-b border-border pb-4">
        <h1 className="text-xl font-bold text-ink sm:text-2xl">Создать публикацию</h1>
        {mode === "edit" ? (
          <p className="mt-1 inline-flex items-center gap-2 text-sm text-success"><Icon name="check-bold" size={16} aria-hidden="true" /> Публикация готова</p>
        ) : (
          <p className="mt-0.5 text-sm text-ink-muted">Опишите идею. Остальное UCust подготовит автоматически.</p>
        )}
      </div>

      <div className="grid grid-cols-1 gap-8 lg:min-h-0 lg:flex-1 lg:grid-cols-[minmax(0,2fr)_minmax(0,3fr)]">
      {/* ══ ЛЕВО: ПАРАМЕТРЫ И ДЕЙСТВИЯ ══ */}
      <div className="flex flex-col gap-4">
        <div className="flex items-center justify-between pb-1">
          <span className="text-xs font-semibold uppercase tracking-wider text-ink-muted">
            {mode === "edit" ? "Управление публикацией" : "Параметры генерации"}
          </span>
        </div>

        {mode === "edit" ? (
          <div className="uc-fade-in flex flex-col gap-4">
            <div className="flex flex-col gap-2 rounded-2xl border border-border bg-card p-4 shadow-sm">
              <span className="mb-1 text-xs font-semibold uppercase tracking-wider text-ink-muted">Действия с публикацией</span>
              <button type="button" onClick={runGeneration} className="btn-glass-blue flex items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-semibold shadow-sm">
                <Icon name="refresh" size={16} aria-hidden="true" /> Перегенерировать
              </button>
              <button type="button" onClick={() => setMode("create")} className="flex items-center gap-2.5 rounded-xl border border-border bg-surface-soft px-4 py-2.5 text-left text-sm font-medium text-ink transition hover:border-brand/40">
                <Icon name="edit" size={16} className="text-brand" aria-hidden="true" /> Изменить запрос / тему
              </button>
              <button type="button" onClick={() => setAiOpen(true)} className="flex items-center gap-2.5 rounded-xl border border-border bg-surface-soft px-4 py-2.5 text-left text-sm font-medium text-ink transition hover:border-brand/40">
                <Icon name="sparkles" size={16} className="text-brand" aria-hidden="true" /> Улучшить текст с AI
              </button>
            </div>

            <div className="rounded-2xl border border-border bg-card p-4">
              <span className="mb-2 block text-xs font-semibold uppercase tracking-wider text-ink-muted">Текущая тема запроса</span>
              <p className="rounded-xl bg-surface-soft p-3 text-xs leading-relaxed text-ink line-clamp-4">{topic || "Запрос без темы"}</p>
            </div>

            {photos.items.length > 0 && (
              <div className="rounded-2xl border border-border bg-card p-4">
                <span className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-ink-muted">
                  <Icon name="image" size={13} aria-hidden="true" /> Учтены при написании
                </span>
                <div className="flex flex-wrap gap-2">
                  {photos.items.map((r) => (
                    <span key={r.id} className="relative h-12 w-12 overflow-hidden rounded-xl border border-border">
                      <Image src={r.url} alt={r.name} fill unoptimized sizes="48px" className="object-cover" />
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="pt-2">
              <button type="button" onClick={startNew} className="inline-flex items-center gap-2 text-sm font-medium text-brand transition hover:text-brand-hover">
                <Icon name="plus" size={16} aria-hidden="true" /> Создать новую публикацию
              </button>
            </div>
          </div>
        ) : (
          <>
            <PromptComposer
              value={topic}
              onChange={onTopic}
              placeholder="Например: расскажи о новом летнем меню, сделай акцент на авторском кофе и пригласи гостей попробовать новинки."
              attachments={photos.items}
              onAttach={photos.add}
              onRemove={photos.remove}
              max={photos.max}
              disabled={mode === "generating"}
              autoFocus
              onSubmit={runGeneration}
              footer="Можно приложить фото — ИИ учтёт их в тексте"
            />

            {mode === "create" && (
              <div>
                <span className="mb-2 block text-sm font-medium text-ink-muted">С чего начать</span>
                <div className="flex flex-wrap gap-2">
                  {IDEAS.map((idea) => (
                    <button key={idea.label} type="button" onClick={() => onTopic(idea.text)}
                      className="rounded-full border border-border bg-transparent px-4 py-2 text-sm font-medium text-ink-muted transition hover:border-brand/40 hover:text-ink">
                      {idea.label}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {settingsShown && mode === "create" && (
              <div className="uc-fade-in flex flex-col gap-5 lg:flex-1">
                <div>
                  <span className="mb-2.5 block text-sm font-medium text-ink-muted">Формат</span>
                  <RadioPills value={format} onChange={setFormat} options={[{ id: "post", label: "Публикация", icon: "file-text" }, { id: "video", label: "Видео", icon: "clapperboard" }]} />
                </div>

                <div>
                  <span className="mb-2.5 block text-sm font-medium text-ink-muted">{format === "video" ? "Видео" : "Изображение"}</span>
                  {format === "post" ? (
                    <RadioPills value={imgSource} onChange={(v) => { setImgSource(v); if (v === "ai") aiImage(); else if (v === "upload") photoInput.current?.click(); else setMedia({ kind: "none" }); }}
                      options={[{ id: "none", label: "Без изображения" }, { id: "upload", label: "Загрузить своё" }, { id: "ai", label: "Сгенерировать AI" }]} />
                  ) : (
                    <RadioPills value={vidSource} onChange={(v) => { setVidSource(v); if (v === "ai") aiVideo(); else videoInput.current?.click(); }}
                      options={[{ id: "upload", label: "Загрузить своё" }, { id: "ai", label: "Сгенерировать AI" }]} />
                  )}
                </div>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <span className="mb-2 block text-sm font-medium text-ink-muted">Стиль поста</span>
                    <MiniSelect value={voice} options={VOICES} onChange={setVoice} />
                  </div>
                  <div>
                    <span className="mb-2 block text-sm font-medium text-ink-muted">Длина публикации</span>
                    <MiniSelect value={length} options={LENGTHS} onChange={setLength} />
                  </div>
                </div>

                <button type="button" onClick={runGeneration} disabled={!canCreate}
                  className="btn-glass-blue mt-1 inline-flex items-center justify-center gap-2 px-6 py-4 text-base font-semibold disabled:cursor-not-allowed disabled:opacity-50 lg:mt-auto shadow-md">
                  <Icon name="sparkles" size={18} aria-hidden="true" /> Создать публикацию
                </button>
              </div>
            )}
          </>
        )}
        <input ref={photoInput} type="file" accept="image/*" hidden onChange={onPhoto} />
        <input ref={videoInput} type="file" accept="video/*" hidden onChange={onVideo} />
      </div>

      {/* ══ ПРАВО: РАЗДЕЛ ГЕНЕРАЦИИ И ГОТОВОЙ ПУБЛИКАЦИИ ══ */}
      <div className="flex min-h-0 flex-col gap-4">
        <div className="flex items-center justify-between pb-1">
          <span className="text-xs font-semibold uppercase tracking-wider text-ink-muted">
            {mode === "edit" ? "Сгенерированная публикация" : mode === "generating" ? "Раздел генерации" : "Предпросмотр"}
          </span>
          {mode === "edit" && (
            <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-success">
              <Icon name="check-bold" size={13} aria-hidden="true" /> Готово к публикации
            </span>
          )}
        </div>

        {mode === "edit" ? (
          <div className="uc-fade-in flex flex-col gap-4 rounded-[28px] border border-border bg-card p-5 sm:p-6 lg:min-h-0 lg:flex-1 shadow-sm">
            {/* Медиа */}
            {(format === "post" || media.kind !== "none") && (
              <div className="lg:min-h-[220px] lg:flex-[1.3]">
                <MediaEditor media={media} onChange={() => (format === "video" ? videoInput : photoInput).current?.click()} onUpload={() => photoInput.current?.click()} onGenerate={() => (format === "video" ? aiVideo() : aiImage())} onRemove={() => setMedia({ kind: "none" })} />
              </div>
            )}

            {/* Текст */}
            <div ref={aiRef} className={`relative lg:flex lg:min-h-[140px] lg:flex-1 lg:flex-col ${aiOpen ? "z-40" : ""}`}>
              <div className="mb-2 flex shrink-0 items-center justify-between">
                <span className="text-sm font-medium text-ink-muted">Текст публикации</span>
                <button type="button" onClick={() => setAiOpen((v) => !v)} aria-expanded={aiOpen}
                  className="inline-flex items-center rounded-full border border-brand/30 bg-brand/5 px-3 py-1.5 text-xs font-semibold text-brand transition hover:bg-brand/10">
                  Переписать с AI
                </button>
                {aiOpen && (
                  <div className="uc-pop-in absolute right-0 top-9 z-30 w-64 overflow-hidden rounded-2xl border border-border bg-card p-1.5 shadow-lift">
                    {TEXT_AI_ACTIONS.map((a) => (
                      <button key={a.key} type="button" onClick={() => runTextAi(a.key)} className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-left text-sm text-ink transition hover:bg-surface-soft">
                        <Icon name={a.icon} size={14} className="shrink-0 text-brand" aria-hidden="true" /> {a.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              {/* Поле с футером: слева счётчик, справа эмодзи */}
              <div className="flex flex-col rounded-2xl border border-transparent bg-surface-soft transition focus-within:border-brand/40 focus-within:bg-card lg:min-h-0 lg:flex-1">
                <textarea ref={textRef} value={text} onChange={(e) => setText(e.target.value)} rows={5}
                  className="w-full flex-1 resize-none bg-transparent px-4 pt-3 text-sm leading-relaxed text-ink outline-none" />
                <div className="flex items-center justify-between gap-2 px-3 pb-2 pt-1">
                  <span className="text-xs text-ink-muted/70">{text.length} символов</span>
                  <EmojiPicker targetRef={textRef} value={text} onChange={setText} />
                </div>
              </div>
            </div>

            {/* Хэштеги */}
            <div>
              <span className="mb-2 block text-sm font-medium text-ink-muted">Хэштеги</span>
              <div className="flex flex-wrap items-center gap-2">
                {hashtags.map((h) => (
                  <span key={h} className="inline-flex items-center gap-1 rounded-full bg-surface-soft px-3 py-1.5 text-xs font-medium text-ink">
                    #{h}
                    <button type="button" onClick={() => setHashtags((x) => x.filter((t) => t !== h))} aria-label={`Убрать #${h}`} className="text-ink-muted transition hover:text-ink"><Icon name="close" size={12} aria-hidden="true" /></button>
                  </span>
                ))}
                <input value={newTag} onChange={(e) => setNewTag(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addTag(); } }}
                  placeholder="+ добавить" className="w-28 rounded-full bg-transparent px-3 py-1.5 text-xs text-ink outline-none placeholder:text-ink-muted/70 focus:bg-surface-soft" />
              </div>
            </div>

            {/* Готовность */}
            <div className="flex items-center gap-2 rounded-2xl bg-success/8 px-3.5 py-2.5 text-sm">
              <Icon name="check-bold" size={16} className="shrink-0 text-success" aria-hidden="true" />
              <span className="font-medium text-ink">Пост готов к публикации</span>
              <span className="truncate text-ink-muted">· проверено AI</span>
            </div>

            {/* Действия */}
            <div className="flex flex-col gap-2 border-t border-border pt-4 sm:flex-row sm:items-center">
              <button type="button" onClick={publish} className="btn-glass-blue inline-flex flex-1 items-center justify-center gap-2 px-4 py-3 text-sm font-semibold"><Icon name="send" size={16} aria-hidden="true" /> Опубликовать</button>
              <button type="button" onClick={schedule} className="btn-glass inline-flex flex-1 items-center justify-center gap-2 px-4 py-3 text-sm font-semibold"><Icon name="calendar-plus" size={16} aria-hidden="true" /> Запланировать</button>
              <button type="button" onClick={draft} className="inline-flex items-center justify-center gap-2 rounded-full px-4 py-3 text-sm font-medium text-ink-muted transition hover:text-ink">Черновик</button>
            </div>
          </div>
        ) : (
          <div className="flex min-h-[540px] flex-col rounded-[28px] border border-border bg-card p-6 sm:p-7 lg:min-h-0 lg:flex-1 shadow-sm">
            {mode === "generating" ? (
              <div className="flex flex-1 flex-col items-center justify-center gap-6 py-10 text-center">
                <span className="flex h-16 w-16 items-center justify-center rounded-3xl bg-brand/10 text-brand shadow-sm">
                  <Icon name="sparkles" size={30} className="animate-pulse" aria-hidden="true" />
                </span>
                <div>
                  <p className="text-lg font-bold text-ink">UCust готовит публикацию</p>
                  <p className="mt-1 text-sm text-ink-muted">Синхронизация с командой ИИ-агентов</p>
                </div>
                <ul className="flex w-full max-w-xs flex-col gap-3.5 text-left">
                  {aiSteps.map((step, i) => {
                    const done = i < doneSteps;
                    const active = i === doneSteps;
                    return (
                      <li key={step} className={`flex items-center gap-3 text-sm font-medium transition-all ${done || active ? "text-ink" : "text-ink-muted/50"}`}>
                        <span className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-semibold transition-all ${
                          done
                            ? "bg-success text-white shadow-sm"
                            : active
                            ? "bg-brand text-white shadow-md animate-pulse"
                            : "bg-surface-soft text-ink-muted/50"
                        }`}>
                          {done ? (
                            <Icon name="check" size={13} aria-hidden="true" />
                          ) : active ? (
                            <Icon name="refresh" size={13} className="animate-spin" aria-hidden="true" />
                          ) : (
                            <span>{i + 1}</span>
                          )}
                        </span>
                        <span>{i + 1}. {step}</span>
                      </li>
                    );
                  })}
                </ul>
              </div>
            ) : (
              /* Плейсхолдер будущей публикации */
              <div className="flex flex-1 flex-col gap-5">
                <div className="grid h-56 w-full sm:h-64 lg:h-auto lg:flex-1 place-items-center rounded-2xl bg-surface-soft text-ink-muted/40">
                  <Icon name={format === "video" ? "clapperboard" : "image"} size={32} aria-hidden="true" />
                </div>
                <div className="flex flex-col gap-2.5">
                  <div className="h-3.5 w-3/4 rounded-full bg-surface-soft" />
                  <div className="h-3.5 w-full rounded-full bg-surface-soft" />
                  <div className="h-3.5 w-full rounded-full bg-surface-soft" />
                  <div className="h-3.5 w-2/3 rounded-full bg-surface-soft" />
                </div>
                <div className="flex flex-wrap gap-2">
                  {[52, 40, 64, 36].map((w, i) => <span key={i} className="h-6 rounded-full bg-surface-soft" style={{ width: w }} />)}
                </div>
                <p className="mt-auto inline-flex items-center gap-1.5 pt-4 text-sm text-ink-muted">
                  <Icon name="sparkles" size={14} className="text-brand" aria-hidden="true" /> Здесь в реальном времени появится сгенерированная публикация
                </p>
              </div>
            )}
          </div>
        )}
      </div>
      </div>

      <PublishFlow mode={publishMode} channels={channels} onChange={setChannels}
        onClose={() => setPublishMode(null)}
        onDone={() => { setPublishMode(null); router.push("/dashboard/content"); }}
        onNewPost={() => { setPublishMode(null); startNew(); }} />
    </div>
  );
}

/* ── Флоу публикации / планирования: карточки каналов → экран успеха ── */
const CONNECTED = new Set<ChannelId>(["vk", "telegram", "max", "ok", "zen"]);

function ChannelCard({ id, on, onToggle }: { id: ChannelId; on: boolean; onToggle: () => void }) {
  const ch = CHANNELS[id];
  const connected = CONNECTED.has(id);
  if (!connected) {
    return (
      <div className="flex flex-col gap-1.5 rounded-2xl border border-dashed border-border bg-transparent p-3.5">
        <span className="flex items-center gap-2 text-sm font-medium text-ink-muted">{channelIcon(id, 18)} {ch.label}</span>
        <span className="text-xs text-ink-muted/70">Не подключён</span>
        <button type="button" onClick={() => toast("Подключение канала скоро появится")} className="text-left text-xs font-semibold text-brand transition hover:opacity-70">Подключить</button>
      </div>
    );
  }
  return (
    <button type="button" onClick={onToggle} aria-pressed={on}
      className={`relative flex items-center gap-2.5 rounded-2xl border p-3.5 text-left transition ${on ? "border-brand bg-brand/8" : "border-border hover:border-brand/40"}`}>
      {channelIcon(id, 20)}
      <span className="min-w-0 flex-1 truncate text-sm font-medium text-ink">{ch.label}</span>
      <span className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full border transition ${on ? "border-brand bg-brand text-white" : "border-border"}`}>{on && <Icon name="check" size={12} aria-hidden="true" />}</span>
    </button>
  );
}

function PublishFlow({ mode, channels, onChange, onClose, onDone, onNewPost }: {
  mode: null | "publish" | "schedule"; channels: ChannelId[]; onChange: (v: ChannelId[]) => void;
  onClose: () => void; onDone: () => void; onNewPost: () => void;
}) {
  const [mounted, setMounted] = useState(false);
  const [step, setStep] = useState<"form" | "done">("form");
  const [date, setDate] = useState(isoOffset(1));
  const [time, setTime] = useState("12:00");
  useEffect(() => setMounted(true), []);
  useEffect(() => { if (mode) setStep("form"); }, [mode]);
  useEffect(() => {
    if (!mode) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    document.addEventListener("keydown", onKey);
    const prev = document.body.style.overflow; document.body.style.overflow = "hidden";
    return () => { document.removeEventListener("keydown", onKey); document.body.style.overflow = prev; };
  }, [mode, onClose]);
  if (!mounted || !mode) return null;

  const isSchedule = mode === "schedule";
  const toggle = (id: ChannelId) => onChange(channels.includes(id) ? channels.filter((x) => x !== id) : [...channels, id]);
  const chosen = channels.filter((c) => CONNECTED.has(c));

  return createPortal(
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div className="uc-fade-in absolute inset-0 bg-ink/50 backdrop-blur-sm" onClick={onClose} aria-hidden="true" />
      <div role="dialog" aria-modal="true" aria-label={isSchedule ? "Запланировать" : "Опубликовать"} className="uc-modal-in relative flex max-h-[92vh] w-full max-w-lg flex-col overflow-hidden rounded-[28px] border border-border bg-card shadow-lift">
        {step === "form" ? (
          <>
            <div className="flex items-center justify-between border-b border-border px-5 py-4">
              <span className="text-base font-bold text-ink">{isSchedule ? "Запланировать публикацию" : "Опубликовать публикацию"}</span>
              <button type="button" onClick={onClose} aria-label="Закрыть" className="flex h-9 w-9 items-center justify-center rounded-full text-ink-muted transition hover:bg-surface-soft hover:text-ink"><Icon name="close" size={20} aria-hidden="true" /></button>
            </div>

            <div className="flex-1 overflow-y-auto p-5">
              <span className="mb-2.5 block text-sm font-medium text-ink-muted">Выберите площадки</span>
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                {CHANNEL_ORDER.map((id) => <ChannelCard key={id} id={id} on={channels.includes(id)} onToggle={() => toggle(id)} />)}
              </div>

              {isSchedule && (
                <div className="mt-5 grid grid-cols-2 gap-3 border-t border-border pt-5">
                  {/* Дата и время — те же контролы, что и в редактировании публикации */}
                  <div>
                    <span className="mb-1.5 block text-sm font-medium text-ink-muted">Дата</span>
                    <DateField value={date} onChange={setDate} variant="field" />
                  </div>
                  <div>
                    <span className="mb-1.5 block text-sm font-medium text-ink-muted">Время</span>
                    <TimeInput value={time} onChange={setTime} variant="field" ariaLabel="Время публикации" />
                  </div>
                  <div>
                    <span className="mb-1.5 block text-sm font-medium text-ink-muted">Часовой пояс</span>
                    <div className="rounded-2xl bg-surface-soft px-4 py-2.5 text-sm text-ink-muted">Europe/Moscow</div>
                  </div>
                  <div>
                    <span className="mb-1.5 block text-sm font-medium text-ink-muted">Повторять</span>
                    <div className="rounded-2xl bg-surface-soft px-4 py-2.5 text-sm text-ink-muted">Нет</div>
                  </div>
                </div>
              )}

              {chosen.length > 1 && (
                <p className="mt-4 inline-flex items-start gap-1.5 text-xs text-ink-muted"><Icon name="sparkles" size={13} className="mt-px shrink-0 text-brand" aria-hidden="true" /> Публикация будет адаптирована автоматически под каждую выбранную площадку.</p>
              )}
            </div>

            <div className="flex items-center gap-2 border-t border-border p-4">
              <button type="button" onClick={onClose} className="inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-medium text-ink-muted transition hover:text-ink">Отмена</button>
              <button type="button" onClick={() => setStep("done")} disabled={chosen.length === 0}
                className="btn-glass-blue ml-auto inline-flex items-center justify-center gap-2 px-6 py-3 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-50">
                <Icon name={isSchedule ? "calendar-plus" : "send"} size={16} aria-hidden="true" />
                {isSchedule ? "Запланировать" : "Опубликовать сейчас"}
              </button>
            </div>
          </>
        ) : (
          <div className="flex flex-col items-center gap-5 px-6 py-10 text-center">
            <span className="flex h-16 w-16 items-center justify-center rounded-full bg-success/15 text-success"><Icon name="check-bold" size={32} aria-hidden="true" /></span>
            <div>
              <h2 className="text-lg font-bold text-ink">{isSchedule ? "Публикация запланирована" : "Публикация успешно отправлена"}</h2>
              {isSchedule && <p className="mt-1 text-sm text-ink-muted">{fmtDayMonth(date)}, {time} · Europe/Moscow</p>}
            </div>
            <div className="flex flex-col gap-1.5">
              {chosen.map((id) => (
                <span key={id} className="inline-flex items-center gap-2 text-sm text-ink">{channelIcon(id, 18)} {CHANNELS[id].label} <Icon name="check" size={14} className="text-success" aria-hidden="true" /></span>
              ))}
            </div>
            <div className="mt-2 flex w-full flex-col gap-2 sm:flex-row-reverse">
              <button type="button" onClick={onDone} className="btn-glass-blue inline-flex flex-1 items-center justify-center gap-2 px-5 py-3 text-sm font-semibold">Вернуться в контент-план</button>
              {!isSchedule && <button type="button" onClick={onNewPost} className="inline-flex flex-1 items-center justify-center gap-2 rounded-full border border-border px-5 py-3 text-sm font-semibold text-ink transition hover:bg-surface-soft">Создать ещё публикацию</button>}
            </div>
          </div>
        )}
      </div>
    </div>,
    document.body,
  );
}
