# Онбординг проекта — дизайн

Дата: 2026-06-28
Статус: утверждён к реализации

## Цель

После регистрации и подтверждения почты пользователь проходит онбординг проекта:
визард сбора данных о бизнесе → экран анализа → превью сгенерированного бренд-профиля
(«мозг бренда») с возможностью правки → переход в дашборд.

Адаптация присланного примера (10 экранов) под дизайн-систему ЮКаст: бренд-синий
`#4f7dff`, палитра (purple/pink/orange/success), скруглённые карточки на `bg-card`/
`surface-soft` с `border`, glass-кнопки, шрифт Manrope, обе темы (light/dark) по теме сайта.
Без тёмных блоков-«плашек» из оригинала — только токены палитры.

## Природа и скоуп

- **Гибрид: моки сейчас, API потом.** Чистый слой данных (типы + функция-заглушка
  `analyzeBusiness`), который позже подменяется на реальный fetch без изменения UI.
- Строим **весь флоу целиком**: визард (3 шага) → анализ → превью профиля (5 разделов).
- **Вне скоупа:** реальный бэкенд/ML, реальный OAuth соцсетей, реальная загрузка файлов
  (всё имитируется), полноценный дашборд (пока заглушка `/dashboard`, реальный — следующей
  итерацией).

## Архитектура (подход A: state-machine + ревью отдельным роутом)

### Роуты (App Router)

```
app/verify-email/page.tsx        — экран подтверждения почты (имитация)
app/onboarding/layout.tsx        — OnboardingProvider + полноэкранный каркас
app/onboarding/page.tsx          — визард: шаги 1–3 + экран анализа (клиентский state-machine)
app/onboarding/review/page.tsx   — превью бренд-профиля (sidebar + 5 разделов)
app/dashboard/page.tsx           — заглушка «Дашборд скоро»
```

### Слой данных

```
lib/onboarding/types.ts    — WizardInput, BrandProfile и под-типы
lib/onboarding/presets.ts  — пресеты бренд-профиля по нишам + выбор по ключевым словам
lib/onboarding/mock.ts     — analyzeBusiness(input): Promise<BrandProfile>  (≈2.5с + пресет)
lib/onboarding/storage.ts  — read/write sessionStorage (ключ ucust:onboarding)
```

`analyzeBusiness` детерминированно собирает `BrandProfile`: подставляет введённые
**название/описание**, выбирает нишевый пресет по ключевым словам, заполняет рынок/SWOT/
услуги/цели данными пресета. Возвращает Promise (имитация задержки). Замена на API —
только тело этой функции.

### Типы (черновик)

```ts
type AboutMode = "link" | "manual";
type SocialId = "instagram" | "vk" | "telegram" | "facebook";

interface WizardInput {
  name: string;
  description?: string;        // шаг 1, необязательно
  aboutMode: AboutMode;        // шаг 2
  link?: string;               // aboutMode=link
  activity?: string;           // aboutMode=manual: чем занимается
  difference?: string;         // aboutMode=manual: чем отличаетесь (необязательно)
  socials: SocialId[];         // подключённые (имитация)
  files: string[];             // имена загруженных файлов (имитация)
}

interface BrandProfile {
  name: string;
  field: string;               // сфера деятельности
  positioning: string;
  market: { competitors: string[]; geography: string; segment: string; trends: string[] };
  swot: { strengths: string[]; weaknesses: string[]; opportunities: string[]; threats: string[] };
  services: { title: string; items: string }[];
  goals: string[];
  tone: string[];              // стиль общения
}
```

### Состояние

`OnboardingProvider` (React-контекст): `input`, `profile`, `setInput(partial)`,
`runAnalysis()` (вызывает `analyzeBusiness`, кладёт `profile`), персист в `sessionStorage`.
Прямой заход на `/onboarding/review` без `profile` → редирект на `/onboarding`.

## Экраны

### `/verify-email`
Карточка по центру: иконка-конверт, заголовок «Подтвердите почту», текст
«Мы отправили письмо на {email}» (email из query/sessionStorage, иначе плейсхолдер),
кнопка **«Я подтвердил почту»** → `/onboarding`, ссылка «Отправить повторно» (имитация,
тост/дизейбл на 30с).

### Каркас визарда (`/onboarding`)
- **Топ-бар** (`OnboardingTopBar`): лого UCust (свап по теме) · переключатель проекта
  (`Кофейня "Зерно" ▾`, декоративный) · `ThemeToggle` · колокольчик с бейджем · аватар+имя.
- **`ProgressSteps`**: 4 сегмента (Название · О бизнесе · Соцсети · Анализ), заполнение
  по текущему шагу, бренд-синий.
- Контент по центру (макс. ширина ~640px), снизу кнопки **«Назад»** (`.btn-glass`) /
  **«Далее»** (`.btn-glass-blue`).

**Шаг 1 — «Как называется ваш бизнес?»**
input «Название» (плейсхолдер «Например: Кофейня Аромат») + textarea «Чем занимается ваш
бизнес? (необязательно)». «Далее» активна при непустом названии.

**Шаг 2 — «Расскажите о бизнесе»**
Табы-переключатели **По ссылке** / **Вручную** (segmented control, активный — синий).
- *По ссылке*: одно поле URL (плейсхолдер `https://example.com или ссылка на VK/Instagram`)
  + подсказка.
- *Вручную*: «Чем занимается бизнес» (input) + «Что отличает вас от конкурентов?
  (необязательно)» (textarea).

**Шаг 3 — «Подключите соцсети»**
4 карточки-кнопки (Instagram, ВКонтакте, Telegram, Facebook) с иконкой бренд-цвета,
названием и подписью «Нажмите для подключения»; по клику — состояние «Подключено»
(галочка, имитация). Ниже — drag-drop зона загрузки файлов (PDF/DOC/XLSX, до 10,
имитация: добавляем имена в список, без реальной отправки). Кнопка **«Начать анализ»**
→ `runAnalysis()` + переход на экран анализа.

**Экран анализа** (тот же роут, состояние `analyzing`)
По центру: анимированная иконка-звезда (знак UCust), «Анализируем ваш бизнес»,
«Это займёт несколько секунд…», прогресс-бар. По завершении `runAnalysis()`
→ `router.push('/onboarding/review')`. Прогресс 4-го сегмента активен.

### Ревью (`/onboarding/review`)
Двухколоночный: слева **sidebar** («← На главную», заголовок «Проект», 5 пунктов с
активным состоянием), справа активный раздел. Навигация — локальное состояние раздела,
кнопки «Назад»/«Далее» переключают разделы; на последнем — **«Готово — перейти в дашборд»**
→ `/dashboard`. На мобильном sidebar превращается в горизонтальные табы/дропдаун.

1. **О проекте** — превью-карточка лого (инициалы/градиент) + поля Название / Сфера
   деятельности / Позиционирование (редактируемые `input`/`textarea`, прокинуты в контекст).
2. **Рынок** — Конкуренты (чипы), карточки География / Сегмент, Тренды рынка (чипы,
   секция «Подробнее»).
3. **SWOT** — 4 квадранта (Сильные `success` · Слабые `pink` · Возможности `brand` ·
   Угрозы `orange`) с цветным маркером и списком пунктов.
4. **Услуги и товары** — карточки с иконкой-градиентом, заголовком и перечнем.
5. **Цели** — цели-чипы (цвета палитры) + «Стиль общения с клиентами» чипы. Кнопка
   «Готово — перейти в дашборд».

### `/dashboard`
Заглушка: лого, «Дашборд скоро», короткий текст, кнопка «На главную». Будет заменена
реальным дашбордом следующей итерацией.

## Нишевые пресеты (мок)

`presets.ts`: 4–5 пресетов + дефолт. Выбор по ключевым словам в `name`+`description`+`activity`:
- **coffee** (кофе, кофейня, кафе, бариста) — пример «Зерно».
- **beauty** (салон, красота, маникюр, барбершоп, парикмахер).
- **retail** (магазин, товары, продажа, шоурум).
- **services** (услуги, юридич, консалтинг, агентство, ремонт).
- **default** — нейтральный универсальный профиль.

Каждый пресет задаёт `field`, `positioning`, `market`, `swot`, `services`, `goals`, `tone`.
`name` всегда из ввода пользователя; `positioning`/`field` — из пресета (правятся в ревью).

## Компоненты (изоляция)

```
components/onboarding/OnboardingProvider.tsx   — контекст + персист
components/onboarding/OnboardingTopBar.tsx      — топ-бар
components/onboarding/ProgressSteps.tsx         — 4-сегментный прогресс
components/onboarding/WizardFlow.tsx            — оркестратор шагов/анализа
components/onboarding/steps/StepBusinessName.tsx
components/onboarding/steps/StepAbout.tsx        — табы link/manual
components/onboarding/steps/StepChannels.tsx     — соцсети + загрузка
components/onboarding/AnalysisScreen.tsx
components/onboarding/review/ProfileSidebar.tsx
components/onboarding/review/ReviewFlow.tsx       — оркестратор разделов
components/onboarding/review/SectionAbout.tsx
components/onboarding/review/SectionMarket.tsx
components/onboarding/review/SectionSwot.tsx
components/onboarding/review/SectionServices.tsx
components/onboarding/review/SectionGoals.tsx
components/onboarding/Field.tsx, Chip.tsx, SocialCard.tsx  — мелкие переиспользуемые
```

Переиспользование: `.btn-glass*`, токены тем, lucide-иконки, framer-motion, бренд-цвета
соцсетей из `lib/channels` где подходят.

## Вход во флоу

`SignupModal` после сабмита → `router.push('/verify-email?email=...')` (демо: без реальной
регистрации). `/verify-email` → `/onboarding`. `/onboarding` также открывается напрямую.

## Тема

Роуты наследуют корневой `app/layout.tsx` (class-based dark + анти-FOUC уже есть), поэтому
тема сайта сохраняется. `ThemeToggle` доступен в топ-баре онбординга.

## Доступность

- Прогресс — `aria-current`/подписи шагов.
- Табы шага 2 — `role="tablist"`, segmented control с клавиатурой.
- Соц-карточки и тогглы — `aria-pressed`.
- Поля — связанные `label`.
- Анимации уважают `prefers-reduced-motion` (без ветвления, влияющего на гидрацию —
  как в существующих компонентах).

## Тестирование/проверка

Визуальная проверка через Playwright (light+dark): проход визарда, экран анализа,
все 5 разделов ревью, мобильная раскладка sidebar. Линт/тайпчек чисты.
```
