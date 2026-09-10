# ─────────────────────────────────────────────────────────────
#  UCust · фронт. Docker-образ.
#
#  Многоступенчатая сборка по выводу Next.js standalone:
#  шаг зависимостей → шаг сборки → шаг-контейнер с сервером.
#
#  Сборка:
#    docker build \
#      --build-arg NEXT_PUBLIC_API_BASE_URL="https://api.ucust.n4d3sh1k4.site/api/v0" \
#      --tag ucust-front .
#
#  Запуск:
#    docker run -p 3000:3000 ucust-front
# ─────────────────────────────────────────────────────────────

# Бэкенд Next.js просит Node >=20.9 (package.json engines). 22 LTS — надёжно.
FROM node:22-alpine AS deps
WORKDIR /app

# .env* не копируем (в .dockerignore); для NEXT_PUBLIC_* используем build-arg —
# они подставляются в бандл на этапе next build и не нужны контейнеру в рантайме.
COPY package.json package-lock.json ./
RUN npm ci

FROM node:22-alpine AS builder
WORKDIR /app
ARG NEXT_PUBLIC_API_BASE_URL=/api/v0
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# standalone собирает server.js + traces; сборка без линта/тестов в образе —
# они тяжелее сетки и не нужны в проде.
RUN npm run build

FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

# Не root: головному процессу сервера контейнера права не нужны.
RUN addgroup --system --gid 1001 nodejs \
  && adduser --system --uid 1001 nextjs

# standalone-сервер Next.js вместе с traces (кэш Next может копировать из builder).
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
# Public-ассеты + собранный статический контент копируем вручную —
# standalone их не включает, а server.js отдаёт их сам (документация output).
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000

CMD ["node", "server.js"]