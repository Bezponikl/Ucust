# Hero mesh-шейдер — план внедрения

> **For agentic workers:** REQUIRED SUB-SKILL: используйте superpowers:subagent-driven-development (рекомендуется) или superpowers:executing-plans для выполнения задача-за-задачей. Шаги помечены `- [ ]`.

**Goal:** Заменить Hero-визуал (`/hero.webp`) на полноэкранный тема-зависимый mesh-градиентный WebGL-шейдер в фирменных цветах, с сохранением текстов и CTA.

**Architecture:** `ShaderBackground` (обёртка над `MeshGradient` из `@paper-design/shaders-react`) рендерится как full-bleed фон Hero; наш контент лежит поверх через z-слой. Цвета шейдера и цвет текста переключаются по классу `.dark` на `<html>` через хук `useIsDark`. При `prefers-reduced-motion` вместо canvas — статичный CSS-градиент.

**Tech Stack:** Next.js 16, React 19, Tailwind v4, framer-motion, `@paper-design/shaders-react` (новая зависимость), Playwright (визуальная проверка).

## Global Constraints

- Тема — класс `.dark` на `<html>` (НЕ `prefers-color-scheme`); `@custom-variant dark` уже в `globals.css`.
- Бренд-цвета: `--brand #4f7dff`, `--brand-purple #7b5cff`, `--brand-pink #ff5fa2`, `--brand-orange #ff8c4b`.
- Контейнер: `max-w-(--container-page)`.
- Анимации НЕ ветвить по `useReducedMotion` через разные деревья рендера при гидрации — известная гоча hydration mismatch. Клиентские шейдеры монтировать после гидрации.
- Проект НЕ git-репозиторий → шаги «commit» отсутствуют; фиксация прогресса — галочками в плане.
- Верификация: `npx tsc --noEmit` + `npm run build` + `node scripts/screenshot.mjs` (обе темы) + отсутствие console-ошибок.

---

### Task 1: Установить компонент и зависимость

**Files:**
- Create: `components/ui/hero-shader.tsx` (из 21st CLI ИЛИ фолбэк-код ниже)
- Modify: `package.json` (зависимость `@paper-design/shaders-react`)

**Interfaces:**
- Produces: `export function ShaderBackground({ children }: { children: React.ReactNode }): JSX.Element` — full-bleed контейнер с canvas-шейдером и слотом для overlay-контента.

- [ ] **Step 1: Основной путь — 21st CLI (авторизация пользователя).** Пользователь запускает:
  ```
  npx @21st-dev/cli@beta add designali-in/hero-shader
  ```
  Ожидаемо: создан `components/ui/hero-shader.tsx`, в `package.json` добавлен `@paper-design/shaders-react`.

- [ ] **Step 2: Фолбэк, если авторизация 21st не проходит.** Установить зависимость вручную:
  ```
  npm install @paper-design/shaders-react
  ```
  и создать `components/ui/hero-shader.tsx` со следующим содержимым (базовый публичный паттерн; цвета временные — перекрасим в Task 3):
  ```tsx
  "use client";

  import { MeshGradient } from "@paper-design/shaders-react";

  export function ShaderBackground({ children }: { children: React.ReactNode }) {
    return (
      <div className="relative h-full w-full overflow-hidden">
        <MeshGradient
          className="absolute inset-0 h-full w-full"
          colors={["#0a0b14", "#4f7dff", "#7b5cff", "#ff5fa2", "#ff8c4b"]}
          speed={0.3}
        />
        {children}
      </div>
    );
  }
  ```

- [ ] **Step 3: Проверить, что проект компилируется с новой зависимостью**
  Run: `npx tsc --noEmit`
  Expected: без ошибок про отсутствие модуля `@paper-design/shaders-react`. Если API-пропсы (`colors`/`speed`) не совпали с установленной версией — свериться с типами пакета в `node_modules/@paper-design/shaders-react` и поправить имена пропсов, оставив `colors` массивом hex-строк.

---

### Task 2: Хук `useIsDark`

**Files:**
- Create: `lib/useIsDark.ts`

**Interfaces:**
- Produces: `export function useIsDark(): boolean` — реактивно возвращает `true`, если на `<html>` есть класс `dark`; обновляется при переключении темы. До монтирования возвращает `false` (стабильно для гидрации).

- [ ] **Step 1: Написать хук**
  ```ts
  "use client";

  import { useEffect, useState } from "react";

  export function useIsDark(): boolean {
    const [isDark, setIsDark] = useState(false);

    useEffect(() => {
      const root = document.documentElement;
      const update = () => setIsDark(root.classList.contains("dark"));
      update();
      const observer = new MutationObserver(update);
      observer.observe(root, { attributes: true, attributeFilter: ["class"] });
      return () => observer.disconnect();
    }, []);

    return isDark;
  }
  ```

- [ ] **Step 2: Проверить типы**
  Run: `npx tsc --noEmit`
  Expected: без ошибок.

---

### Task 3: Перекраска под бренд + тема-зависимость + reduced-motion

**Files:**
- Modify: `components/ui/hero-shader.tsx`

**Interfaces:**
- Consumes: `useIsDark` из `lib/useIsDark.ts`; `MeshGradient` из `@paper-design/shaders-react`.
- Produces: тот же `ShaderBackground({ children })`, но с тема-зависимой палитрой и статичным фолбэком при `prefers-reduced-motion`.

- [ ] **Step 1: Переписать `hero-shader.tsx` с палитрами по теме и фолбэком**
  ```tsx
  "use client";

  import { useEffect, useState } from "react";
  import { MeshGradient } from "@paper-design/shaders-react";
  import { useIsDark } from "@/lib/useIsDark";

  // Фирменный градиент: blue → purple → pink → orange
  const DARK_COLORS = ["#0a0b14", "#4f7dff", "#7b5cff", "#ff5fa2", "#ff8c4b"];
  const LIGHT_COLORS = ["#f5f7ff", "#c9d6ff", "#d7ccff", "#ffd0e2", "#ffe0cc"];

  function useReducedMotion(): boolean {
    const [reduced, setReduced] = useState(false);
    useEffect(() => {
      const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
      const update = () => setReduced(mq.matches);
      update();
      mq.addEventListener("change", update);
      return () => mq.removeEventListener("change", update);
    }, []);
    return reduced;
  }

  export function ShaderBackground({ children }: { children: React.ReactNode }) {
    const isDark = useIsDark();
    const reduced = useReducedMotion();
    const colors = isDark ? DARK_COLORS : LIGHT_COLORS;

    return (
      <div className="relative h-full w-full overflow-hidden">
        {reduced ? (
          <div
            aria-hidden
            className="absolute inset-0 h-full w-full"
            style={{
              background: `radial-gradient(120% 120% at 30% 20%, ${colors[1]}, ${colors[2]} 40%, ${colors[0]} 100%)`,
            }}
          />
        ) : (
          <MeshGradient
            className="absolute inset-0 h-full w-full"
            colors={colors}
            speed={0.3}
          />
        )}
        {children}
      </div>
    );
  }
  ```

- [ ] **Step 2: Проверить типы**
  Run: `npx tsc --noEmit`
  Expected: без ошибок.

---

### Task 4: Встроить шейдер в `Hero.tsx`, убрать `HeroArt`

**Files:**
- Modify: `components/Hero.tsx`

**Interfaces:**
- Consumes: `ShaderBackground` из `components/ui/hero-shader.tsx`.

- [ ] **Step 1: Переписать `Hero.tsx` — шейдер-фон + overlay-контент**
  Динамический импорт `ShaderBackground` с `ssr: false` (монтаж после гидрации); убрать импорт и использование `HeroArt`; текст/CTA оставить, обернуть в overlay поверх шейдера; цвет текста — по теме (белый в dark, `--ink` в light) через существующие токены; добавить scrim для читаемости.
  ```tsx
  "use client";

  import dynamic from "next/dynamic";
  import { motion } from "framer-motion";
  import Icon from "./ui/Icon";
  import GradientScrollText from "./GradientScrollText";
  import { useAuthModal } from "./AuthModalProvider";
  import { fadeUp, staggerContainer } from "@/lib/motion";

  const ShaderBackground = dynamic(
    () => import("./ui/hero-shader").then((m) => m.ShaderBackground),
    { ssr: false, loading: () => <div className="absolute inset-0 bg-brand-tint/40" /> }
  );

  export default function Hero() {
    const { openSignup } = useAuthModal();

    return (
      <section className="relative min-h-[85vh] overflow-hidden">
        {/* full-bleed шейдер-фон */}
        <div aria-hidden className="absolute inset-0">
          <ShaderBackground>{null as unknown as React.ReactNode}</ShaderBackground>
        </div>
        {/* scrim для читаемости текста */}
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 bg-white/40 dark:bg-black/40"
        />

        <div className="relative z-10 mx-auto flex min-h-[85vh] max-w-(--container-page) items-center px-4 py-16 sm:px-6">
          <motion.div
            variants={staggerContainer(0.15)}
            initial="hidden"
            animate="visible"
            className="max-w-2xl"
          >
            <motion.p variants={fadeUp} className="kicker mb-5 text-xs text-brand sm:text-sm">
              ИИ-маркетолог для малого бизнеса
            </motion.p>

            <motion.div variants={fadeUp}>
              <GradientScrollText
                as="h1"
                eager
                lines={["Соцсети вашего", "бизнеса ведёт ИИ"]}
                className="text-[34px] font-extrabold leading-[1.08] tracking-tight sm:text-[44px] lg:text-[56px] xl:text-[64px]"
              />
            </motion.div>

            <motion.p
              variants={fadeUp}
              className="mt-5 max-w-xl text-base leading-relaxed text-ink-muted sm:text-lg"
            >
              Расскажите о бизнесе один раз — UCust сам напишет посты в вашем стиле и
              опубликует их в VK, Telegram, MAX и Одноклассниках по расписанию.
            </motion.p>

            <motion.div
              variants={fadeUp}
              className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center"
            >
              <button
                type="button"
                onClick={openSignup}
                className="btn-glass-blue inline-flex items-center justify-center rounded-xl px-6 py-3.5 text-sm font-semibold sm:text-base"
              >
                Попробовать бесплатно
              </button>
              <a
                href="#product-showcase"
                className="btn-glass inline-flex items-center justify-center gap-2 rounded-xl px-6 py-3.5 text-sm font-medium sm:text-base"
              >
                Посмотреть демо
                <Icon name="arrow-right" size={16} />
              </a>
            </motion.div>
          </motion.div>
        </div>
      </section>
    );
  }
  ```
  Примечание: `ShaderBackground` ожидает `children`; здесь фон и контент разведены (шейдер отдельным слоем, контент — своим z-10-слоем), поэтому в шейдер передаём пустой слот. Если чище — можно обернуть контент прямо внутрь `ShaderBackground` как children; тогда убрать отдельный фон-div. Выбрать один вариант при реализации и не дублировать.

- [ ] **Step 2: Проверить типы**
  Run: `npx tsc --noEmit`
  Expected: без ошибок.

- [ ] **Step 3: Собрать проект**
  Run: `npm run build`
  Expected: сборка проходит без ошибок; нет предупреждений про `HeroArt`/`hero.webp` как обязательных (они больше не импортируются в Hero).

---

### Task 5: Визуальная проверка обеих тем и viewport'ов

**Files:** нет изменений кода (только запуск и осмотр).

- [ ] **Step 1: Запустить dev-сервер**
  Run: `npm run dev` (в фоне)
  Expected: сервер на `http://localhost:3000`.

- [ ] **Step 2: Снять скриншоты (светлая тема по умолчанию)**
  Run: `node scripts/screenshot.mjs`
  Expected: в `screenshots/` появились `desktop-full.png`, `desktop-hero.png`, `mobile-full.png` без console-ошибок (скрипт печатает `console errors = []`).

- [ ] **Step 3: Осмотреть `screenshots/desktop-hero.png` и `mobile-full.png`**
  Проверить: mesh-шейдер виден фоном Hero в фирменных цветах; текст и обе кнопки читаемы; вёрстка не разъехалась на мобильном.

- [ ] **Step 4: Проверить тёмную тему**
  Переключить тему тумблером (или выставить `localStorage.theme = "dark"` + класс `dark` на `<html>`), обновить страницу, снять hero-скриншот вручную/скриптом.
  Expected: тёмная база + насыщенные «дымки», белый текст читаем.

- [ ] **Step 5: Проверить reduced-motion фолбэк**
  В DevTools эмулировать `prefers-reduced-motion: reduce`, обновить.
  Expected: вместо canvas — статичный радиальный градиент; нет анимации/нагрузки GPU; текст читаем.

---

## Self-Review (выполнено при написании)

- **Покрытие спеки:** получение компонента (Task 1) ✓; перекраска+тема (Task 3) ✓; встройка в Hero, удаление HeroArt (Task 4) ✓; reduced-motion/ssr-фолбэк (Task 3–4) ✓; критерии готовности → верификация (Task 5) + build (Task 4) ✓.
- **Плейсхолдеры:** нет — код приведён в каждом шаге, цвета и пропсы конкретны.
- **Согласованность типов:** `ShaderBackground({ children })` определён в Task 1, уточнён в Task 3, потребляется в Task 4; `useIsDark(): boolean` определён в Task 2, потребляется в Task 3 — имена совпадают.
- **Риск:** точные имена пропсов `MeshGradient` зависят от версии `@paper-design/shaders-react` — снимается Step 3 Task 1 (сверка с типами пакета) и `tsc`/`build`.
