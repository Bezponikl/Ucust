This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## API и переменные окружения

Перед первым запуском нужен `.env.local` — скопировать из шаблона и подставить адрес шлюза:

```bash
cp .env.example .env.local
```

Переменная всего одна — `NEXT_PUBLIC_API_BASE_URL`, адрес шлюза вместе с префиксом контракта `/api/v0`:

| Значение | Когда |
| --- | --- |
| `/api/v0` | фронт и API за одним nginx |
| `http://localhost:8100/api/v0` | фронт локально, шлюз рядом |
| `https://api.ucust.n4d3sh1k4.site/api/v0` | тестовый контур на сервере |

Слой работы с бэком целиком лежит в `lib/api/`:

- `config.ts` — читает переменную окружения, единственное место с базовым адресом;
- `endpoints.ts` — реестр всех путей контракта v0, больше нигде путей нет;
- `client.ts` — `apiFetch`: Bearer-заголовок, повтор запроса после `/auth/refresh` на 401, разворачивание обёртки `ApiResponse`;
- `errors.ts` — `ApiError` и перевод кодов бэка в текст для пользователя;
- `auth.ts`, `users.ts`, `projects.ts`, `tariffs.ts`, `quota.ts`, `orchestration.ts`, `status.ts`, `oauth.ts` — вызовы по сервисам;
- `map*.ts` — перекладывание DTO бэка в модели экранов;
- `types.ts` — DTO контракта.

Access-токен живёт только в памяти вкладки, refresh — в httpOnly-куке шлюза; поэтому все запросы идут с `credentials: "include"`, а сессия восстанавливается запросом `/auth/refresh` (`lib/session/SessionProvider.tsx`).

Исходный контракт бэка — `docs/api/api-endpoints-public.json`, его человекочитаемый разбор — `docs/api/endpoints.md`.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
