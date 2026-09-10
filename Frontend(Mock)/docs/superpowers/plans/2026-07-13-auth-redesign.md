# Auth Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the login/signup modals with full-page `/login` and `/signup` flows on a
shared photo background, consolidate the registration terms checkbox into one link to a new
`/legal` hub, and replace the 6-digit email code with a "check your email" + link-confirmation
flow (still fully mocked — there is no backend in this project).

**Architecture:** A new shared layout component (`AuthPageChrome`) renders the full-bleed
`bg-6.jpg` background + scrim + logo once; four new route pages (`/login`, `/signup`,
`/signup/verify-email`, `/signup/confirm`) reuse it and carry over the existing form markup
from `LoginModal.tsx`/`SignupModal.tsx` unchanged. `AuthModalProvider`'s public API
(`useAuthModal().openLogin/openSignup`) is preserved but re-implemented with
`router.push` instead of modal state, so the four existing call sites
(`Navbar.tsx`, `Hero.tsx`, `Pricing.tsx`, `FinalCta.tsx`) need zero changes. Old modal
components and their now-obsolete Playwright debug scripts are deleted once nothing
references them.

**Tech Stack:** Next.js 16 App Router, React 19, Tailwind CSS v4 (design tokens via
`@theme` in `app/globals.css`), Playwright (for manual/visual verification scripts — this
project has no unit test runner).

## Global Constraints

- Reuse existing design tokens only (`bg-card`, `text-ink`, `text-ink-muted`,
  `border-border`, `bg-surface-soft`, `bg-surface-blue`, `btn-glass-blue`, `shadow-lift`) —
  no new raw hex colors or one-off utility values.
- Every interactive element that has a `dark:` variant in the current `LoginModal.tsx` /
  `SignupModal.tsx` keeps that same variant verbatim in the new pages.
- No new npm dependencies.
- Background image is the existing `public/backgrounds/bg-6.jpg` ("Мраморные волны"),
  used as-is — do not crop/recompress/duplicate the file.
- `ModalShell.tsx` is not modified (other modals in the codebase depend on it).
- `LEGAL_DOCS` / `LEGAL_LINKS` content in `lib/legal.ts` is not modified — the hub page only
  lists the existing entries.
- This project has no test runner (no jest/vitest) — verification is done by running the
  dev server and driving it with a Playwright script under `scripts/`, following the exact
  pattern already used in `scripts/auth-modal.mjs` (navigate, act, screenshot to
  `screenshots/`, log `console`/`pageerror` events, assert the array is empty by inspection).

---

## File Structure

**Create:**
- `components/auth/AuthPageChrome.tsx` — shared full-screen background + logo + card shell.
- `app/login/page.tsx` — login page (content moved from `LoginModal.tsx`).
- `app/legal/page.tsx` — legal hub index page.
- `app/signup/page.tsx` — signup step 1 (form), content moved from `SignupModal.tsx` step `"form"`.
- `app/signup/verify-email/page.tsx` — "check your email" screen (replaces step `"code"`).
- `app/signup/confirm/page.tsx` — "email confirmed" screen (replaces `handleConfirm`).
- `scripts/auth-pages-flow.mjs` — new Playwright verification script covering the full new flow.

**Modify:**
- `components/AuthModalProvider.tsx` — re-implement `openLogin`/`openSignup` via
  `router.push`, stop rendering `LoginModal`/`SignupModal`, drop the unused `close` method.
- `components/SignupModal.tsx` — checkbox text updated in Task 4 while the component still
  exists (kept in sync until deletion in Task 8) — see note in Task 4.

**Delete (Task 8, once nothing references them):**
- `components/LoginModal.tsx`
- `components/SignupModal.tsx`
- `scripts/auth-modal.mjs`
- `scripts/auth-modal-debug.mjs`
- `scripts/signup-flow.mjs`

---

### Task 1: `AuthPageChrome` shared layout component

**Files:**
- Create: `components/auth/AuthPageChrome.tsx`

**Interfaces:**
- Produces: `export default function AuthPageChrome({ children }: { children: ReactNode }): JSX.Element` — fixed `bg-6.jpg` background + scrim, logo linking to `/`, close link to `/`, and a centered `bg-card` panel that renders `children`. All later tasks (`/login`, `/signup`, `/signup/verify-email`, `/signup/confirm`) wrap their content in this component.

- [ ] **Step 1: Create the component**

```tsx
// components/auth/AuthPageChrome.tsx
import Image from "next/image";
import Link from "next/link";
import type { ReactNode } from "react";
import Icon from "@/components/ui/Icon";

export default function AuthPageChrome({ children }: { children: ReactNode }) {
  return (
    <div className="relative min-h-dvh">
      <div className="fixed inset-0 -z-10" aria-hidden="true">
        <Image
          src="/backgrounds/bg-6.jpg"
          alt=""
          fill
          priority
          sizes="100vw"
          className="object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-ink/55 via-ink/20 to-ink/65" />
      </div>

      <Link
        href="/"
        aria-label="UCust — на главную"
        className="fixed left-5 top-5 z-10 inline-flex items-center sm:left-8 sm:top-8"
      >
        <Image
          src="/brand/logo-lighttext.webp"
          alt="UCust"
          width={700}
          height={161}
          unoptimized
          className="h-6 w-auto sm:h-7"
        />
      </Link>

      <Link
        href="/"
        aria-label="Закрыть и вернуться на главную"
        className="fixed right-5 top-5 z-10 flex h-9 w-9 items-center justify-center rounded-full bg-white/15 text-white backdrop-blur transition-colors hover:bg-white/25 sm:right-8 sm:top-8"
      >
        <Icon name="close" size={20} aria-hidden="true" />
      </Link>

      <div className="flex min-h-dvh items-center justify-center px-4 py-24 sm:px-6">
        <div className="w-full max-w-md rounded-[28px] bg-card p-7 shadow-lift sm:p-8">
          {children}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify it renders with a throwaway probe page**

Create a temporary file `app/_auth-chrome-probe/page.tsx`:

```tsx
import AuthPageChrome from "@/components/auth/AuthPageChrome";

export default function Probe() {
  return (
    <AuthPageChrome>
      <p className="text-ink">probe content</p>
    </AuthPageChrome>
  );
}
```

Start the dev server and check the route:

```bash
npm run dev
```

In a second terminal:

```bash
node -e "
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto('http://localhost:3000/_auth-chrome-probe', { waitUntil: 'networkidle' });
  await page.screenshot({ path: 'screenshots/auth-chrome-probe.png' });
  await browser.close();
})();
"
```

Expected: `screenshots/auth-chrome-probe.png` shows the bg-6 photo full-bleed, the white
logo top-left, a close icon top-right, and a centered white card containing "probe content".

- [ ] **Step 3: Delete the probe page**

```bash
rm -rf app/_auth-chrome-probe
```

- [ ] **Step 4: Commit**

```bash
git add components/auth/AuthPageChrome.tsx
git commit -m "feat(auth): add shared AuthPageChrome layout for full-page auth screens"
```

---

### Task 2: `/legal` hub page

**Files:**
- Create: `app/legal/page.tsx`

**Interfaces:**
- Consumes: `LEGAL_LINKS`, `LEGAL_UPDATED` from `lib/legal.ts` (already exist, unchanged — `LEGAL_LINKS: { label: string; href: string }[]`).
- Produces: route `/legal` listing all documents. Task 4's signup checkbox links here.

- [ ] **Step 1: Create the page**

```tsx
// app/legal/page.tsx
import type { Metadata } from "next";
import Link from "next/link";
import Icon from "@/components/ui/Icon";
import { LEGAL_LINKS, LEGAL_UPDATED } from "@/lib/legal";

export const metadata: Metadata = { title: "Правовые документы — UCust" };

export default function LegalIndexPage() {
  return (
    <div className="mx-auto max-w-3xl px-5 py-10 sm:px-6 sm:py-14">
      <h1 className="font-display text-2xl font-bold text-ink sm:text-3xl">
        Правовые документы
      </h1>
      <p className="mt-2 text-xs text-ink-muted">Редакция от {LEGAL_UPDATED}</p>

      <div className="mt-8 flex flex-col gap-3">
        {LEGAL_LINKS.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="flex items-center justify-between rounded-2xl border border-border bg-surface-soft px-5 py-4 text-sm font-medium text-ink transition-colors hover:border-brand/40 hover:bg-card"
          >
            {link.label}
            <Icon name="arrow-right" size={18} className="text-ink-muted" aria-hidden="true" />
          </Link>
        ))}
      </div>
    </div>
  );
}
```

This page sits inside `app/legal/`, so it automatically gets the existing
`app/legal/layout.tsx` chrome (header with logo + "На главную" link, footer) — no layout
changes needed.

- [ ] **Step 2: Verify**

With `npm run dev` running:

```bash
node -e "
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('http://localhost:3000/legal', { waitUntil: 'networkidle' });
  await page.screenshot({ path: 'screenshots/legal-hub.png' });
  console.log('links found:', await page.locator('a[href^=\"/legal/\"]').count());
  console.log('errors:', errors);
  await browser.close();
})();
"
```

Expected: `links found: 3` (offer, privacy, pdn-consent), `errors: []`.

- [ ] **Step 3: Commit**

```bash
git add app/legal/page.tsx
git commit -m "feat(legal): add /legal hub page listing all legal documents"
```

---

### Task 3: `/login` page

**Files:**
- Create: `app/login/page.tsx`

**Interfaces:**
- Consumes: `AuthPageChrome` (Task 1), `Checkbox` from `components/ui/Checkbox.tsx`, `seedDemoProject` from `lib/onboarding/demo.ts` (existing, signature `(): void`).
- Produces: route `/login`. Task 6 (`AuthModalProvider`) will point `openLogin` here.

- [ ] **Step 1: Create the page**

```tsx
// app/login/page.tsx
"use client";

import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import AuthPageChrome from "@/components/auth/AuthPageChrome";
import Checkbox from "@/components/ui/Checkbox";
import { seedDemoProject } from "@/lib/onboarding/demo";

export default function LoginPage() {
  const router = useRouter();

  const enterDashboard = () => {
    seedDemoProject();
    router.push("/dashboard");
  };

  return (
    <AuthPageChrome>
      <h1 className="text-2xl font-bold text-ink sm:text-[28px]">С возвращением</h1>
      <p className="mt-2 text-sm leading-relaxed text-ink-muted">
        Войдите в аккаунт, чтобы продолжить.
      </p>

      <form
        className="mt-6 flex flex-col gap-4"
        onSubmit={(e) => {
          e.preventDefault();
          enterDashboard();
        }}
      >
        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-ink">Email</span>
          <input
            type="email"
            required
            placeholder="you@example.com"
            className="rounded-full border border-border bg-surface-soft px-4 py-3 text-sm text-ink outline-none transition-colors placeholder:text-ink-muted focus:border-brand focus:bg-card"
          />
        </label>

        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-ink">Пароль</span>
          <input
            type="password"
            required
            placeholder="••••••••"
            className="rounded-full border border-border bg-surface-soft px-4 py-3 text-sm text-ink outline-none transition-colors placeholder:text-ink-muted focus:border-brand focus:bg-card"
          />
        </label>

        <div className="flex items-center justify-between text-sm">
          <label className="flex items-center gap-2 text-ink-muted">
            <Checkbox />
            Запомнить меня
          </label>
          <a href="#" className="font-medium text-brand transition-colors hover:text-brand-hover">
            Забыли пароль?
          </a>
        </div>

        <button
          type="submit"
          className="btn-glass-blue mt-1 inline-flex w-full items-center justify-center px-6 py-3.5 text-sm font-semibold"
        >
          Войти
        </button>
      </form>

      <div className="my-5 flex items-center gap-3 text-xs uppercase tracking-wide text-ink-muted">
        <span className="h-px flex-1 bg-border" aria-hidden="true" />
        или
        <span className="h-px flex-1 bg-border" aria-hidden="true" />
      </div>

      <div className="flex flex-col gap-2.5">
        <button
          type="button"
          onClick={enterDashboard}
          className="flex w-full items-center gap-3 rounded-xl border border-border bg-surface-soft px-4 py-3 text-sm font-medium text-ink transition-all hover:border-brand/40 hover:bg-card dark:hover:bg-white/5"
        >
          <Image
            src="/vk.png"
            alt=""
            width={20}
            height={20}
            className="h-5 w-5 shrink-0 object-contain"
            aria-hidden="true"
          />
          <span className="flex-1 text-center">Продолжить с VK</span>
          <span className="w-5" aria-hidden="true" />
        </button>

        <button
          type="button"
          onClick={enterDashboard}
          className="flex w-full items-center gap-3 rounded-xl border border-border bg-surface-soft px-4 py-3 text-sm font-medium text-ink transition-all hover:border-brand/40 hover:bg-card dark:hover:bg-white/5"
        >
          <Image
            src="/yandex.svg"
            alt=""
            width={20}
            height={20}
            className="h-5 w-5 shrink-0"
            aria-hidden="true"
          />
          <span className="flex-1 text-center">Продолжить с Яндексом</span>
          <span className="w-5" aria-hidden="true" />
        </button>
      </div>

      <p className="mt-6 text-center text-sm text-ink-muted">
        Нет аккаунта?{" "}
        <Link href="/signup" className="font-medium text-brand transition-colors hover:text-brand-hover">
          Зарегистрироваться
        </Link>
      </p>
    </AuthPageChrome>
  );
}
```

- [ ] **Step 2: Verify**

With `npm run dev` running:

```bash
node -e "
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle' });
  await page.screenshot({ path: 'screenshots/login-page.png' });
  await page.getByRole('textbox', { name: 'Email' }).fill('demo@example.com');
  await page.locator('input[type=\"password\"]').fill('password123');
  await page.locator('form button[type=\"submit\"]').click();
  await page.waitForURL('**/dashboard', { timeout: 5000 });
  console.log('landed on:', page.url());
  console.log('errors:', errors);
  await browser.close();
})();
"
```

Expected: `landed on: http://localhost:3000/dashboard`, `errors: []`.

- [ ] **Step 3: Commit**

```bash
git add app/login/page.tsx
git commit -m "feat(auth): add full-page /login route"
```

---

### Task 4: `/signup` page (step 1 — form)

**Files:**
- Create: `app/signup/page.tsx`

**Interfaces:**
- Consumes: `AuthPageChrome` (Task 1), `Checkbox`, links to `/legal` (Task 2).
- Produces: route `/signup`. On submit, stores the entered email in
  `sessionStorage.setItem("uc_signup_email", email)` and navigates to
  `/signup/verify-email` (Task 5 reads this key).

- [ ] **Step 1: Create the page**

```tsx
// app/signup/page.tsx
"use client";

import type { FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import AuthPageChrome from "@/components/auth/AuthPageChrome";
import Checkbox from "@/components/ui/Checkbox";

const inputClass =
  "rounded-full border border-border bg-surface-soft px-4 py-3 text-sm text-ink outline-none transition-colors placeholder:text-ink-muted focus:border-brand focus:bg-card";

export default function SignupPage() {
  const router = useRouter();

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const email = new FormData(e.currentTarget).get("email");
    try {
      if (typeof email === "string") sessionStorage.setItem("uc_signup_email", email);
    } catch {}
    router.push("/signup/verify-email");
  };

  return (
    <AuthPageChrome>
      <h1 className="text-2xl font-bold text-ink sm:text-[28px]">Создать аккаунт</h1>
      <p className="mt-2 text-sm leading-relaxed text-ink-muted">
        Первые посты будут готовы через 5 минут — без привязки карты.
      </p>

      <form className="mt-6 flex flex-col gap-4" onSubmit={handleSubmit}>
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="flex flex-col gap-1.5">
            <span className="text-sm font-medium text-ink">Имя</span>
            <input type="text" required placeholder="Иван" className={inputClass} />
          </label>

          <label className="flex flex-col gap-1.5">
            <span className="text-sm font-medium text-ink">Фамилия</span>
            <input type="text" required placeholder="Иванов" className={inputClass} />
          </label>
        </div>

        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-ink">
            Отчество{" "}
            <span className="font-normal text-ink-muted">(не обязательно)</span>
          </span>
          <input type="text" placeholder="Иванович" className={inputClass} />
        </label>

        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-ink">Email</span>
          <input
            name="email"
            type="email"
            required
            placeholder="you@example.com"
            className={inputClass}
          />
        </label>

        <div className="grid gap-4 sm:grid-cols-2">
          <label className="flex flex-col gap-1.5">
            <span className="text-sm font-medium text-ink">Пароль</span>
            <input type="password" required placeholder="••••••••" className={inputClass} />
          </label>

          <label className="flex flex-col gap-1.5">
            <span className="text-sm font-medium text-ink">Повторите пароль</span>
            <input type="password" required placeholder="••••••••" className={inputClass} />
          </label>
        </div>

        <label className="flex items-start gap-2.5 text-sm text-ink-muted">
          <Checkbox required className="mt-0.5" />
          <span>
            Я принимаю{" "}
            <Link
              href="/legal"
              className="font-medium text-brand transition-colors hover:text-brand-hover"
            >
              условия использования
            </Link>
          </span>
        </label>

        <button
          type="submit"
          className="btn-glass-blue mt-1 inline-flex w-full items-center justify-center px-6 py-3.5 text-sm font-semibold"
        >
          Зарегистрироваться
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-ink-muted">
        Уже есть аккаунт?{" "}
        <Link href="/login" className="font-medium text-brand transition-colors hover:text-brand-hover">
          Войти
        </Link>
      </p>
    </AuthPageChrome>
  );
}
```

- [ ] **Step 2: Verify**

With `npm run dev` running:

```bash
node -e "
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('http://localhost:3000/signup', { waitUntil: 'networkidle' });
  await page.screenshot({ path: 'screenshots/signup-page.png' });
  console.log('legal links in checkbox row:', await page.locator('a[href=\"/legal\"]').count());
  await page.getByRole('textbox', { name: 'Имя' }).fill('Иван');
  await page.getByRole('textbox', { name: 'Фамилия' }).fill('Иванов');
  await page.getByRole('textbox', { name: 'Email' }).fill('demo@example.com');
  await page.locator('input[type=\"password\"]').nth(0).fill('password123');
  await page.locator('input[type=\"password\"]').nth(1).fill('password123');
  await page.locator('input[type=\"checkbox\"]').check();
  await page.locator('form button[type=\"submit\"]').click();
  await page.waitForURL('**/signup/verify-email', { timeout: 5000 });
  console.log('landed on:', page.url());
  console.log('errors:', errors);
  await browser.close();
})();
"
```

Expected: `legal links in checkbox row: 1`, `landed on:
http://localhost:3000/signup/verify-email`, `errors: []` (the route itself 404s until
Task 5, so this step is finished once Task 5 is also done — run this check again after
Task 5 if it fails now on the `waitForURL` step).

- [ ] **Step 3: Commit**

```bash
git add app/signup/page.tsx
git commit -m "feat(auth): add full-page /signup route with single legal-hub checkbox link"
```

---

### Task 5: `/signup/verify-email` page

**Files:**
- Create: `app/signup/verify-email/page.tsx`

**Interfaces:**
- Consumes: `AuthPageChrome` (Task 1), reads `sessionStorage.getItem("uc_signup_email")` (written by Task 4).
- Produces: route `/signup/verify-email`.

- [ ] **Step 1: Create the page**

```tsx
// app/signup/verify-email/page.tsx
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import AuthPageChrome from "@/components/auth/AuthPageChrome";
import Icon from "@/components/ui/Icon";

export default function VerifyEmailPage() {
  const [email, setEmail] = useState("");

  useEffect(() => {
    try {
      setEmail(sessionStorage.getItem("uc_signup_email") ?? "");
    } catch {}
  }, []);

  return (
    <AuthPageChrome>
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-surface-blue text-brand">
        <Icon name="mail" size={24} aria-hidden="true" />
      </div>

      <h1 className="mt-5 text-2xl font-bold text-ink sm:text-[28px]">Проверьте почту</h1>
      <p className="mt-2 text-sm leading-relaxed text-ink-muted">
        Мы отправили ссылку для подтверждения{email ? ` на ${email}` : ""}. Перейдите по
        ней, чтобы завершить регистрацию.
      </p>

      <button
        type="button"
        className="btn-glass-blue mt-6 inline-flex w-full items-center justify-center px-6 py-3.5 text-sm font-semibold"
      >
        Отправить письмо ещё раз
      </button>

      <Link
        href="/signup"
        className="mt-3 block text-center text-sm text-ink-muted transition-colors hover:text-ink"
      >
        ← Изменить email
      </Link>
    </AuthPageChrome>
  );
}
```

- [ ] **Step 2: Verify**

With `npm run dev` running:

```bash
node -e "
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('http://localhost:3000/signup', { waitUntil: 'networkidle' });
  await page.getByRole('textbox', { name: 'Имя' }).fill('Иван');
  await page.getByRole('textbox', { name: 'Фамилия' }).fill('Иванов');
  await page.getByRole('textbox', { name: 'Email' }).fill('verify-demo@example.com');
  await page.locator('input[type=\"password\"]').nth(0).fill('password123');
  await page.locator('input[type=\"password\"]').nth(1).fill('password123');
  await page.locator('input[type=\"checkbox\"]').check();
  await page.locator('form button[type=\"submit\"]').click();
  await page.waitForURL('**/signup/verify-email', { timeout: 5000 });
  await page.screenshot({ path: 'screenshots/signup-verify-email.png' });
  console.log('body has email:', (await page.textContent('body'))?.includes('verify-demo@example.com'));
  console.log('errors:', errors);
  await browser.close();
})();
"
```

Expected: `body has email: true`, `errors: []`.

- [ ] **Step 3: Commit**

```bash
git add app/signup/verify-email/page.tsx
git commit -m "feat(auth): add /signup/verify-email screen replacing the 6-digit code step"
```

---

### Task 6: `/signup/confirm` page

**Files:**
- Create: `app/signup/confirm/page.tsx`

**Interfaces:**
- Consumes: `AuthPageChrome` (Task 1).
- Produces: route `/signup/confirm`. Continuing sets `sessionStorage.uc_show_setup = "1"` and navigates to `/onboarding` (same side effect as the old `SignupModal.handleConfirm`).

- [ ] **Step 1: Create the page**

```tsx
// app/signup/confirm/page.tsx
"use client";

import { useRouter } from "next/navigation";
import AuthPageChrome from "@/components/auth/AuthPageChrome";
import Icon from "@/components/ui/Icon";

export default function ConfirmEmailPage() {
  const router = useRouter();

  const handleContinue = () => {
    try {
      sessionStorage.setItem("uc_show_setup", "1");
    } catch {}
    router.push("/onboarding");
  };

  return (
    <AuthPageChrome>
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-surface-blue text-brand">
        <Icon name="mail-check" size={24} aria-hidden="true" />
      </div>

      <h1 className="mt-5 text-2xl font-bold text-ink sm:text-[28px]">Почта подтверждена</h1>
      <p className="mt-2 text-sm leading-relaxed text-ink-muted">
        Регистрация завершена. Переходите в кабинет — настроим ваш проект за пару минут.
      </p>

      <button
        type="button"
        onClick={handleContinue}
        className="btn-glass-blue mt-6 inline-flex w-full items-center justify-center px-6 py-3.5 text-sm font-semibold"
      >
        Продолжить
      </button>
    </AuthPageChrome>
  );
}
```

- [ ] **Step 2: Verify**

With `npm run dev` running:

```bash
node -e "
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('http://localhost:3000/signup/confirm', { waitUntil: 'networkidle' });
  await page.screenshot({ path: 'screenshots/signup-confirm.png' });
  await page.locator('button', { hasText: 'Продолжить' }).click();
  await page.waitForURL('**/onboarding', { timeout: 5000 });
  console.log('landed on:', page.url());
  console.log('errors:', errors);
  await browser.close();
})();
"
```

Expected: `landed on: http://localhost:3000/onboarding`, `errors: []`.

- [ ] **Step 3: Commit**

```bash
git add app/signup/confirm/page.tsx
git commit -m "feat(auth): add /signup/confirm success screen"
```

---

### Task 7: Rewire `AuthModalProvider` to navigate instead of opening modals

**Files:**
- Modify: `components/AuthModalProvider.tsx` (full rewrite, see below)

**Interfaces:**
- Consumes: nothing new.
- Produces: `useAuthModal(): { openLogin: () => void; openSignup: () => void }` — the
  `close` method is removed (confirmed unused everywhere outside this file). All 4 existing
  consumers (`Navbar.tsx`, `Hero.tsx`, `Pricing.tsx`, `FinalCta.tsx`) keep compiling and
  working unchanged, since they only ever destructured `openLogin`/`openSignup`.

- [ ] **Step 1: Rewrite the provider**

```tsx
// components/AuthModalProvider.tsx
"use client";

import { createContext, useContext, type ReactNode } from "react";
import { useRouter } from "next/navigation";

interface AuthModalContextValue {
  openLogin: () => void;
  openSignup: () => void;
}

const AuthModalContext = createContext<AuthModalContextValue | null>(null);

export function useAuthModal() {
  const ctx = useContext(AuthModalContext);
  if (!ctx) {
    throw new Error("useAuthModal must be used within AuthModalProvider");
  }
  return ctx;
}

export default function AuthModalProvider({ children }: { children: ReactNode }) {
  const router = useRouter();

  const value: AuthModalContextValue = {
    openLogin: () => router.push("/login"),
    openSignup: () => router.push("/signup"),
  };

  return <AuthModalContext.Provider value={value}>{children}</AuthModalContext.Provider>;
}
```

- [ ] **Step 2: Verify the build has no type errors**

```bash
npm run build
```

Expected: build succeeds (no TypeScript errors about `close` being missing, since no
consumer destructures it).

- [ ] **Step 3: Verify the header buttons now navigate**

With `npm run dev` running:

```bash
node -e "
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
  await page.getByRole('button', { name: 'Войти' }).click();
  await page.waitForURL('**/login', { timeout: 5000 });
  console.log('login nav ok:', page.url());
  await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
  await page.getByRole('button', { name: 'Зарегистрироваться' }).click();
  await page.waitForURL('**/signup', { timeout: 5000 });
  console.log('signup nav ok:', page.url());
  console.log('errors:', errors);
  await browser.close();
})();
"
```

Expected: `login nav ok: http://localhost:3000/login`, `signup nav ok:
http://localhost:3000/signup`, `errors: []`.

- [ ] **Step 4: Commit**

```bash
git add components/AuthModalProvider.tsx
git commit -m "refactor(auth): AuthModalProvider navigates to /login and /signup instead of opening modals"
```

---

### Task 8: Remove obsolete modal components and debug scripts

**Files:**
- Delete: `components/LoginModal.tsx`
- Delete: `components/SignupModal.tsx`
- Delete: `scripts/auth-modal.mjs`
- Delete: `scripts/auth-modal-debug.mjs`
- Delete: `scripts/signup-flow.mjs`
- Create: `scripts/auth-pages-flow.mjs` (consolidated replacement covering the full new flow)

**Interfaces:**
- Consumes: nothing (leaf cleanup task, runs after Task 7 confirms nothing imports the old modals).

- [ ] **Step 1: Confirm nothing still imports the old modals**

```bash
grep -rn "LoginModal\|SignupModal" --include="*.tsx" --include="*.ts" components app
```

Expected: no output (after Task 7, only `AuthModalProvider.tsx`'s old version referenced
them, and that file was already rewritten in Task 7).

- [ ] **Step 2: Delete the old modal components and debug scripts**

```bash
rm components/LoginModal.tsx components/SignupModal.tsx
rm scripts/auth-modal.mjs scripts/auth-modal-debug.mjs scripts/signup-flow.mjs
```

- [ ] **Step 3: Add the consolidated verification script**

```js
// scripts/auth-pages-flow.mjs
import { chromium } from "playwright";

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await ctx.newPage();
const errors = [];
page.on("console", (msg) => { if (msg.type() === "error") errors.push(msg.text()); });
page.on("pageerror", (err) => errors.push(err.message));

await page.goto("http://localhost:3000", { waitUntil: "networkidle" });
await page.getByRole("button", { name: "Зарегистрироваться" }).click();
await page.waitForURL("**/signup");
await page.screenshot({ path: "screenshots/flow-1-signup.png" });

await page.getByRole("textbox", { name: "Имя" }).fill("Иван");
await page.getByRole("textbox", { name: "Фамилия" }).fill("Иванов");
await page.getByRole("textbox", { name: "Email" }).fill("flow-demo@example.com");
await page.locator('input[type="password"]').nth(0).fill("password123");
await page.locator('input[type="password"]').nth(1).fill("password123");
await page.locator('input[type="checkbox"]').check();
await page.locator('form button[type="submit"]').click();
await page.waitForURL("**/signup/verify-email");
await page.screenshot({ path: "screenshots/flow-2-verify-email.png" });

await page.goto("http://localhost:3000/signup/confirm", { waitUntil: "networkidle" });
await page.screenshot({ path: "screenshots/flow-3-confirm.png" });
await page.locator("button", { hasText: "Продолжить" }).click();
await page.waitForURL("**/onboarding");
console.log("final url:", page.url());

await page.goto("http://localhost:3000/legal", { waitUntil: "networkidle" });
await page.screenshot({ path: "screenshots/flow-4-legal-hub.png" });
console.log("legal doc links:", await page.locator('a[href^="/legal/"]').count());

await page.goto("http://localhost:3000/login", { waitUntil: "networkidle" });
await page.screenshot({ path: "screenshots/flow-5-login.png" });

console.log("errors:", errors);
await browser.close();
```

- [ ] **Step 4: Run the consolidated script**

With `npm run dev` running:

```bash
node scripts/auth-pages-flow.mjs
```

Expected output: `final url: http://localhost:3000/onboarding`, `legal doc links: 3`,
`errors: []`. Inspect the 5 screenshots in `screenshots/` to confirm the bg-6 background,
scrim, and logo appear consistently across all pages.

- [ ] **Step 5: Run the production build one more time**

```bash
npm run build
```

Expected: build succeeds with no errors or warnings about unused/missing imports.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "chore(auth): remove obsolete modal components and debug scripts, add consolidated flow check"
```

---

## Self-Review Notes

- **Spec coverage:** routing table (all 5 routes), `useAuthModal` API preservation, visual
  chrome (bg-6 + scrim + logo, theme-independent), signup content unchanged except
  checkbox, verify-email content, confirm content + side effect, legal hub — all covered by
  Tasks 1–8. Out-of-scope items from the spec (footer/profile-menu legal links, `ModalShell`,
  real email sending) are explicitly not touched by any task.
- **Placeholder scan:** no TBD/TODO; every step has runnable code or commands.
- **Type consistency:** `AuthPageChrome({ children: ReactNode })` signature matches its use
  in Tasks 3, 5, 6 and (implicitly, same shape) Task 4; `sessionStorage` key names
  (`uc_signup_email`, `uc_show_setup`) match between Task 4→5 and Task 6 exactly.
