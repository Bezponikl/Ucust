# Settings Screens Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Business Profile settings screen (`/dashboard/business`) and an Account Settings screen (`/dashboard/account`), reachable via a gear icon in the business switcher and a "Настройки" item in the profile menu.

**Architecture:** Two new client components rendered by two new App Router pages inside the existing `DashboardShell`. A small mock-data module supplies per-business profiles. Shared field/toggle/card components keep both settings screens DRY. All state is local (mock, visual-only), matching the rest of the demo.

**Tech Stack:** Next.js 16 (App Router, client components), React 19, Tailwind v4 tokens already in the project, lucide-react icons, `@/lib/channels` for social channels.

## Global Constraints

- No backend / persistence: forms are visual-only, local `useState`, save shows transient "Сохранено" (0.65s), matching existing `PostModal.save`.
- Styling tokens only: `rounded-[24px]`, `border-border`, `bg-card`, `bg-surface-soft`, `btn-glass-blue`, `text-ink` / `text-ink-muted`, focus `focus:border-brand focus:ring-2 focus:ring-brand-tint`. Dark theme is class-based (`.dark`) — no hardcoded light-only colors.
- Verification per task = `npx tsc --noEmit` clean + a Playwright screenshot (light and, where relevant, dark) against the dev server on `http://localhost:3111`. There is **no** unit-test harness and **no** git repo — do not write pytest tests, do not run `git commit`.
- Tone of Voice is intentionally excluded.
- These two pages are NOT added to the sidebar nav (entry only via gear / profile menu).

---

### Task 1: Business mock-data module

**Files:**
- Create: `lib/dashboard/businesses.ts`

**Interfaces:**
- Produces:
  - `interface SocialLink { id: ChannelId; connected: boolean }`
  - `interface BusinessProfile { id: string; name: string; logo?: string; category: string; address: string; phone: string; site: string; description: string; workStart: string; workEnd: string; daysOff: number[]; socials: SocialLink[] }`
  - `const BUSINESSES: BusinessProfile[]`
  - `function getBusiness(id?: string): BusinessProfile`  // by id, fallback to BUSINESSES[0]
  - `const CATEGORIES: string[]`  // for the «Сфера деятельности» select

- [ ] **Step 1: Create the module**

```ts
import type { ChannelId } from "@/lib/channels";
import { CHANNEL_ORDER } from "@/lib/channels";

export interface SocialLink {
  id: ChannelId;
  connected: boolean;
}

export interface BusinessProfile {
  id: string;
  name: string;
  logo?: string;
  category: string;
  address: string;
  phone: string;
  site: string;
  description: string;
  workStart: string; // "09:00"
  workEnd: string; // "18:00"
  daysOff: number[]; // 0..6 → Пн..Вс
  socials: SocialLink[];
}

export const CATEGORIES = [
  "Кофейня / кафе",
  "Ресторан",
  "Розничный магазин",
  "Салон красоты",
  "Услуги",
  "Онлайн-магазин",
  "Другое",
];

const socials = (connectedIds: ChannelId[]): SocialLink[] =>
  CHANNEL_ORDER.slice(0, 6).map((id) => ({ id, connected: connectedIds.includes(id) }));

export const BUSINESSES: BusinessProfile[] = [
  {
    id: "coffee",
    name: "Кофейня «Утро»",
    category: "Кофейня / кафе",
    address: "Минск, ул. Немига, 5",
    phone: "+375 29 123-45-67",
    site: "utro.coffee",
    description: "Уютная городская кофейня со свежей обжаркой и домашней выпечкой.",
    workStart: "08:00",
    workEnd: "22:00",
    daysOff: [],
    socials: socials(["vk", "telegram"]),
  },
  {
    id: "verdiktor",
    name: "Вердиктор",
    category: "Услуги",
    address: "Москва, ул. Тверская, 12",
    phone: "+7 495 000-00-00",
    site: "verdiktor.ru",
    description: "LegalTech-сервис для малого бизнеса.",
    workStart: "09:00",
    workEnd: "18:00",
    daysOff: [5, 6],
    socials: socials(["telegram"]),
  },
  {
    id: "fashion",
    name: "Fashion Store",
    category: "Онлайн-магазин",
    address: "Санкт-Петербург, Невский пр., 30",
    phone: "+7 812 000-00-00",
    site: "fashion.store",
    description: "Онлайн-магазин одежды и аксессуаров.",
    workStart: "10:00",
    workEnd: "20:00",
    daysOff: [6],
    socials: socials(["vk", "telegram", "instagram"]),
  },
];

export function getBusiness(id?: string): BusinessProfile {
  return BUSINESSES.find((b) => b.id === id) ?? BUSINESSES[0];
}
```

- [ ] **Step 2: Typecheck**

Run: `npx tsc --noEmit`
Expected: exit 0 (no errors). If `CHANNEL_ORDER`/`ChannelId` import paths differ, open `lib/channels.ts` and match the real exports.

---

### Task 2: Shared settings UI primitives

**Files:**
- Create: `components/dashboard/settings/primitives.tsx`

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces (all `"use client"`-safe presentational components):
  - `SettingsCard({ title?, desc?, children, className? })` — section wrapper card.
  - `Field({ label, hint?, value, onChange, type?, placeholder?, editable? })` — labeled input; when `editable` (default true) shows a decorative pencil (`SquarePen`) on the right.
  - `TextArea({ label, value, onChange, placeholder? })`
  - `SelectField({ label, value, onChange, options })`
  - `Toggle({ checked, onChange, label? })` — on/off switch styled with brand.
  - `SaveButton({ onSave })` — «Сохранить изменения»; shows «Сохранено» + Check for 0.65s (internal state).

- [ ] **Step 1: Create the primitives**

```tsx
"use client";

import { useState, type ReactNode } from "react";
import { Check, SquarePen } from "lucide-react";

export function SettingsCard({ title, desc, children, className = "" }: { title?: string; desc?: string; children: ReactNode; className?: string }) {
  return (
    <section className={`rounded-[24px] border border-border bg-card p-5 shadow-soft sm:p-6 ${className}`}>
      {title && <h2 className="text-base font-bold text-ink sm:text-lg">{title}</h2>}
      {desc && <p className="mt-1 text-sm text-ink-muted">{desc}</p>}
      <div className={title ? "mt-4" : ""}>{children}</div>
    </section>
  );
}

const inputCls =
  "w-full rounded-xl border border-border bg-surface-soft px-4 py-2.5 text-sm text-ink outline-none transition focus:border-brand focus:ring-2 focus:ring-brand-tint";

export function Field({ label, hint, value, onChange, type = "text", placeholder, editable = true }: { label: string; hint?: string; value: string; onChange: (v: string) => void; type?: string; placeholder?: string; editable?: boolean }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-semibold text-ink">
        {label} {hint && <span className="font-normal text-ink-muted">{hint}</span>}
      </span>
      <span className="relative block">
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className={`${inputCls} ${editable ? "pr-10" : ""}`}
        />
        {editable && <SquarePen size={15} className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-ink-muted" aria-hidden="true" />}
      </span>
    </label>
  );
}

export function TextArea({ label, value, onChange, placeholder }: { label: string; value: string; onChange: (v: string) => void; placeholder?: string }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-semibold text-ink">{label}</span>
      <textarea value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} className={`min-h-24 resize-none ${inputCls}`} />
    </label>
  );
}

export function SelectField({ label, value, onChange, options }: { label: string; value: string; onChange: (v: string) => void; options: string[] }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-semibold text-ink">{label}</span>
      <select value={value} onChange={(e) => onChange(e.target.value)} className={inputCls}>
        {options.map((o) => <option key={o} value={o}>{o}</option>)}
      </select>
    </label>
  );
}

export function Toggle({ checked, onChange, label }: { checked: boolean; onChange: (v: boolean) => void; label?: string }) {
  return (
    <button type="button" role="switch" aria-checked={checked} aria-label={label} onClick={() => onChange(!checked)}
      className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition ${checked ? "bg-brand" : "bg-ink-muted/40"}`}>
      <span className={`inline-block h-5 w-5 transform rounded-full bg-white shadow transition ${checked ? "translate-x-5" : "translate-x-0.5"}`} />
    </button>
  );
}

export function SaveButton({ onSave }: { onSave?: () => void }) {
  const [saved, setSaved] = useState(false);
  const save = () => { setSaved(true); onSave?.(); setTimeout(() => setSaved(false), 900); };
  return (
    <button type="button" onClick={save} className="btn-glass-blue inline-flex items-center justify-center gap-2 rounded-xl px-5 py-3 text-sm font-semibold">
      {saved ? <Check size={16} aria-hidden="true" /> : null}
      {saved ? "Сохранено" : "Сохранить изменения"}
    </button>
  );
}
```

- [ ] **Step 2: Typecheck**

Run: `npx tsc --noEmit`
Expected: exit 0.

---

### Task 3: Profile menu — «Настройки» entry

**Files:**
- Modify: `components/dashboard/ProfileMenu.tsx`

**Interfaces:**
- Consumes: nothing new.
- Produces: a link `/dashboard/account` inside the profile dropdown.

- [ ] **Step 1: Add the icon import**

In the lucide import line, add `Settings`:
```tsx
import { Sun, Moon, LogOut, Scale, ChevronDown, Settings } from "lucide-react";
```

- [ ] **Step 2: Add the «Настройки» link above the «Правовое» block**

Immediately before the `{/* Правовое ... */}` wrapper `<div className="lg:hidden">`, insert:
```tsx
<Link
  href="/dashboard/account"
  onClick={() => setOpen(false)}
  className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-left text-sm text-ink transition-colors hover:bg-surface-soft"
>
  <Settings size={16} aria-hidden="true" /> Настройки
</Link>
<div className="my-1 h-px bg-border" />
```
(`Link` is already imported in this file.)

- [ ] **Step 3: Typecheck + screenshot**

Run: `npx tsc --noEmit` → exit 0.
Then with dev server up, capture the open profile menu (script pattern in Task 6) and confirm «Настройки» appears above «Правовое».

---

### Task 4: Business switcher — widen + gear icon + real businesses

**Files:**
- Modify: `components/dashboard/ProjectSwitcher.tsx`

**Interfaces:**
- Consumes: `BUSINESSES` from Task 1.
- Produces: gear per row → `router.push(/dashboard/business?id=<id>)`.

- [ ] **Step 1: Swap imports + data**

Replace the `MOCK_PROJECTS` constant and add imports:
```tsx
import { useRouter } from "next/navigation";
import { ChevronDown, Plus, Check, Settings } from "lucide-react";
import { BUSINESSES } from "@/lib/dashboard/businesses";
```
Add `const router = useRouter();` in the component body (next to existing hooks). Delete `const MOCK_PROJECTS = [...]`.

- [ ] **Step 2: Widen the trigger button**

Change the button className max-width from `max-w-[200px] ... sm:max-w-[168px]` to:
```
max-w-[220px] ... sm:max-w-[240px]
```
(keep the rest of the class list unchanged).

- [ ] **Step 3: Render businesses with a gear per row**

Replace the dropdown list body. The current business is `current` (from `data?.businessName`); render `BUSINESSES` as options and add a gear button on the right of each row:
```tsx
{BUSINESSES.map((b) => {
  const active = b.name === current;
  return (
    <div key={b.id} className="group flex items-center gap-1 rounded-xl pr-1 hover:bg-surface-soft">
      <button type="button" onClick={() => setOpen(false)} className="flex min-w-0 flex-1 items-center gap-2 rounded-xl px-3 py-2 text-left">
        <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-surface-soft text-xs font-bold text-ink-muted" aria-hidden="true">{b.name.slice(0, 1)}</span>
        <span className="min-w-0 flex-1 truncate text-sm font-medium text-ink">{b.name}</span>
        {active && <Check size={16} className="shrink-0 text-brand" aria-hidden="true" />}
      </button>
      <button
        type="button"
        aria-label={`Настройки бизнеса ${b.name}`}
        onClick={(e) => { e.stopPropagation(); setOpen(false); router.push(`/dashboard/business?id=${b.id}`); }}
        className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-ink-muted transition hover:bg-card hover:text-brand"
      >
        <Settings size={16} aria-hidden="true" />
      </button>
    </div>
  );
})}
```
Keep the trailing divider + «Добавить проект» button as-is.

- [ ] **Step 4: Typecheck + screenshot**

Run: `npx tsc --noEmit` → exit 0.
Screenshot the open switcher; confirm the button fits a long name and each row has a gear.

---

### Task 5: Business Profile page

**Files:**
- Create: `app/dashboard/business/page.tsx`
- Create: `components/dashboard/business/BusinessSettings.tsx`

**Interfaces:**
- Consumes: `getBusiness`, `BusinessProfile`, `CATEGORIES` (Task 1); `SettingsCard`, `Field`, `TextArea`, `SelectField`, `SaveButton` (Task 2); `CHANNELS`, `CHANNEL_ORDER` from `@/lib/channels`.

- [ ] **Step 1: Page wrapper**

`app/dashboard/business/page.tsx`:
```tsx
import BusinessSettings from "@/components/dashboard/business/BusinessSettings";
export default function Page() {
  return <BusinessSettings />;
}
```

- [ ] **Step 2: Component**

`components/dashboard/business/BusinessSettings.tsx`:
```tsx
"use client";

import { useEffect, useRef, useState, type ChangeEvent } from "react";
import Image from "next/image";
import { ImagePlus, Trash2 } from "lucide-react";
import { CHANNELS } from "@/lib/channels";
import { getBusiness, CATEGORIES, type BusinessProfile } from "@/lib/dashboard/businesses";
import { SettingsCard, Field, TextArea, SelectField, SaveButton } from "@/components/dashboard/settings/primitives";

const WEEK = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];

export default function BusinessSettings() {
  // читаем ?id только на клиенте (Suspense-safe, как в ContentView)
  const [b, setB] = useState<BusinessProfile>(() => getBusiness());
  useEffect(() => {
    const id = new URLSearchParams(window.location.search).get("id") ?? undefined;
    /* eslint-disable react-hooks/set-state-in-effect */
    setB(getBusiness(id));
    /* eslint-enable react-hooks/set-state-in-effect */
  }, []);

  const logoInput = useRef<HTMLInputElement>(null);
  const urls = useRef<string[]>([]);
  useEffect(() => () => urls.current.forEach((u) => URL.revokeObjectURL(u)), []);

  const set = <K extends keyof BusinessProfile>(k: K, v: BusinessProfile[K]) => setB((p) => ({ ...p, [k]: v }));
  const onLogo = (e: ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) { const u = URL.createObjectURL(f); urls.current.push(u); set("logo", u); }
    e.target.value = "";
  };
  const toggleDay = (d: number) => set("daysOff", b.daysOff.includes(d) ? b.daysOff.filter((x) => x !== d) : [...b.daysOff, d]);
  const toggleSocial = (id: string) => set("socials", b.socials.map((s) => s.id === id ? { ...s, connected: !s.connected } : s));

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold text-ink sm:text-3xl">Профиль бизнеса</h1>
        <p className="mt-1 text-sm text-ink-muted">Данные бизнеса и подключённые каналы</p>
      </div>

      {/* Шапка: лого + название */}
      <SettingsCard>
        <div className="flex items-center gap-4">
          <span className="relative flex h-20 w-20 shrink-0 items-center justify-center overflow-hidden rounded-2xl bg-brand-tint text-2xl font-bold text-brand">
            {b.logo ? <Image src={b.logo} alt="" fill unoptimized={b.logo.startsWith("blob:")} className="object-cover" /> : b.name.slice(0, 1)}
          </span>
          <div className="min-w-0">
            <p className="truncate text-lg font-bold text-ink">{b.name || "Название бизнеса"}</p>
            <p className="text-sm text-ink-muted">{b.category}</p>
            <div className="mt-2 flex items-center gap-3 text-sm">
              <button type="button" onClick={() => logoInput.current?.click()} className="inline-flex items-center gap-1.5 font-medium text-brand hover:text-brand-hover"><ImagePlus size={15} /> Загрузить</button>
              {b.logo && <button type="button" onClick={() => set("logo", undefined)} className="text-ink-muted hover:text-ink">Удалить</button>}
            </div>
          </div>
          <input ref={logoInput} type="file" accept="image/*" hidden onChange={onLogo} />
        </div>
      </SettingsCard>

      {/* Основное */}
      <SettingsCard title="Основное">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="Название компании" value={b.name} onChange={(v) => set("name", v)} />
          <SelectField label="Сфера деятельности" value={b.category} onChange={(v) => set("category", v)} options={CATEGORIES} />
          <Field label="Адрес" value={b.address} onChange={(v) => set("address", v)} />
          <Field label="Телефон" value={b.phone} onChange={(v) => set("phone", v)} />
          <Field label="Сайт" value={b.site} onChange={(v) => set("site", v)} />
        </div>
        <div className="mt-4">
          <TextArea label="Описание бизнеса" value={b.description} onChange={(v) => set("description", v)} placeholder="Опишите, чем занимается ваш бизнес" />
        </div>
      </SettingsCard>

      {/* Часы работы */}
      <SettingsCard title="Часы работы">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="Время начала" type="time" editable={false} value={b.workStart} onChange={(v) => set("workStart", v)} />
          <Field label="Время окончания" type="time" editable={false} value={b.workEnd} onChange={(v) => set("workEnd", v)} />
        </div>
        <div className="mt-4">
          <span className="mb-1.5 block text-sm font-semibold text-ink">Выходные дни</span>
          <div className="flex flex-wrap gap-2">
            {WEEK.map((w, i) => {
              const off = b.daysOff.includes(i);
              return (
                <button key={w} type="button" aria-pressed={off} onClick={() => toggleDay(i)}
                  className={`rounded-xl border px-3.5 py-2 text-sm font-medium transition ${off ? "border-brand bg-brand/8 text-brand" : "border-border bg-surface-soft text-ink-muted hover:text-ink"}`}>
                  {w}
                </button>
              );
            })}
          </div>
        </div>
      </SettingsCard>

      {/* Соцсети */}
      <SettingsCard title="Соцсети бизнеса" desc="Подключённые каналы для публикаций">
        <ul className="flex flex-col divide-y divide-border">
          {b.socials.map((s) => {
            const ch = CHANNELS[s.id];
            return (
              <li key={s.id} className="flex items-center gap-3 py-3">
                {ch.icon && ch.iconType !== "wordmark"
                  ? <Image src={ch.icon} alt="" width={22} height={22} className="h-[22px] w-[22px] object-contain" aria-hidden="true" />
                  : <span className="h-[22px] w-[22px] rounded" style={{ backgroundColor: ch.colorVar }} aria-hidden="true" />}
                <span className="flex-1 text-sm font-medium text-ink">{ch.label}</span>
                {s.connected ? (
                  <span className="flex items-center gap-3 text-sm">
                    <span className="font-medium text-success">Подключено</span>
                    <button type="button" className="text-ink-muted hover:text-ink">Редактировать</button>
                    <button type="button" onClick={() => toggleSocial(s.id)} className="text-red-500 hover:text-red-600">Отключить</button>
                  </span>
                ) : (
                  <button type="button" onClick={() => toggleSocial(s.id)} className="text-sm font-medium text-brand hover:text-brand-hover">Подключить</button>
                )}
              </li>
            );
          })}
        </ul>
      </SettingsCard>

      {/* Действия */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <SaveButton />
        <button type="button" className="inline-flex items-center gap-2 self-start rounded-xl px-4 py-3 text-sm font-semibold text-red-500 transition hover:bg-red-500/10">
          <Trash2 size={16} aria-hidden="true" /> Удалить бизнес
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Typecheck**

Run: `npx tsc --noEmit` → exit 0. If `CHANNELS[id].colorVar`/`iconType` names differ, match `lib/channels.ts` (same usage exists in `CreateView.tsx`).

- [ ] **Step 4: Screenshot light + dark**

With dev server up, capture `/dashboard/business?id=coffee` at 900×1400 in `colorScheme: light` and `dark`. Confirm: header logo/initial, все секции, выходные-тоглы, соцсети статусы, Сохранить + Удалить бизнес.

---

### Task 6: Account Settings page

**Files:**
- Create: `app/dashboard/account/page.tsx`
- Create: `components/dashboard/account/AccountSettings.tsx`

**Interfaces:**
- Consumes: `SettingsCard`, `Field`, `Toggle`, `SaveButton` (Task 2).

- [ ] **Step 1: Page wrapper**

`app/dashboard/account/page.tsx`:
```tsx
import AccountSettings from "@/components/dashboard/account/AccountSettings";
export default function Page() {
  return <AccountSettings />;
}
```

- [ ] **Step 2: Component**

`components/dashboard/account/AccountSettings.tsx`:
```tsx
"use client";

import { useEffect, useRef, useState, type ChangeEvent } from "react";
import Image from "next/image";
import { ImagePlus, LogOut, Monitor } from "lucide-react";
import { SettingsCard, Field, Toggle, SaveButton } from "@/components/dashboard/settings/primitives";

const EMAIL_NOTIFS = ["Новые отзывы", "Завершение публикации постов", "Критичные вопросы в чат-боте", "Еженедельный отчёт"];
const PUSH_NOTIFS = ["Новые отзывы", "Завершение публикации постов", "Критичные вопросы в чат-боте", "Напоминание о еженедельном отчёте"];
const SESSIONS = [
  { device: "Samsung Galaxy A23", os: "Android 10.10.1", city: "Минск, Беларусь", time: "07:09", current: true },
  { device: "MacBook Pro", os: "Chrome · macOS", city: "Минск, Беларусь", time: "вчера", current: false },
];

export default function AccountSettings() {
  const [firstName, setFirstName] = useState("Анна");
  const [lastName, setLastName] = useState("Иванова");
  const [middleName, setMiddleName] = useState(""); // отчество — опционально
  const [role, setRole] = useState("Маркетолог");
  const [email, setEmail] = useState("anna@example.com");
  const [phone, setPhone] = useState("+7 900 000-00-00");
  const [avatar, setAvatar] = useState<string | undefined>();
  const [twoFa, setTwoFa] = useState(false);
  const [emailN, setEmailN] = useState<boolean[]>([true, false, false, false]);
  const [pushN, setPushN] = useState<boolean[]>([true, false, false, false]);

  const avatarInput = useRef<HTMLInputElement>(null);
  const urls = useRef<string[]>([]);
  useEffect(() => () => urls.current.forEach((u) => URL.revokeObjectURL(u)), []);
  const onAvatar = (e: ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) { const u = URL.createObjectURL(f); urls.current.push(u); setAvatar(u); }
    e.target.value = "";
  };

  // Имя = Фамилия Имя [Отчество] — отчество только если заполнено
  const fullName = [lastName, firstName, middleName].filter(Boolean).join(" ") || "Имя не указано";
  const initials = ((lastName[0] ?? "") + (firstName[0] ?? "")).toUpperCase() || "U";
  const toggleAt = (arr: boolean[], set: (v: boolean[]) => void, i: number) => set(arr.map((v, idx) => (idx === i ? !v : v)));

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold text-ink sm:text-3xl">Настройки аккаунта</h1>
        <p className="mt-1 text-sm text-ink-muted">Личные данные, уведомления и безопасность</p>
      </div>

      {/* Шапка: аватар + имя */}
      <SettingsCard>
        <div className="flex items-center gap-4">
          <span className="relative flex h-20 w-20 shrink-0 items-center justify-center overflow-hidden rounded-full bg-brand text-2xl font-bold text-white">
            {avatar ? <Image src={avatar} alt="" fill unoptimized className="object-cover" /> : initials}
          </span>
          <div className="min-w-0">
            <p className="truncate text-lg font-bold text-ink">{fullName}</p>
            <p className="text-sm text-ink-muted">{role}</p>
            <div className="mt-2 flex items-center gap-3 text-sm">
              <button type="button" onClick={() => avatarInput.current?.click()} className="inline-flex items-center gap-1.5 font-medium text-brand hover:text-brand-hover"><ImagePlus size={15} /> Загрузить</button>
              {avatar && <button type="button" onClick={() => setAvatar(undefined)} className="text-ink-muted hover:text-ink">Удалить</button>}
            </div>
          </div>
          <input ref={avatarInput} type="file" accept="image/*" hidden onChange={onAvatar} />
        </div>
      </SettingsCard>

      {/* Профиль */}
      <SettingsCard title="Профиль">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="Фамилия" value={lastName} onChange={setLastName} />
          <Field label="Имя" value={firstName} onChange={setFirstName} />
          <Field label="Отчество" hint="(не обязательно)" value={middleName} onChange={setMiddleName} placeholder="Отчество" />
          <Field label="Должность" value={role} onChange={setRole} />
          <Field label="Email" type="email" value={email} onChange={setEmail} />
          <Field label="Телефон" value={phone} onChange={setPhone} />
        </div>
        <div className="mt-5"><SaveButton /></div>
      </SettingsCard>

      {/* Уведомления */}
      <SettingsCard title="Уведомления">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          {[["Email-уведомления", EMAIL_NOTIFS, emailN, setEmailN], ["Push-уведомления", PUSH_NOTIFS, pushN, setPushN]].map(([title, items, arr, set]) => (
            <div key={title as string}>
              <span className="mb-2 block text-sm font-semibold text-ink">{title as string}</span>
              <ul className="flex flex-col gap-2">
                {(items as string[]).map((label, i) => (
                  <li key={label}>
                    <label className="flex items-center gap-2.5 text-sm text-ink">
                      <input type="checkbox" checked={(arr as boolean[])[i]} onChange={() => toggleAt(arr as boolean[], set as (v: boolean[]) => void, i)} className="h-4 w-4 rounded border-border text-brand accent-brand" />
                      {label}
                    </label>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </SettingsCard>

      {/* Безопасность */}
      <SettingsCard title="Безопасность">
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="flex flex-col gap-3">
            <span className="text-sm font-semibold text-ink">Смена пароля</span>
            <Field label="Текущий пароль" type="password" editable={false} value="" onChange={() => {}} placeholder="Текущий пароль" />
            <Field label="Новый пароль" type="password" editable={false} value="" onChange={() => {}} placeholder="Новый пароль" />
            <Field label="Повторите новый пароль" type="password" editable={false} value="" onChange={() => {}} placeholder="Повторите новый пароль" />
            <button type="button" className="btn-glass inline-flex w-fit items-center justify-center rounded-xl px-4 py-2.5 text-sm font-semibold">Обновить пароль</button>
          </div>
          <div>
            <div className="flex items-center justify-between gap-4">
              <div>
                <span className="block text-sm font-semibold text-ink">Двухфакторная аутентификация</span>
                <span className="text-xs text-ink-muted">Дополнительная защита при входе</span>
              </div>
              <Toggle checked={twoFa} onChange={setTwoFa} label="Двухфакторная аутентификация" />
            </div>
            <span className="mb-2 mt-6 block text-sm font-semibold text-ink">Активные сессии</span>
            <ul className="flex flex-col gap-2">
              {SESSIONS.map((s) => (
                <li key={s.device} className="flex items-center gap-3 rounded-2xl border border-border bg-surface-soft px-4 py-3">
                  <Monitor size={18} className="shrink-0 text-ink-muted" aria-hidden="true" />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-ink">{s.device} {s.current && <span className="text-xs font-normal text-success">· текущая</span>}</p>
                    <p className="truncate text-xs text-ink-muted">{s.os} · {s.city} · {s.time}</p>
                  </div>
                  {!s.current && <button type="button" aria-label="Завершить сессию" className="text-ink-muted hover:text-red-500"><LogOut size={16} /></button>}
                </li>
              ))}
            </ul>
            <button type="button" className="mt-3 inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold text-red-500 transition hover:bg-red-500/10">
              <LogOut size={16} aria-hidden="true" /> Выйти со всех устройств
            </button>
          </div>
        </div>
      </SettingsCard>
    </div>
  );
}
```

- [ ] **Step 3: Typecheck**

Run: `npx tsc --noEmit` → exit 0.

- [ ] **Step 4: Screenshot + отчество check**

Capture `/dashboard/account` light + dark. Confirm sections. Then verify the conditional patronymic: with empty Отчество the header shows «Иванова Анна»; type a value into Отчество → header becomes «Иванова Анна <value>».

---

### Task 7: Full verification pass

**Files:** none (verification only).

- [ ] **Step 1: Typecheck whole project**

Run: `npx tsc --noEmit` → exit 0.

- [ ] **Step 2: Production build**

Run: `npx next build`
Expected: compiles; new routes `/dashboard/business` and `/dashboard/account` listed. (If it fails only on Google Fonts fetch, that's the known local-network issue — ignore; Vercel builds fine.)

- [ ] **Step 3: Flow screenshots**

With dev server up, script: open switcher → click a gear → land on `/dashboard/business?id=…`; open profile menu → click «Настройки» → land on `/dashboard/account`. Capture both destinations light + dark. Confirm no console errors.

---

## Self-Review

- **Spec coverage:** switcher widen + gear (Task 4) ✓; profile-menu «Настройки» (Task 3) ✓; business page with logo/name/основное/часы/выходные/соцсети/save/delete, no Tone of Voice (Task 5) ✓; account page avatar/имя-фамилия-отчество(conditional)/должность/email/телефон/уведомления/безопасность/2FA/сессии (Task 6) ✓; mock data module (Task 1) ✓; shared primitives DRY (Task 2) ✓; verification tsc+build+screenshots (Task 7) ✓.
- **Placeholder scan:** every task ships real code; no TBD/TODO.
- **Type consistency:** `BusinessProfile`, `getBusiness`, `CATEGORIES`, `SettingsCard/Field/TextArea/SelectField/Toggle/SaveButton` names identical across producing/consuming tasks.

## Verification helper (reuse across tasks)

Temp script `scripts/_verify.mjs` (delete after): launches Playwright, one context per theme, screenshots a URL. Example:
```js
import { chromium } from "playwright";
const b = await chromium.launch();
for (const theme of ["light", "dark"]) {
  const c = await b.newContext({ viewport: { width: 1200, height: 1400 }, colorScheme: theme });
  const p = await c.newPage();
  await p.goto(process.argv[2] ?? "http://localhost:3111/dashboard/account", { waitUntil: "networkidle" });
  await p.waitForTimeout(800);
  await p.screenshot({ path: `scripts/_shot-${theme}.png` });
  await c.close();
}
await b.close();
```
