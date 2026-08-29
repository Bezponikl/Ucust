# Эндпоинты бэка и функции фронта

Источник правды — `docs/api/api-endpoints-public.json` (контракт v0, отдан бэком).
Пути собраны в одном месте: `lib/api/endpoints.ts`. Транспорт (заголовки, куки,
обновление токена на 401) — `lib/api/client.ts`. DTO — `lib/api/types.ts`.

Тест `lib/api/__tests__/endpoints.test.ts` читает контракт и падает, если реестр
разошёлся с ним в любую сторону: пропущенный путь или выдуманный лишний.

## Адреса

| Переменная | Значение | Когда |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | `/api/v0` | фронт и API за одним nginx |
| | `http://localhost:8100/api/v0` | шлюз поднят рядом |
| | `https://api.ucust.n4d3sh1k4.site/api/v0` | тестовый контур |

При разных доменах фронта и API (например, локальный фронт против тестового
контура) браузер отдаст refresh-куку, только если шлюз ставит её как
`SameSite=None; Secure` и отвечает `Access-Control-Allow-Credentials: true`
с конкретным origin фронта. Иначе вход проходит, а сессия не восстанавливается.

## Авторизация (security-service)

| Метод | Путь | Функция фронта | Токен |
|---|---|---|---|
| POST | `/auth/register` | `register()` | — |
| GET | `/auth/confirm-email?token` | `confirmEmail()` | — |
| POST | `/auth/resend-confirmation?email` | `resendConfirmation()` | — |
| POST | `/auth/login` | `login()` | — |
| POST | `/auth/refresh` | `refresh()` | кука |
| POST | `/auth/logout` | `logout()` | Bearer |
| POST | `/auth/forgot-password` | `forgotPassword()` | — |
| POST | `/auth/reset-password` | `resetPassword()` | — |
| POST | `/auth/yandex-mobile` | `loginWithYandexToken()` | — |
| POST | `/auth/link-social` | `linkSocial()` | — |
| POST | `/auth/change-email/verify-password` | `changeEmailVerifyPassword()` | Bearer |
| POST | `/auth/change-email/set-new-email` | `changeEmailSetNewEmail()` | — |
| POST | `/auth/change-email/confirm` | `changeEmailConfirm()` | — |

Все — `lib/api/auth.ts`. Вход через соцсеть в вебе начинается с `authorizeUrl()`
(`lib/api/oauth.ts`): это переход браузера, а не fetch.

## Статус (security-service)

| Метод | Путь | Функция | Файл |
|---|---|---|---|
| GET | `/status/hello` | `hello()` | `lib/api/status.ts` |
| GET | `/status/me` | `whoAmI()` | `lib/api/status.ts` |

## Профиль (user-service)

| Метод | Путь | Функция | Файл |
|---|---|---|---|
| GET | `/user/me` | `getMe()` | `lib/api/users.ts` |
| PATCH | `/user/me` | `updateMe()` | `lib/api/users.ts` |
| POST | `/user/me/avatar` | `uploadAvatar()` | `lib/api/users.ts` |

`uploadAvatar` — единственный метод профиля, завёрнутый в `ApiResponse`:
адрес картинки лежит в поле `data`.

## Проекты (business-service)

| Метод | Путь | Функция | Файл |
|---|---|---|---|
| POST | `/projects` | `createProject()` | `lib/api/projects.ts` |
| GET | `/projects` | `listProjects()` | `lib/api/projects.ts` |
| GET | `/projects/{id}` | `getProject()` | `lib/api/projects.ts` |
| PATCH | `/projects/{id}` | `updateProject()` | `lib/api/projects.ts` |
| DELETE | `/projects/{id}` | `deleteProject()` | `lib/api/projects.ts` |
| POST | `/projects/{id}/logo` | `uploadLogo()` | `lib/api/projects.ts` |

Профиль бренда из онбординга превращается в `ProjectRequest` через
`lib/api/mapProfile.ts`.

## Тарифы и квоты (billing-service)

| Метод | Путь | Функция | Файл |
|---|---|---|---|
| GET | `/tariffs` | `listTariffs()` | `lib/api/tariffs.ts` |
| GET | `/tariffs/{id}` | `getTariff()` | `lib/api/tariffs.ts` |
| GET | `/quota/me?feature` | `getMyQuota()` | `lib/api/quota.ts` |
| GET | `/quota/me/tariff` | `getMySubscription()` | `lib/api/quota.ts` |
| POST | `/quota/me/purchase` | `purchaseTariff()` | `lib/api/quota.ts` |

Тарифы публичные — их можно тянуть с лендинга без входа. `getMySubscription()`
отвечает 404, когда подписки нет: это штатный случай, а не сбой.

## Генерация (generative-orchestration-service)

| Метод | Путь | Функция | Файл |
|---|---|---|---|
| POST | `/orchestration/generate/async` | `generateAsync()` | `lib/api/orchestration.ts` |
| GET | `/orchestration/tasks/{taskId}` | `getTaskStatus()`, `pollTask()` | `lib/api/orchestration.ts` |
| GET | `/orchestration/posts/{id}` | `getPost()` | `lib/api/orchestration.ts` |
| POST | `/orchestration/posts/{id}/confirm` | `confirmPost()` | `lib/api/orchestration.ts` |
| POST | `/orchestration/posts/{id}/publish` | `publishPost()` | `lib/api/orchestration.ts` |
| GET | `/orchestration/projects/{projectId}/posts` | `listProjectPosts()` | `lib/api/orchestration.ts` |

Генерация асинхронная: `generateAsync` отвечает `202` и отдаёт только `taskId`,
дальше состояние забирается опросом. `pollTask` требует явный признак готовности —
набор значений `status` в контракте не раскрыт, и гадать за бэк здесь нельзя.

## Где эндпоинт вызывается в интерфейсе

Каждый путь контракта имеет точку входа в UI — от неё и стоит начинать отладку.

| Эндпоинт | Экран |
|---|---|
| `POST /auth/register` | `app/signup/page.tsx` |
| `GET /auth/confirm-email` | `app/signup/confirm/page.tsx` — переход по ссылке из письма |
| `POST /auth/resend-confirmation` | `app/signup/verify-email/page.tsx` |
| `POST /auth/login` | `app/login/page.tsx` через `SessionProvider` |
| `POST /auth/refresh` | `SessionProvider` при загрузке + `client.ts` на 401 |
| `POST /auth/logout` | `components/dashboard/ProfileMenu.tsx` |
| `POST /auth/forgot-password` | `app/forgot-password/page.tsx` |
| `POST /auth/reset-password` | `app/forgot-password/reset/page.tsx` |
| `POST /auth/link-social` | `app/login/page.tsx` — возврат из Яндекса с `email_exists_link_required` |
| `POST /auth/yandex-mobile` | `app/oauth-callback/page.tsx` — ветка `?yandexToken=` для мобильной обёртки |
| `POST /auth/change-email/*` (3 шага) | `components/dashboard/account/ChangeEmailModal.tsx` |
| `GET /status/hello`, `/status/me` | `components/dashboard/support/SupportSettings.tsx` — «Связь с сервером» |
| `GET /user/me`, `PATCH /user/me` | `SessionProvider`, `AccountSettings` |
| `POST /user/me/avatar` | `AccountSettings` — загрузка аватара |
| `GET /projects` | `lib/dashboard/source.ts` → `DashboardProvider` |
| `POST /projects` | `components/onboarding/review/ReviewFlow.tsx` |
| `GET /projects/{id}`, `PATCH`, `DELETE` | `components/dashboard/business/BusinessSettings.tsx` |
| `POST /projects/{id}/logo` | `BusinessSettings` — загрузка логотипа |
| `GET /tariffs`, `GET /tariffs/{id}` | `SubscriptionSettings` — витрина и подтверждение покупки |
| `GET /quota/me`, `/quota/me/tariff` | `SubscriptionSettings` — остаток генераций и текущая подписка |
| `POST /quota/me/purchase` | `SubscriptionSettings` — модалка подтверждения |
| `POST /orchestration/generate/async` | `components/dashboard/create/CreateView.tsx` |
| `GET /orchestration/tasks/{taskId}` | `CreateView` через `pollTask` |
| `GET /orchestration/projects/{id}/posts` | `components/dashboard/content/ContentView.tsx` |
| `GET /orchestration/posts/{id}` | `components/dashboard/content/RemotePostEditView.tsx` |
| `POST /orchestration/posts/{id}/confirm` | `CreateView` (перед отправкой), `PostEditView` |
| `POST /orchestration/posts/{id}/publish` | `CreateView` («опубликовать сейчас»), `PostEditView` |

Общее правило деградации: если сервис не отвечает, экран не ломается — контент-план
и тарифы показывают демо-данные витрины, генерация собирает черновик локально и
честно сообщает об этом тостом. Так демо остаётся показуемым, пока бэк поднимает
недостающие сервисы.

## Сверка с живым контуром (13.08.2026)

Проверено запросами к `https://api.ucust.n4d3sh1k4.site`:

| Путь | Ответ | Что значит |
|---|---|---|
| `POST /api/v0/auth/login` | 400 на пустом теле | сервис авторизации на месте |
| `GET /api/v0/status/hello`, `/user/me`, `/projects` | 401 | маршруты есть, ждут токен |
| `GET /api/v0/tariffs`, `/quota/me` | 404 | billing-service не отвечает через шлюз |
| `GET /api/v0/orchestration/tasks/{id}` | 404 | генерация не отвечает через шлюз |
| `GET /api/v0/oauth2/authorization/yandex` | 302 на `oauth.yandex.ru` | цепочка живёт **под** `/api/v0` |
| `GET /oauth2/authorization/yandex` | 404 | путь из `publicRoutes` контракта не работает |

Два вывода. Первый: контракт перечисляет OAuth2 как `/oauth2/**` и
`/login/oauth2/**`, но шлюз обслуживает цепочку под префиксом версии —
`authorizeUrl()` строится от `API_BASE_URL`, менять на «origin без префикса»
нельзя, вход сломается. Второй: тарифы, квоты и генерация на контуре пока
не подняты — код фронта под них написан, но проверять его можно будет
только после того, как бэк выведет эти сервисы через шлюз.

## Что в контракте не расшифровано

Формы `TariffResponse`, `CheckQuotaResponse`, `SubscriptionOverview`,
`TaskStatusResponse`, `PostResponse` названы, но не расписаны по полям, как и
значения `GenerationMode`. В `types.ts` они описаны известными полями плюс
открытая индексная подпись — фронт не выдумывает поля и не падает на лишних.
Когда бэк даст расшифровку, подписи убираются, поля дописываются.
