# Платформа UCust: монорепо фронта и бэка, реальная авторизация, тестовый контур

Дата: 2026-08-05
Статус: утверждён (брейншторм пройден, ждёт вычитки перед планом)

## Контекст

До сих пор фронт (`C:\Claude\UCust`, Next.js 16) и бэк (Spring Boot 4, микросервисы) жили
независимо и ни разу не встречались: во фронте нет ни одного HTTP-вызова к API, в бэке нет
ни одного клиента. Исходники пришли двумя архивами.

**`Ucust-main.zip`** — `Frontend/` в нём это снимок нашего же фронта примерно от 09.07.2026
(`components/Navbar.tsx` бит-в-бит совпадает с коммитом `edf803d`). Локальная версия ушла
вперёд на месяц, поэтому архивный фронт не используется — берём только корневые ТЗ
(`TS backend Ucust.md`, `TS frontend.md`, `TS ML.md`, `Read ME.md`). Папка `src/` в архиве пуста.

**`Ucust-develop.zip`** — `src/N4d3sh1k4-UCust_Dev`, рабочий бэкенд: 134 java-файла,
7 gradle-модулей, каждый сервис оформлен отдельным git-submodule со своим `gradlew`.
Dockerfile'ы multi-stage на `eclipse-temurin:25` — Java и Gradle на хосте не нужны.

Сервер арендован и обследован (05.08.2026): Ubuntu 22.04.5 LTS, ядро 6.2, 10 vCPU, 26 ГБ RAM,
диск 366 ГБ (свободно 322), Tesla V100-SXM2 16 ГБ с драйвером 550.107. Docker не установлен,
репозиторий `docker-ce` не подключён; `sudo` требует пароль.

**Сервер стоит за NAT:** на `eth0` приватный `192.168.12.109/23`, исходящий адрес
`195.208.16.105`, публичного IP нет. Наружу доступны только пробросы провайдера — SSH
`195.208.16.1:40298` и Jupyter `178.18.226.110:8888`; порты 80/443 на хосте свободны, но
снаружи не опубликованы. Доступ ограничен белым списком (`185.14.4.36`).
Это **тестовый контур**, не постоянный прод.

## Цели

1. Свести фронт, бэк, инфраструктуру и ТЗ в один репозиторий `C:\Claude\UCust-Platform`.
2. Перевести на настоящий бэк авторизацию, профиль пользователя и бизнес-проект.
3. Поднять весь стек на арендованном сервере и пройти сквозной сценарий вживую.

## Не-цели

Контент и календарь, промо, отзывы, входящие, аналитика, подписка и вся ИИ-генерация
**остаются на моках** — соответствующих сервисов в бэке не существует. ML-контур
(Saiga, Kandinsky) в этот спек не входит.

## Архитектура

```
     SSH-туннель (разработка)  |  Cloudflare Tunnel → app.ucust.online (показ)
                             │
                        nginx :80/:443
                    ┌────────┴────────┐
                 /  │                 │  /api/v0/*
          frontend:3000          api-gateway:8100
       (Next standalone)      ┌───────┼────────┬──────────┐
                          security  user   business  notification
                            :8101   :8102    :8104      :8103
                              └───────┴────────┴──────────┘
                        postgres:5432   rabbitmq:5672   minio:9000
```

Фронт и API за одним nginx — один origin. Это главное архитектурное решение: httpOnly-кука
`refreshToken` работает без CORS и без `SameSite=None`.

## Структура репозитория

```
C:\Claude\UCust-Platform\
├── frontend/          клон C:\Claude\UCust, ветка platform, remote "showcase"
├── backend/           7 модулей, как обычные папки (submodule'ы раскрыты)
│   ├── api-gateway/ security-service/ user-service/ business-service/
│   ├── notification-service/ configuration-service/ common/
│   └── settings.gradle, gradlew
├── ops/               docker-compose.stack.yml, nginx/, postgres/init.sql,
│                      rabbitmq/definitions.json, .env.example, deploy.sh
├── docs/
│   ├── ts/            ТЗ из main-архива
│   ├── api-contract.md   сводный контракт /api/v0 — источник правды для фронта
│   └── superpowers/specs/
└── README.md
```

### Git-схема

Витрина ведущая по UI. `frontend/` — это `git clone C:\Claude\UCust`, ветка `platform`,
remote `showcase`. UI пилится в витрине, оттуда вливается: `git fetch showcase && git merge
showcase/main`. Чтобы слияния оставались чистыми, интеграционный код живёт **в новых файлах**
(`lib/api/*`, `lib/session/*`), а в существующие экраны вносятся вставки в 1–3 строки.

`ops/.env` с секретами — в `.gitignore`; в репозиторий уходит только `.env.example`.

**Предусловие:** в `C:\Claude\UCust` более 20 незакоммиченных файлов. Их нужно закоммитить
до клонирования, иначе они не попадут в платформу.

## Контракт `/api/v0` и маппинг на экраны

Маршруты задаются в коде (`ApiGatewayApplication.customRouteLocator`), префикс `/api/v0`.
Набор маршрутов в `application.yml` (`/api/auth/**`, `/api/users/**`) устарел и будет удалён.

| Экран | Метод | Тело / примечание |
|---|---|---|
| `/signup` | `POST /auth/register` | `firstName, lastName, email, password, confirmPassword` |
| `/signup/verify-email` | `POST /auth/resend-confirmation?email=` | письмо через RabbitMQ → notification-service |
| ссылка из письма | `GET /auth/confirm-email?token=` | активация аккаунта |
| `/login` | `POST /auth/login` | `{accessToken, type:"Bearer"}` + `Set-Cookie: refreshToken` (httpOnly) |
| авто-продление | `POST /auth/refresh` | по куке: при старте приложения и на каждый 401 |
| выход | `POST /auth/logout` | требует `Authorization: Bearer` |
| `/forgot-password` | `POST /auth/forgot-password` | `{email}` |
| `/forgot-password/reset` | `POST /auth/reset-password` | `{token, newPassword, confirmPassword}` |
| `/dashboard/account` | `GET/PATCH /user/me`, `POST /user/me/avatar` | имя/фамилия только кириллица, телефон `79XXXXXXXXX` |
| онбординг | `POST /projects`, `GET /projects`, `PATCH /projects/{id}`, `POST /projects/{id}/logo` | |

Ошибки — единый `ApiError {status, code, message, time}`; на фронте один маппер в текст.

### Известные расхождения контракта с UI

- Отчество на форме регистрации бэк не принимает — поле остаётся декоративным.
- `firstName`/`lastName` в user-service валидируются регуляркой только на кириллицу,
  телефон — строго `79XXXXXXXXX`. Те же правила дублируются на фронте, чтобы пользователь
  не ловил 400 после отправки.

### Маппинг онбординга в проект

`BrandProfile` фронта богаче `ProjectRequest`: SWOT, услуги, цели, конкуренты и тренды
хранить негде. Решение — добавить в `business-service` колонку **`brand_profile jsonb`**
и складывать туда профиль целиком.

Типизированные поля при этом заполняются:

| Поле бэка | Источник |
|---|---|
| `name` | `WizardInput.name` |
| `description` | `WizardInput.description` (обрезка до 2000) |
| `city` | `BrandProfile.market.geography` |
| `targetAudience` | `BrandProfile.market.segment` (обрезка до 500) |
| `industry` | эвристика по нише пресета → enum из 8, fallback `OTHER` |
| `toneOfVoice` | `BrandProfile.tone[0]` → enum из 4, fallback `FRIENDLY` |
| `socialLinks` | `WizardInput.socials` + `link` |
| `businessHours` | не собирается онбордингом → `null` |

`Industry`: `CAFE_RESTAURANT, BEAUTY_SALON, RETAIL, SERVICES, EDUCATION, FITNESS, MEDICINE, OTHER`.
`ToneOfVoice`: `FRIENDLY, PROFESSIONAL, INFORMAL, CREATIVE`.

## Правки бэка

Бэк правим свободно, но каждую правку держим маленькой и отдельным коммитом — чтобы её
можно было отдать команде PR-ом.

1. **Компиляция.** `AuthController` обращается к полю `yandexAuthService`, которого в классе
   нет, — в текущем виде ветка не собирается. Восстановить поле и внедрение либо временно
   убрать эндпоинты `yandex-mobile`/`link-social`.
2. **Gateway.** `lb://security-service` требует service discovery, которого в стеке нет, —
   заменить на `http://security-service:8101` и т.д. Удалить дублирующие маршруты из
   `application.yml`, оставив единственный источник — `customRouteLocator`.
3. **CORS.** Сейчас разрешены чужие origin'ы (`ucust.n4d3sh1k4.site`, `localhost:5173`).
   При работе через один nginx CORS не нужен вовсе; оставляем настройку только для
   локальной разработки (`localhost:3000`).
4. **Кука.** Проверить флаги `Secure`/`SameSite` в `CookieUtils`: с `Secure` по http
   авторизация молча ломается. Отсюда — обязательный HTTPS (ниже).
5. **`brand_profile jsonb`** в business-service: колонка, поле в сущности, в `ProjectRequest`
   и `ProjectResponse`.

## Инфраструктура

Один `ops/docker-compose.stack.yml` собирает всё из исходников: postgres 16, rabbitmq
(с `definitions.json`), minio, пять сервисов, фронт (Next standalone), nginx.
На хосте нужен только Docker Engine + compose plugin.

**Публикация наружу.** Изначальный план (A-запись `app.ucust.online` на IP сервера +
Let's Encrypt по HTTP-01) неприменим: сервер за NAT без публичного IP, а валидатор
Let's Encrypt не пройдёт ни NAT, ни белый список. Вместо этого:

- **Разработка и отладка — SSH-туннель:** `ssh -L 8080:localhost:80 -p 40298 user@195.208.16.1`,
  платформа открывается на `http://localhost:8080`. Сертификаты и пробросы не нужны;
  origin остаётся единым, поэтому кука работает.
- **Показ снаружи — Cloudflare Tunnel:** `cloudflared` держит исходящее соединение с сервера
  и публикует `app.ucust.online` по HTTPS с автоматическим сертификатом. NAT и белый список
  не мешают, так как соединение инициируется изнутри. Требует перевода DNS домена на Cloudflare.
- Запасной путь — запросить у провайдера проброс 80/443; сроки непредсказуемы.

Пока работаем через туннель, кука ставится без флага `Secure` (профиль `dev`); при публикации
через Cloudflare включается `Secure` — это разные значения одной переменной окружения,
а не разный код.

**Почта.** `smtp.yandex.ru:587` (STARTTLS), `ucust@yandex.ru`, пароль-приложения — в `ops/.env`.
Для e2e-тестов профиль compose поднимает **Mailpit** вместо Яндекса, иначе тест зависит
от чтения реальной почты.

**Доступ.** Белый список провайдера пропускает один IP (`185.14.4.36`). При работе через
SSH-туннель это ограничение действует; Cloudflare Tunnel его обходит, так как соединение
исходящее.

**Docker.** На хосте не установлен и репозиторий `docker-ce` не подключён — фаза 2
начинается с добавления официального репозитория Docker и установки Engine + compose plugin.
`sudo` требует пароль, поэтому команды установки идут через `sudo -S`.

## Слой интеграции на фронте

```
frontend/lib/api/       client.ts (fetch + credentials, авто-refresh на 401),
                        auth.ts, users.ts, projects.ts, errors.ts, types.ts
frontend/lib/session/   SessionProvider.tsx — access в памяти, bootstrap
                        через /auth/refresh, useSession()
```

`NEXT_PUBLIC_API_BASE_URL` пустой → поведение ровно как сейчас (моки, витрина на Vercel не
ломается). Переменная задана → авторизация, профиль и проект идут на сервер.

Access-токен живёт **только в памяти**: в localStorage его класть нельзя, иначе XSS уносит
сессию. Refresh — в httpOnly-куке, недоступной JS. Параллельные 401 сходятся в один запрос
обновления через общую очередь, иначе гонка выбьет пользователя.

Сейчас формы бутафорские: `handleSubmit` делает `router.push`, состояний загрузки и ошибок
нет — их нужно добавить на всех auth-экранах.

## Фазы

| Фаза | Содержание | Критерий готовности |
|---|---|---|
| 0 | Каркас монорепо, перенос бэка и ТЗ, README, git init | структура на диске, витрина закоммичена и склонирована |
| 1 | Правки бэка: компиляция, gateway, CORS, кука | `docker compose build` проходит |
| 2 | Сервер: Docker, стек, nginx, `.env`, SSH-туннель | `GET /api/v0/status/hello` отвечает через туннель |
| 3 | `lib/api` + `lib/session`, флаг режима | mock↔real переключается одной переменной |
| 4 | Auth-экраны на живой бэк, guard дашборда | аккаунт заводится и подтверждается письмом |
| 5 | Профиль, аватар, онбординг → `POST /projects`, `brand_profile` | профиль переживает перезагрузку вкладки |
| 6 | Фронт в Docker за тем же nginx, e2e Playwright | сквозной сценарий зелёный |

## Риски

- **Ветка develop не собирается** — до фазы 1 неизвестно, один ли это дефект или их больше.
  Фаза 1 может разрастись; это первый кандидат на пересмотр сроков.
- **Java 25 + Spring Boot 4 + Spring Cloud 2025.1.1** — свежий стек, alpine-образы
  `eclipse-temurin:25-*` нужно проверить на существование, иначе переходим на не-alpine.
- **NAT и белый список** — публичного IP нет, поэтому любой внешний доступ идёт либо через
  SSH-туннель, либо через Cloudflare Tunnel. Если понадобится постоянный публичный адрес,
  тестовый контур придётся переносить на обычный VPS.
- **Стоимость сервера** — 25 ₽/час, ~18 000 ₽/мес при работе 24/7. Тестовый контур
  разумно гасить между сессиями; данные в PostgreSQL при этом должны переживать перезапуск
  (именованные тома, а не эфемерные).
- **Расхождение с репозиторием команды** — наш форк бэка уедет от их develop. Правки держим
  атомарными и документируем в `docs/backend-patches.md`.
- **Слияния фронта** — витрина активно правится; чем толще вставки в существующие экраны,
  тем больнее merge. Отсюда правило «весь новый код в новых файлах».

## Критерии приёмки

1. `C:\Claude\UCust-Platform` содержит фронт, бэк, ops и ТЗ; `git log` фронта сохранён.
2. `docker compose -f ops/docker-compose.stack.yml up -d` на сервере поднимает стек целиком.
3. Через SSH-туннель (`http://localhost:8080`) проходит сценарий: регистрация → письмо на
   реальную почту → подтверждение → вход → онбординг → проект сохранён в PostgreSQL и виден
   после перезагрузки страницы и после перезапуска стека. Публикация на `app.ucust.online`
   через Cloudflare Tunnel — отдельный шаг, выполняется под демонстрацию.
4. Витрина на Vercel продолжает работать на моках, её сборка не сломана.
5. e2e-сценарий Playwright проходит на тестовом профиле с Mailpit.
