# Profile menu rework + account pages (appearance, subscription, support)

## Context

`ProfileMenu.tsx` (avatar dropdown, top-right of `DashboardTopBar`) currently has: profile
info, theme toggle (mobile only), "Настройки" → `/dashboard/account`, "Правовое" (collapsible,
mobile/tablet only — desktop relies on the footer), "Выйти".

This project expands that menu with three new destinations and renames one existing item.
It does **not** touch the visual "windowed card" treatment recently built for Входящие
(Inbox) — applying that frame to every dashboard page is an explicitly separate, larger
follow-up project.

## Scope

1. Rename "Настройки" → "Управление аккаунтом" in `ProfileMenu` (same link, no page changes).
2. New page `/dashboard/appearance` — pick a dashboard background (preset or custom upload).
3. New page `/dashboard/subscription` — current plan, plan switch, payment history.
4. New page `/dashboard/support` — contacts, contact form, FAQ, ticket history.

All new pages are static/mock, consistent with the rest of the dashboard (no real backend).

## 1. Menu changes (`components/dashboard/ProfileMenu.tsx`)

New order of links (icons from the existing Solar set; two new icons added — see §5):

1. "Управление аккаунтом" → `/dashboard/account` — icon `settings` (unchanged link/icon, renamed label)
2. "Оформление" → `/dashboard/appearance` — icon `image`
3. "Подписка" → `/dashboard/subscription` — icon `card` (new)
4. "Поддержка" → `/dashboard/support` — icon `help`
5. Theme toggle — mobile-only, unchanged
6. "Правовое" — collapsible, mobile/tablet-only, unchanged
7. "Выйти" — unchanged

## 2. Appearance page (`/dashboard/appearance`)

**Component:** `components/dashboard/appearance/AppearanceSettings.tsx`, wrapped in the
existing `SettingsCard` pattern for visual consistency with `/dashboard/account`.

**Data:** `lib/dashboard/appearance.ts` exports `BACKGROUND_PRESETS: { id: string; label: string; src: string }[]`
— 8 entries pointing at `public/backgrounds/bg-1.jpg` … `bg-8.jpg` (copied from
`C:\Users\Ант\OneDrive\Desktop\Фоны`, renamed to clean slugs).

**UI:** A responsive grid of tiles:
- First tile: "Без фона" — a plain canvas-colored swatch, no image. This is the default.
- 8 preset tiles — thumbnail of each image.
- Last tile: "Добавить свой" — dashed-border upload tile; opens a file picker
  (`accept="image/*"`). Files over 4 MB are rejected with a toast ("Файл слишком большой,
  максимум 4 МБ"). Accepted files are read via `FileReader` to a data URL and stored as the
  custom background (replaces any previous custom upload — single slot, matching the avatar
  upload pattern in `AccountSettings`).

Clicking any tile applies it **immediately** as the real dashboard background — the live
result IS the preview, no separate mockup panel. The selected tile gets a brand-colored ring
+ checkmark badge, matching the selection style already used elsewhere (e.g. `SelectField`
active-option treatment).

**Persistence & rendering:**
- Extend `DashboardProvider` (`components/dashboard/DashboardProvider.tsx`) with
  `background: string | null` (a CSS background-image URL — preset path, or a data URL for
  custom) and `setBackground(v: string | null)`. Persisted to `localStorage["uc_bg"]`,
  hydrated once on mount alongside the existing `hydrated` flag (same pattern as onboarding
  data — small flash of no-background on first paint is acceptable, unlike the dark/light
  theme which has a blocking anti-FOUC script).
- New `components/dashboard/BackgroundLayer.tsx`: a `fixed inset-0 -z-10` div rendered by
  `DashboardShell`, painting `background-image` (cover, centered) when `background` is set,
  plus a theme-aware scrim overlay for legibility (heavier dark tint in dark theme, lighter
  in light theme — same idea as the landing-page hero scrim). When `background` is `null`,
  the layer is invisible and the existing solid `bg-canvas` shows through unchanged.
- No changes required to `DashboardSidebar` (already `bg-card/80 backdrop-blur-xl`, so it
  naturally reads as frosted glass over the new background) or to individual page cards
  (already solid `bg-card`).

## 3. Subscription page (`/dashboard/subscription`)

**Component:** `components/dashboard/subscription/SubscriptionSettings.tsx`.

**Data:** reuse the tariff shape from `components/Pricing.tsx` (`PLANS`: Старт 1500₽,
Бизнес 3500₽) plus a third "Свой тариф" card pointing at the existing
`TariffConfigurator` flow. Mock current-subscription state: plan = "Бизнес", renews
"11 августа 2026", status = active.

**UI sections (top to bottom, `SettingsCard` per section):**
1. **Текущий тариф** — plan name, price, next renewal date, bullet list of what's included
   (reuse the plan's `features` array).
2. **Сменить тариф** — the 3 plan cards (Старт / Бизнес / Свой тариф).
   - Selecting Старт/Бизнес opens a confirmation with a single CTA:
     **"Оплатить через ЮKassa"**. No card-number fields anywhere — a short note explains
     payment is handled by ЮKassa's hosted checkout so the app never stores card data.
     Clicking the CTA just shows a toast ("Переход к оплате…" — mock, no real redirect)
     since there's no backend.
   - Selecting "Свой тариф" reuses the existing `TariffConfigurator` component as-is
     (it's already a self-contained controlled modal: `{ open, onClose, onStart }` props).
     `onStart` shows the same "Переход к оплате…" toast and closes the modal, so all three
     plans end at the same mock payment stub.
3. **История платежей** — a simple table/list of mock rows: date, tariff, amount, status
   (Оплачено/Отменено), consistent with the "Активные сессии" list style already in
   `AccountSettings`.

## 4. Support page (`/dashboard/support`)

**Component:** `components/dashboard/support/SupportSettings.tsx`.

**UI sections:**
1. **Контакты** — email, Telegram handle, phone (mock values), each with an icon and a
   copy/open action.
2. **Форма обращения** — subject (`SelectField` or plain `Field`) + message (`TextArea`) +
   submit button. On submit: toast "Обращение отправлено" and a new row is prepended to the
   ticket history below (client-state only, resets on reload — same volatility as other mock
   forms in the app).
3. **FAQ** — accordion of 5-6 Q&A pairs (tariffs, changing plan, data privacy, cancelling,
   supported platforms) using a simple expand/collapse pattern (same interaction as
   "Правовое" in `ProfileMenu`).
4. **История обращений** — list of mock tickets + the ones added via the form this session,
   each with a status badge (Открыт/Закрыт), newest first.

## 5. Icon additions

`scripts/gen-icons.mjs` MAP additions (regenerate `lib/icons/solar.ts` after):
- `card: "card-linear"` — subscription/payment icon
- `receipt: "bill-list-linear"` — payment history icon
- `phone: "phone-linear"` — support contact icon

(`help`, `image`, `message`, `send`, `edit` already exist and are reused as-is.)

## Out of scope (explicitly deferred)

- Applying the Входящие-style rounded/bordered "windowed card" frame to every other
  dashboard page (Дашборд, Контент, Акции, Аналитика, Настройки, etc.). Tracked as a
  separate follow-up redesign project.
- Any real payment/backend integration — the ЮKassa button is a UI-only stub.
- Multiple saved custom backgrounds (only one custom upload slot, replacing on re-upload).
