# UCust Platform: монорепо и реальная авторизация — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Свести фронт и бэк UCust в монорепо `C:\Claude\UCust-Platform`, поднять весь стек на арендованном сервере и перевести авторизацию, профиль и бизнес-проект с моков на настоящий API.

**Architecture:** Next.js-фронт и пять Spring Boot-сервисов работают за одним nginx — единый origin, поэтому httpOnly-кука `refreshToken` живёт без CORS. Access-токен хранится только в памяти вкладки и продлевается через `/auth/refresh`. Переключение mock↔real — одна переменная `NEXT_PUBLIC_API_BASE_URL`, поэтому витрина на Vercel продолжает работать на моках.

**Tech Stack:** Next.js 16 / React 19 / TypeScript / Tailwind 4; Spring Boot 4.0.4 / Java 25 / Gradle; PostgreSQL 16, RabbitMQ 3, MinIO; Docker Engine + compose plugin; nginx; Vitest (юнит), Playwright (e2e).

## Global Constraints

- Монорепо: `C:\Claude\UCust-Platform`; фронт — `frontend/`, бэк — `backend/`, инфраструктура — `ops/`, документы — `docs/`.
- `frontend/` — клон `C:\Claude\UCust` с remote `showcase`; работа идёт в ветке `platform`. Витрина ведущая по UI.
- Весь интеграционный код фронта — **в новых файлах** (`lib/api/*`, `lib/session/*`). В существующие компоненты допускаются вставки не более 3 строк подряд.
- Префикс API — `/api/v0`. Единственный источник маршрутов — `ApiGatewayApplication.customRouteLocator`.
- Секреты только в `ops/.env` (в `.gitignore`); в репозиторий уходит `ops/.env.example` с пустыми значениями.
- Сервер: `ssh -i ~/.ssh/ucust_gpu -p 40298 user@195.208.16.1`, Ubuntu 22.04.5, за NAT, `sudo` требует пароль (`sudo -S`).
- Почта: `smtp.yandex.ru:587`, `ucust@yandex.ru`, пароль-приложения из `ops/.env`.
- Реальными становятся только auth, профиль и проект. Контент, промо, отзывы, входящие, аналитика, подписка и ИИ остаются моками — их код не трогать.
- Коммиты атомарные; правки бэка — отдельными коммитами с префиксом `backend:`, чтобы их можно было отдать команде PR-ом.

## File Structure

**Создаётся в монорепо:**

| Файл | Ответственность |
|---|---|
| `ops/docker-compose.stack.yml` | весь стек: инфраструктура + 5 сервисов + nginx + фронт |
| `ops/.env.example` | список переменных без значений |
| `ops/nginx/default.conf` | `/` → фронт, `/api/` → gateway |
| `ops/postgres/init.sql` | три базы |
| `ops/deploy.sh` | rsync исходников на сервер + пересборка |
| `docs/api-contract.md` | контракт `/api/v0` — источник правды для фронта |
| `docs/backend-patches.md` | журнал правок бэка для передачи команде |

**Создаётся во фронте (`frontend/`):**

| Файл | Ответственность |
|---|---|
| `lib/api/config.ts` | базовый URL и флаг режима (mock/real) |
| `lib/api/errors.ts` | `ApiError`, разбор ответа бэка в человеческий текст |
| `lib/api/client.ts` | fetch-обёртка: заголовки, куки, единая очередь refresh на 401 |
| `lib/api/auth.ts` | register / login / logout / refresh / confirm / forgot / reset |
| `lib/api/users.ts` | `getMe`, `updateMe`, `uploadAvatar` |
| `lib/api/projects.ts` | `listProjects`, `createProject`, `updateProject`, `uploadLogo` |
| `lib/api/types.ts` | типы DTO бэка один-в-один |
| `lib/api/mapProfile.ts` | `BrandProfile` + `WizardInput` → `ProjectRequest` |
| `lib/session/SessionProvider.tsx` | контекст сессии: access в памяти, bootstrap, logout |
| `frontend/Dockerfile` | standalone-сборка Next |
| `frontend/vitest.config.ts` | юнит-тесты |

---

## Фаза 0. Монорепо

### Task 1: Каркас монорепо

**Files:**
- Create: `C:\Claude\UCust-Platform\README.md`, `.gitignore`
- Create: `C:\Claude\UCust-Platform\backend\**` (перенос из архива develop)
- Create: `C:\Claude\UCust-Platform\docs\ts\**` (перенос ТЗ из архива main)
- Create: `C:\Claude\UCust-Platform\ops\**` (перенос `ucust-ops` из архива develop)
- Clone: `C:\Claude\UCust-Platform\frontend` (из `C:\Claude\UCust`)

**Interfaces:**
- Produces: структура каталогов, на которую опираются все последующие задачи; ветка `platform` во `frontend/`.

- [ ] **Step 1: Создать каталог и склонировать фронт**

```powershell
New-Item -ItemType Directory -Force C:\Claude\UCust-Platform | Out-Null
git clone C:\Claude\UCust C:\Claude\UCust-Platform\frontend
cd C:\Claude\UCust-Platform\frontend
git remote rename origin showcase
git checkout -b platform
```

- [ ] **Step 2: Проверить, что история фронта на месте**

Run: `git -C C:\Claude\UCust-Platform\frontend log --oneline -3`
Expected: последний коммит — `feat(dashboard): promo editor, guided tour, project guard and onboarding polish`

- [ ] **Step 3: Перенести бэк, ops и ТЗ**

Источник — распакованные архивы. Если их нет, распаковать заново:

```powershell
$tmp = "$env:LOCALAPPDATA\Temp\ucust-zips"
Expand-Archive "C:\Users\Ант\Downloads\Ucust-develop.zip" "$tmp\develop" -Force
Expand-Archive "C:\Users\Ант\Downloads\Ucust-main.zip" "$tmp\main" -Force
$dev = "$tmp\develop\Ucust-develop\src\N4d3sh1k4-UCust_Dev"

Copy-Item $dev "C:\Claude\UCust-Platform\backend" -Recurse
Remove-Item "C:\Claude\UCust-Platform\backend\ucust-ops" -Recurse -Force
Remove-Item "C:\Claude\UCust-Platform\backend\.gitmodules" -Force
Copy-Item "$dev\ucust-ops\*" "C:\Claude\UCust-Platform\ops" -Recurse -Force
New-Item -ItemType Directory -Force "C:\Claude\UCust-Platform\docs\ts" | Out-Null
Copy-Item "$tmp\main\Ucust-main\*.md" "C:\Claude\UCust-Platform\docs\ts\"
```

Каждый сервис в архиве был git-submodule — вложенные `.git` каталоги надо удалить, иначе git примет их за подмодули:

```powershell
Get-ChildItem "C:\Claude\UCust-Platform\backend" -Recurse -Force -Directory -Filter ".git" |
  Remove-Item -Recurse -Force
```

- [ ] **Step 4: Написать `.gitignore`**

```gitignore
# зависимости и сборка
node_modules/
.next/
build/
.gradle/
out/

# секреты
ops/.env
frontend/.env.local

# служебное
*.log
.DS_Store
```

- [ ] **Step 5: Написать `README.md`**

```markdown
# UCust Platform

Монорепо платформы: фронт (Next.js), бэк (Spring Boot, 5 сервисов), инфраструктура.

## Структура

- `frontend/` — Next.js. Клон витрины `C:\Claude\UCust` (remote `showcase`), ветка `platform`.
  UI разрабатывается в витрине и вливается сюда: `git fetch showcase && git merge showcase/main`.
- `backend/` — Spring Boot 4 / Java 25, Gradle. Форк ветки develop команды.
- `ops/` — docker compose, nginx, init.sql, определения RabbitMQ.
- `docs/` — контракт API, ТЗ, спеки и планы.

## Запуск тестового контура

Стек живёт на арендованном сервере (см. `docs/superpowers/specs/`):

    ssh -i ~/.ssh/ucust_gpu -p 40298 user@195.208.16.1
    cd ~/ucust && docker compose -f ops/docker-compose.stack.yml up -d

Сервер за NAT, поэтому доступ с локальной машины — через туннель:

    ssh -i ~/.ssh/ucust_gpu -p 40298 -L 8080:localhost:80 user@195.208.16.1

Платформа открывается на http://localhost:8080

## Режимы фронта

Без `NEXT_PUBLIC_API_BASE_URL` фронт работает на моках (режим витрины).
С переменной — авторизация, профиль и проект идут на настоящий бэк.
```

- [ ] **Step 6: Инициализировать git и закоммитить**

```powershell
cd C:\Claude\UCust-Platform
git init -b main
git add -A
git commit -m "chore: monorepo skeleton — backend, ops, docs, frontend clone"
```

Замечание: `frontend/` содержит собственный `.git`, поэтому в индекс корневого репозитория он не попадёт. Это ожидаемо — фронт остаётся отдельным репозиторием со своей историей, монорепо версионирует бэк, ops и docs.

- [ ] **Step 7: Проверить структуру**

Run: `Get-ChildItem C:\Claude\UCust-Platform; Get-ChildItem C:\Claude\UCust-Platform\backend`
Expected: в корне `frontend, backend, ops, docs, README.md`; в backend — семь модулей и `settings.gradle`

---

## Фаза 1. Сервер и сборка бэка

### Task 2: Docker на сервере

**Files:**
- Create: `ops/server-bootstrap.sh`

**Interfaces:**
- Produces: рабочий `docker` и `docker compose` на сервере; каталог `~/ucust` для исходников.

- [ ] **Step 1: Написать `ops/server-bootstrap.sh`**

```bash
#!/usr/bin/env bash
# Ставит Docker Engine на чистую Ubuntu 22.04 и готовит каталог проекта.
# Пароль sudo передаётся через переменную SUDO_PASS.
set -euo pipefail

S() { echo "$SUDO_PASS" | sudo -S "$@"; }

S apt-get update -qq
S apt-get install -y ca-certificates curl gnupg

S install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg |
  S gpg --batch --yes --dearmor -o /etc/apt/keyrings/docker.gpg
S chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" |
  S tee /etc/apt/sources.list.d/docker.list > /dev/null

S apt-get update -qq
S apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
S usermod -aG docker "$USER"

mkdir -p ~/ucust
echo "OK: $(S docker --version), $(S docker compose version)"
```

- [ ] **Step 2: Выполнить на сервере**

```powershell
$ssh = 'ssh -i "$env:USERPROFILE\.ssh\ucust_gpu" -p 40298 user@195.208.16.1'
scp -i "$env:USERPROFILE\.ssh\ucust_gpu" -P 40298 C:\Claude\UCust-Platform\ops\server-bootstrap.sh user@195.208.16.1:~/
ssh -i "$env:USERPROFILE\.ssh\ucust_gpu" -p 40298 user@195.208.16.1 "SUDO_PASS='2F5PU51c' bash ~/server-bootstrap.sh"
```

- [ ] **Step 3: Проверить, что docker работает без sudo**

Run: `ssh -i "$env:USERPROFILE\.ssh\ucust_gpu" -p 40298 user@195.208.16.1 "docker run --rm hello-world | tail -3"`
Expected: строка `This message shows that your installation appears to be working correctly.`
Если ошибка `permission denied` — членство в группе `docker` ещё не подхвачено; переподключиться по SSH.

- [ ] **Step 4: Коммит**

```powershell
cd C:\Claude\UCust-Platform
git add ops/server-bootstrap.sh
git commit -m "ops: docker bootstrap script for Ubuntu 22.04"
```

---

### Task 3: Скрипт синхронизации исходников на сервер

**Files:**
- Create: `ops/deploy.sh`

**Interfaces:**
- Consumes: каталог `~/ucust` из Task 2.
- Produces: команда `bash ops/deploy.sh`, копирующая монорепо на сервер. Все последующие задачи используют её после правок бэка.

- [ ] **Step 1: Написать `ops/deploy.sh`**

```bash
#!/usr/bin/env bash
# Копирует backend/ и ops/ на сервер и пересобирает стек.
# Запускать из корня монорепо: bash ops/deploy.sh [сервис ...]
set -euo pipefail

SSH_KEY="${SSH_KEY:-$HOME/.ssh/ucust_gpu}"
REMOTE="user@195.208.16.1"
PORT=40298
DEST="~/ucust"

rsync -az --delete \
  -e "ssh -i $SSH_KEY -p $PORT" \
  --exclude '.gradle' --exclude 'build' --exclude 'node_modules' --exclude '.next' \
  backend ops "$REMOTE:$DEST/"

ssh -i "$SSH_KEY" -p "$PORT" "$REMOTE" \
  "cd $DEST && docker compose -f ops/docker-compose.stack.yml build $* && \
   docker compose -f ops/docker-compose.stack.yml up -d $*"
```

- [ ] **Step 2: Проверить наличие rsync в Git Bash**

Run: `bash -lc "rsync --version | head -1"`
Expected: строка вида `rsync  version 3.x`.
Если rsync отсутствует, заменить его в скрипте на `scp -r` — но сначала попробовать rsync, он на порядок быстрее при повторных прогонах.

- [ ] **Step 3: Коммит**

```powershell
git add ops/deploy.sh
git commit -m "ops: rsync-based deploy script"
```

---

### Task 4: Починить компиляцию бэка

**Files:**
- Modify: `backend/security-service/src/main/java/com/n4d3sh1k4/security_service/controller/AuthController.java`
- Create: `docs/backend-patches.md`

**Interfaces:**
- Produces: собирающийся `security-service`; журнал правок для передачи команде.

- [ ] **Step 1: Убедиться, что сборка падает**

```bash
ssh -i ~/.ssh/ucust_gpu -p 40298 user@195.208.16.1 \
  "cd ~/ucust/backend/security-service && docker run --rm -v \$PWD:/app -v ~/ucust/backend/common:/common -w /app eclipse-temurin:25-jdk ./gradlew compileJava --no-daemon 2>&1 | tail -30"
```

Expected: ошибка `cannot find symbol: variable yandexAuthService` в `AuthController`.
Записать полный список ошибок — их может быть больше одной.

- [ ] **Step 2: Исправить `AuthController`**

Поле не объявлено и не внедряется, а конструктор принимает восемь неиспользуемых зависимостей. Привести класс к явному виду: оставить только то, что действительно используется, и добавить `YandexAuthService`, если такой сервис существует в `service/`. Проверить:

```bash
ssh -i ~/.ssh/ucust_gpu -p 40298 user@195.208.16.1 \
  "ls ~/ucust/backend/security-service/src/main/java/com/n4d3sh1k4/security_service/service/"
```

Если `YandexAuthService` в списке есть — объявить поле и внедрить через конструктор:

```java
private final AuthenticationManager authenticationManager;
private final AuthService authService;
private final YandexAuthService yandexAuthService;

public AuthController(AuthenticationManager authenticationManager,
                      AuthService authService,
                      YandexAuthService yandexAuthService) {
    this.authenticationManager = authenticationManager;
    this.authService = authService;
    this.yandexAuthService = yandexAuthService;
}
```

Если сервиса нет — удалить эндпоинты `/yandex-mobile` и `/link-social` целиком (OAuth Яндекса в объём этого плана не входит) и зафиксировать это в журнале правок.

- [ ] **Step 3: Пересобрать и убедиться, что компиляция проходит**

```bash
bash ops/deploy.sh   # синхронизация
ssh -i ~/.ssh/ucust_gpu -p 40298 user@195.208.16.1 \
  "cd ~/ucust/backend/security-service && docker run --rm -v \$PWD:/app -w /app eclipse-temurin:25-jdk ./gradlew compileJava --no-daemon 2>&1 | tail -5"
```

Expected: `BUILD SUCCESSFUL`

- [ ] **Step 4: Завести журнал правок**

`docs/backend-patches.md`:

```markdown
# Правки бэка относительно ветки develop

Каждая правка — отдельный коммит с префиксом `backend:`, чтобы её можно было
отдать команде PR-ом.

| # | Файл | Суть | Причина |
|---|---|---|---|
| 1 | `security-service/.../AuthController.java` | восстановлено внедрение `YandexAuthService` | класс не компилировался: поле использовалось, но не было объявлено |
```

- [ ] **Step 5: Коммит**

```bash
git add backend/security-service docs/backend-patches.md
git commit -m "backend: fix AuthController compilation, start patch journal"
```

---

### Task 5: Привести маршруты, куку и ссылки писем в рабочее состояние

**Files:**
- Modify: `backend/api-gateway/src/main/resources/application.yml` (удалить устаревшие маршруты)
- Modify: `backend/api-gateway/src/main/java/com/n4d3sh1k4/api_gateway/ApiGatewayApplication.java`
- Modify: `backend/api-gateway/src/main/java/com/n4d3sh1k4/api_gateway/SecurityConfig.java`
- Modify: `backend/security-service/src/main/java/com/n4d3sh1k4/security_service/utils/CookieUtils.java`
- Modify: `backend/security-service/src/main/resources/application.yml`
- Modify: `backend/notification-service` — шаблонные ссылки писем
- Modify: `docs/backend-patches.md`

**Interfaces:**
- Produces: маршруты `/api/v0/**`, ведущие на `http://<сервис>:<порт>`; кука `refreshToken` с настраиваемым `SameSite`; ссылки в письмах, ведущие на реальный адрес фронта.

- [ ] **Step 1: Заменить `lb://` на прямые адреса**

В `ApiGatewayApplication.customRouteLocator` четыре вызова `.uri("lb://...")`. Spring Cloud LoadBalancer требует service discovery, которого в стеке нет, — заменить:

```java
.uri("http://security-service:8101")   // было lb://security-service
.uri("http://user-service:8102")       // было lb://user-service
.uri("http://business-service:8104")   // было lb://business-service
```

- [ ] **Step 2: Удалить устаревшие маршруты из `application.yml`**

Убрать весь блок `spring.cloud.gateway.routes` (маршруты `/api/auth/**`, `/api/users/**`, `/api/business/**`) — он конфликтует с `customRouteLocator`. Оставить `server.port`, `spring.application.name`, `servlet.multipart`, `codec`, `jwt`, `management`, `logging`.

- [ ] **Step 3: Согласовать путь подтверждения почты**

Письмо ведёт на `/api/v0/auth/confirm`, gateway публикует `/api/v0/auth/confirm`, а контроллер отдаёт `/auth/confirm-email` — после `stripPrefix(2)` получается 404. Привести к одному имени: в `AuthController` заменить

```java
@GetMapping("/confirm-email")
```

на

```java
@GetMapping("/confirm")
```

и в gateway убедиться, что в списке public-маршрутов присутствует `API_PREFIX + "/auth/confirm"` (он уже есть).

- [ ] **Step 4: Вынести адрес фронта из шаблонов писем**

Файл `backend/notification-service/src/main/java/com/n4d3sh1k4/notification_service/service/EmailService.java`,
строки 28 и 38 — ссылки захардкожены как `http://localhost:8180/...`. Заменить на значение из конфигурации:

```java
@Value("${app.public-url}")
private String publicUrl;
...
context.setVariable("activationUrl", publicUrl + "/api/v0/auth/confirm?token=" + token);
context.setVariable("resetUrl", publicUrl + "/forgot-password/reset?token=" + token);
```

и в `notification-service/src/main/resources/application.yml`:

```yaml
app:
  public-url: ${APP_PUBLIC_URL:http://localhost:8080}
```

Путь `/forgot-password/reset` выбран потому, что именно такая страница существует во фронте.

- [ ] **Step 5: Сделать `SameSite` куки настраиваемым**

`CookieUtils` ставит `sameSite("None")` при `secure=false` — такую куку браузер отбрасывает молча. Заменить:

```java
@Value("${cookie.same-site:Lax}")
private String cookieSameSite;
...
.sameSite(cookieSameSite)
```

и в `security-service/src/main/resources/application.yml`:

```yaml
cookie:
  secure:
    state: ${COOKIE_SECURE:false}
  same-site: ${COOKIE_SAME_SITE:Lax}
```

При работе через один origin (nginx) `Lax` корректен. Для публикации через Cloudflare ставится `COOKIE_SECURE=true`.

- [ ] **Step 6: Сузить CORS**

В `SecurityConfig` заменить список origin'ов на:

```java
configuration.setAllowedOrigins(List.of("http://localhost:3000", "http://localhost:8080"));
```

Чужие домены (`ucust.n4d3sh1k4.site`, `adm.ucust.n4d3sh1k4.site`, `localhost:5173`) убрать: при работе через nginx CORS не нужен вовсе, а для локальной разработки фронта достаточно двух адресов.

- [ ] **Step 7: Дописать журнал правок и закоммитить**

Добавить в `docs/backend-patches.md` строки 2–6 (маршруты, дубли в yml, путь confirm, адрес писем, SameSite, CORS) с той же структурой, что и строка 1.

```bash
git add backend docs/backend-patches.md
git commit -m "backend: direct service URIs, single route source, configurable cookie and email URLs"
```

---

### Task 6: Стек в docker compose

**Files:**
- Create: `ops/docker-compose.stack.yml`
- Create: `ops/.env.example`
- Modify: `ops/postgres/init.sql` (перенесён из архива, проверить содержимое)

**Interfaces:**
- Consumes: собирающийся бэк из Task 4–5.
- Produces: поднятый стек; `http://localhost:8100/api/v0/...` внутри сервера.

- [ ] **Step 1: Написать `ops/.env.example`**

```env
# PostgreSQL
POSTGRES_USER=ucust
POSTGRES_PASSWORD=
# RabbitMQ
RABBITMQ_USER=service-user
RABBITMQ_PASS=
# MinIO
MINIO_ROOT_USER=
MINIO_ROOT_PASSWORD=
# JWT (base64)
JWT_SECRET_ACCESS=
# Почта
MAIL_HOST=smtp.yandex.ru
MAIL_PORT=587
MAIL_USERNAME=ucust@yandex.ru
MAIL_PASSWORD=
# Публичный адрес фронта — попадает в ссылки писем
APP_PUBLIC_URL=http://localhost:8080
# Кука
COOKIE_SECURE=false
COOKIE_SAME_SITE=Lax
```

- [ ] **Step 2: Создать `ops/.env` на сервере с настоящими значениями**

Файл не коммитится. Значения: пароли задать случайными (`openssl rand -base64 24`), `JWT_SECRET_ACCESS` — обязательно base64 (`openssl rand -base64 32`), `MAIL_PASSWORD` — пароль-приложения Яндекса.

```bash
ssh -i ~/.ssh/ucust_gpu -p 40298 user@195.208.16.1 'cat > ~/ucust/ops/.env' <<'EOF'
POSTGRES_USER=ucust
POSTGRES_PASSWORD=<сгенерировать>
RABBITMQ_USER=service-user
RABBITMQ_PASS=<сгенерировать>
MINIO_ROOT_USER=ucust
MINIO_ROOT_PASSWORD=<сгенерировать>
JWT_SECRET_ACCESS=<openssl rand -base64 32>
MAIL_HOST=smtp.yandex.ru
MAIL_PORT=587
MAIL_USERNAME=ucust@yandex.ru
MAIL_PASSWORD=mazhmvomqycptdod
APP_PUBLIC_URL=http://localhost:8080
COOKIE_SECURE=false
COOKIE_SAME_SITE=Lax
EOF
```

- [ ] **Step 3: Написать `ops/docker-compose.stack.yml`**

```yaml
name: ucust

x-service-env: &service-env
  SPRING_PROFILES_ACTIVE: prod
  DB_USER: ${POSTGRES_USER}
  DB_PASSWORD: ${POSTGRES_PASSWORD}
  RABBITMQ_USER: ${RABBITMQ_USER}
  RABBITMQ_PASS: ${RABBITMQ_PASS}
  JWT_SECRET_ACCESS: ${JWT_SECRET_ACCESS}

services:
  postgres-db:
    image: postgres:16
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 10

  rabbitmq:
    image: rabbitmq:3-management
    environment:
      RABBITMQ_DEFAULT_USER: ${RABBITMQ_USER}
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASS}
      RABBITMQ_DEFAULT_VHOST: universal-host
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "-q", "ping"]
      interval: 15s
      timeout: 10s
      retries: 10

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
    volumes:
      - minio_data:/data

  api-gateway:
    build:
      context: ../backend
      dockerfile: api-gateway/Dockerfile
    environment:
      <<: *service-env
    depends_on: [security-service, user-service, business-service]

  security-service:
    build:
      context: ../backend
      dockerfile: security-service/Dockerfile
    environment:
      <<: *service-env
      COOKIE_SECURE: ${COOKIE_SECURE}
      COOKIE_SAME_SITE: ${COOKIE_SAME_SITE}
    depends_on:
      postgres-db: {condition: service_healthy}
      rabbitmq: {condition: service_healthy}

  user-service:
    build:
      context: ../backend
      dockerfile: user-service/Dockerfile
    environment:
      <<: *service-env
    depends_on:
      postgres-db: {condition: service_healthy}
      rabbitmq: {condition: service_healthy}

  business-service:
    build:
      context: ../backend
      dockerfile: business-service/Dockerfile
    environment:
      <<: *service-env
    depends_on:
      postgres-db: {condition: service_healthy}

  notification-service:
    build:
      context: ../backend
      dockerfile: notification-service/Dockerfile
    environment:
      <<: *service-env
      MAIL_HOST: ${MAIL_HOST}
      MAIL_PORT: ${MAIL_PORT}
      MAIL_USERNAME: ${MAIL_USERNAME}
      MAIL_PASSWORD: ${MAIL_PASSWORD}
      APP_PUBLIC_URL: ${APP_PUBLIC_URL}
    depends_on:
      rabbitmq: {condition: service_healthy}

volumes:
  postgres_data:
  rabbitmq_data:
  minio_data:
```

Именованные тома обязательны: сервер почасовой и между сессиями гасится, данные должны переживать перезапуск.

`ops/rabbitmq/definitions.json` из архива не подключается: `RabbitMailConfig` в
notification-service объявляет `user-exchange`, очередь `mail-notification-queue` и все
привязки бинами, поэтому топология создаётся сама при старте. Достаточно, чтобы совпадали
пользователь и vhost.

- [ ] **Step 4: Согласовать учётные данные в prod-конфигах**

Хосты в `application-prod.yml` уже верные (`postgres-db:5432`, `rabbitmq`), но учётные данные
разъезжаются, и стек из-за этого не поднимется:

| Проблема | Где | Как чинить |
|---|---|---|
| Пользователь БД захардкожен `ETA_DBUser` | `security-service`, `user-service`, `business-service` | заменить на `${DB_USER}` |
| Два разных пользователя RabbitMQ: `rmuser/rmpassword` и `service-user/servicepassword` | `business-service` против остальных | привести все к `${RABBITMQ_USER}` / `${RABBITMQ_PASS}` |
| `business-service` не указывает `virtual-host`, остальные используют `universal-host` | `business-service` | добавить `virtual-host: universal-host` |
| Устаревшие маршруты `/api/auth/**` | `api-gateway/application-prod.yml` | удалить блок `routes` — так же, как в Step 2 |

После правок значение `POSTGRES_USER` в `ops/.env` может быть любым, лишь бы совпадало с `DB_USER`.
Проще всего оставить `ETA_DBUser`, чтобы не пересоздавать том с базой, если он уже создан.

- [ ] **Step 4b: Проверить, что переменные подставились**

```bash
bash ops/deploy.sh
ssh -i ~/.ssh/ucust_gpu -p 40298 user@195.208.16.1 \
  "cd ~/ucust && docker compose -f ops/docker-compose.stack.yml logs security-service | grep -iE 'HikariPool|Started SecurityService' | tail -5"
```

Expected: `HikariPool-1 - Start completed` и `Started SecurityServiceApplication`.
Ошибка `FATAL: password authentication failed` означает расхождение `DB_USER`/`POSTGRES_USER`.

- [ ] **Step 5: Собрать и поднять**

```bash
bash ops/deploy.sh
```

Expected: `docker compose ... up -d` завершается без ошибок.

- [ ] **Step 6: Проверить, что все контейнеры живы**

```bash
ssh -i ~/.ssh/ucust_gpu -p 40298 user@195.208.16.1 \
  "cd ~/ucust && docker compose -f ops/docker-compose.stack.yml ps"
```

Expected: шесть сервисов в состоянии `running`, инфраструктура — `healthy`.
При падении смотреть журнал конкретного сервиса: `docker compose -f ops/docker-compose.stack.yml logs --tail 50 security-service`

- [ ] **Step 7: Smoke-проверка регистрации прямо на сервере**

```bash
ssh -i ~/.ssh/ucust_gpu -p 40298 user@195.208.16.1 \
  "curl -s -o /dev/null -w '%{http_code}\n' -X POST http://localhost:8100/api/v0/auth/register \
   -H 'Content-Type: application/json' \
   -d '{\"firstName\":\"Тест\",\"lastName\":\"Тестов\",\"email\":\"test@example.com\",\"password\":\"Passw0rd!\",\"confirmPassword\":\"Passw0rd!\"}'"
```

Expected: `200`. Код `500` — смотреть логи security-service; `404` — маршруты gateway не подхватились.

- [ ] **Step 8: Коммит**

```bash
git add ops
git commit -m "ops: full stack compose with healthchecks and named volumes"
```

---

### Task 7: nginx и туннель

**Files:**
- Create: `ops/nginx/default.conf`
- Modify: `ops/docker-compose.stack.yml` (добавить nginx)

**Interfaces:**
- Produces: единая точка входа на порту 80 сервера; `http://localhost:8080` на локальной машине через SSH-туннель.

- [ ] **Step 1: Написать `ops/nginx/default.conf`**

```nginx
server {
    listen 80;
    server_name _;

    client_max_body_size 12M;   # аватарки и логотипы — до 10 МБ на стороне Spring

    location /api/ {
        proxy_pass http://api-gateway:8100;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://frontend:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

Блок `location /` пока ведёт в никуда — контейнер `frontend` появится в Task 17. До тех пор проверяем только `/api/`.

- [ ] **Step 2: Добавить nginx в compose**

```yaml
  nginx:
    image: nginx:1.27-alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on: [api-gateway]
```

- [ ] **Step 3: Применить и проверить изнутри сервера**

```bash
bash ops/deploy.sh
ssh -i ~/.ssh/ucust_gpu -p 40298 user@195.208.16.1 \
  "curl -s -o /dev/null -w '%{http_code}\n' http://localhost/api/v0/auth/login -X POST -H 'Content-Type: application/json' -d '{}'"
```

Expected: `400` или `401` — то есть запрос дошёл до security-service. `502` означает, что nginx не видит gateway.

- [ ] **Step 4: Поднять туннель и проверить с локальной машины**

```powershell
ssh -i "$env:USERPROFILE\.ssh\ucust_gpu" -p 40298 -L 8080:localhost:80 -N user@195.208.16.1
```

В другом окне:

Run: `curl.exe -s -o NUL -w "%{http_code}" -X POST http://localhost:8080/api/v0/auth/login -H "Content-Type: application/json" -d "{}"`
Expected: `400` или `401`

- [ ] **Step 5: Коммит**

```bash
git add ops
git commit -m "ops: nginx as single entry point for frontend and api"
```

---

## Фаза 3. Слой интеграции во фронте

### Task 8: Конфиг, ошибки и клиент

**Files:**
- Create: `frontend/lib/api/config.ts`, `frontend/lib/api/errors.ts`, `frontend/lib/api/client.ts`, `frontend/lib/api/types.ts`
- Create: `frontend/vitest.config.ts`, `frontend/lib/api/__tests__/errors.test.ts`, `frontend/lib/api/__tests__/client.test.ts`
- Modify: `frontend/package.json`

**Interfaces:**
- Produces:
  - `API_BASE_URL: string`, `isRealApi(): boolean` из `config.ts`
  - `class ApiError extends Error { status: number; code?: string }`, `toMessage(e: unknown): string` из `errors.ts`
  - `apiFetch<T>(path: string, init?: RequestInit & { auth?: boolean }): Promise<T>`, `setAccessToken(t: string | null)`, `getAccessToken(): string | null` из `client.ts`

- [ ] **Step 1: Поставить vitest**

```bash
cd C:\Claude\UCust-Platform\frontend
npm i -D vitest@^3
```

Добавить в `package.json` скрипт: `"test": "vitest run"`.

- [ ] **Step 2: Написать `vitest.config.ts`**

```ts
import { defineConfig } from "vitest/config";
import path from "node:path";

export default defineConfig({
  test: { environment: "node" },
  resolve: { alias: { "@": path.resolve(__dirname, ".") } },
});
```

- [ ] **Step 3: Написать падающий тест на разбор ошибок**

`lib/api/__tests__/errors.test.ts`:

```ts
import { describe, it, expect } from "vitest";
import { ApiError, toMessage } from "@/lib/api/errors";

describe("toMessage", () => {
  it("берёт message из ответа бэка", () => {
    expect(toMessage(new ApiError(400, "Пароли не совпадают", "PASSWORD_MISMATCH"))).toBe(
      "Пароли не совпадают",
    );
  });

  it("подставляет понятный текст для 401", () => {
    expect(toMessage(new ApiError(401, ""))).toBe("Неверная почта или пароль");
  });

  it("не показывает пользователю технические детали 500", () => {
    expect(toMessage(new ApiError(500, "NullPointerException at line 42"))).toBe(
      "Сервис временно недоступен, попробуйте позже",
    );
  });

  it("переживает не-ApiError", () => {
    expect(toMessage(new TypeError("fetch failed"))).toBe(
      "Не удалось связаться с сервером",
    );
  });
});
```

- [ ] **Step 4: Убедиться, что тест падает**

Run: `npm test -- errors`
Expected: FAIL — модуль `@/lib/api/errors` не найден

- [ ] **Step 5: Написать `errors.ts`**

```ts
/** Ошибка ответа API. Бэк отдаёт ApiError {status, code, message, time}. */
export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
    readonly code?: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/** Текст для пользователя: детали 5xx не показываем, они уходят только в консоль. */
export function toMessage(e: unknown): string {
  if (e instanceof ApiError) {
    if (e.status >= 500) return "Сервис временно недоступен, попробуйте позже";
    if (e.status === 401 && !e.message) return "Неверная почта или пароль";
    return e.message || "Не удалось выполнить запрос";
  }
  return "Не удалось связаться с сервером";
}
```

- [ ] **Step 6: Убедиться, что тест проходит**

Run: `npm test -- errors`
Expected: PASS, 4 теста

- [ ] **Step 7: Написать `config.ts` и `types.ts`**

`config.ts`:

```ts
/** Пусто → фронт работает на моках (режим витрины). Задано → ходит в настоящий API. */
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export function isRealApi(): boolean {
  return API_BASE_URL.length > 0;
}
```

`types.ts` — DTO бэка один-в-один:

```ts
export interface JwtResponse { accessToken: string; type: string }

export interface RegisterRequest {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export interface LoginRequest { email: string; password: string }

export interface ProfileResponse {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string | null;
  position: string | null;
  fullAvatarUrl: string | null;
}

export interface UpdateProfileRequest {
  firstName?: string;
  lastName?: string;
  phone?: string;
  position?: string;
}

export type Industry =
  | "CAFE_RESTAURANT" | "BEAUTY_SALON" | "RETAIL" | "SERVICES"
  | "EDUCATION" | "FITNESS" | "MEDICINE" | "OTHER";

export type ToneOfVoice = "FRIENDLY" | "PROFESSIONAL" | "INFORMAL" | "CREATIVE";

export interface SocialLinks {
  instagram?: string | null;
  telegram?: string | null;
  website?: string | null;
}

export interface ProjectRequest {
  name: string;
  industry: Industry;
  city: string;
  description?: string;
  targetAudience?: string;
  toneOfVoice: ToneOfVoice;
  socialLinks?: SocialLinks;
  businessHours?: null;
}

export interface ProjectResponse extends Omit<ProjectRequest, "businessHours"> {
  id: string;
  ownerId: string;
  logoUrl: string | null;
}
```

- [ ] **Step 8: Написать падающий тест на очередь refresh**

`lib/api/__tests__/client.test.ts`:

```ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { apiFetch, setAccessToken } from "@/lib/api/client";

const okJson = (body: unknown) =>
  new Response(JSON.stringify(body), { status: 200, headers: { "content-type": "application/json" } });

describe("apiFetch", () => {
  beforeEach(() => setAccessToken("expired"));

  it("на 401 обновляет токен и повторяет запрос один раз", async () => {
    const calls: string[] = [];
    const fetchMock = vi.fn(async (url: string) => {
      calls.push(url);
      if (url.endsWith("/auth/refresh")) return okJson({ accessToken: "fresh", type: "Bearer" });
      return calls.filter((c) => c.endsWith("/user/me")).length === 1
        ? new Response("", { status: 401 })
        : okJson({ id: "1" });
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await apiFetch<{ id: string }>("/user/me", { auth: true });

    expect(result).toEqual({ id: "1" });
    expect(calls.filter((c) => c.endsWith("/auth/refresh"))).toHaveLength(1);
  });

  it("параллельные 401 обновляют токен одним запросом, а не тремя", async () => {
    const refreshCalls: string[] = [];
    let meCalls = 0;
    const fetchMock = vi.fn(async (url: string) => {
      if (url.endsWith("/auth/refresh")) {
        refreshCalls.push(url);
        await new Promise((r) => setTimeout(r, 10));
        return okJson({ accessToken: "fresh", type: "Bearer" });
      }
      meCalls += 1;
      return meCalls <= 3 ? new Response("", { status: 401 }) : okJson({ id: "1" });
    });
    vi.stubGlobal("fetch", fetchMock);

    await Promise.all([
      apiFetch("/user/me", { auth: true }),
      apiFetch("/user/me", { auth: true }),
      apiFetch("/user/me", { auth: true }),
    ]);

    expect(refreshCalls).toHaveLength(1);
  });
});
```

- [ ] **Step 9: Убедиться, что тесты падают**

Run: `npm test -- client`
Expected: FAIL — модуль `@/lib/api/client` не найден

- [ ] **Step 10: Написать `client.ts`**

```ts
import { API_BASE_URL } from "./config";
import { ApiError } from "./errors";

/**
 * Access-токен живёт только в памяти вкладки: в localStorage его класть нельзя,
 * иначе любая XSS уносит сессию. Долгоживущий refresh лежит в httpOnly-куке,
 * недоступной JS.
 */
let accessToken: string | null = null;
let refreshing: Promise<string | null> | null = null;

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export function getAccessToken(): string | null {
  return accessToken;
}

async function refreshAccessToken(): Promise<string | null> {
  // Параллельные 401 должны сойтись в один запрос обновления, иначе гонка
  // сожжёт refresh-токен и выбросит пользователя из сессии.
  if (!refreshing) {
    refreshing = (async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/auth/refresh`, {
          method: "POST",
          credentials: "include",
        });
        if (!res.ok) return null;
        const data = (await res.json()) as { accessToken: string };
        accessToken = data.accessToken;
        return accessToken;
      } catch {
        return null;
      } finally {
        refreshing = null;
      }
    })();
  }
  return refreshing;
}

export interface ApiFetchInit extends RequestInit {
  /** true — подставить Authorization и при 401 попытаться обновить токен */
  auth?: boolean;
}

export async function apiFetch<T>(path: string, init: ApiFetchInit = {}): Promise<T> {
  const { auth = false, headers, ...rest } = init;

  const send = (token: string | null) =>
    fetch(`${API_BASE_URL}${path}`, {
      ...rest,
      credentials: "include",
      headers: {
        ...(rest.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...headers,
      },
    });

  let res = await send(auth ? accessToken : null);

  if (res.status === 401 && auth) {
    const fresh = await refreshAccessToken();
    if (fresh) res = await send(fresh);
  }

  if (!res.ok) {
    let message = "";
    let code: string | undefined;
    try {
      const body = (await res.json()) as { message?: string; code?: string };
      message = body.message ?? "";
      code = body.code;
    } catch {
      /* тело не JSON — оставляем пустое сообщение */
    }
    throw new ApiError(res.status, message, code);
  }

  if (res.status === 204) return undefined as T;
  const text = await res.text();
  return (text ? JSON.parse(text) : undefined) as T;
}
```

- [ ] **Step 11: Убедиться, что тесты проходят**

Run: `npm test`
Expected: PASS, 6 тестов

- [ ] **Step 12: Коммит**

```bash
git add lib/api vitest.config.ts package.json package-lock.json
git commit -m "feat(api): typed client with in-memory access token and single-flight refresh"
```

---

### Task 9: Функции API

**Files:**
- Create: `frontend/lib/api/auth.ts`, `frontend/lib/api/users.ts`, `frontend/lib/api/projects.ts`
- Create: `frontend/docs` не требуется; контракт описывается в `docs/api-contract.md` монорепо

**Interfaces:**
- Produces:
  - `register(req: RegisterRequest): Promise<void>`, `login(req: LoginRequest): Promise<string>`, `logout(): Promise<void>`, `refresh(): Promise<string | null>`, `resendConfirmation(email: string): Promise<void>`, `forgotPassword(email: string): Promise<void>`, `resetPassword(token: string, newPassword: string, confirmPassword: string): Promise<void>`
  - `getMe(): Promise<ProfileResponse>`, `updateMe(req: UpdateProfileRequest): Promise<ProfileResponse>`, `uploadAvatar(file: File): Promise<string>`
  - `listProjects(): Promise<ProjectResponse[]>`, `createProject(req: ProjectRequest): Promise<ProjectResponse>`, `updateProject(id, req): Promise<ProjectResponse>`, `uploadLogo(id: string, file: File): Promise<string>`

- [ ] **Step 1: Написать `auth.ts`**

```ts
import { apiFetch, setAccessToken } from "./client";
import type { JwtResponse, LoginRequest, RegisterRequest } from "./types";

export async function register(req: RegisterRequest): Promise<void> {
  await apiFetch<void>("/auth/register", { method: "POST", body: JSON.stringify(req) });
}

export async function login(req: LoginRequest): Promise<string> {
  const res = await apiFetch<JwtResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(req),
  });
  setAccessToken(res.accessToken);
  return res.accessToken;
}

export async function logout(): Promise<void> {
  try {
    await apiFetch<void>("/auth/logout", { method: "POST", auth: true });
  } finally {
    setAccessToken(null);
  }
}

export async function resendConfirmation(email: string): Promise<void> {
  await apiFetch<void>(`/auth/resend-confirmation?email=${encodeURIComponent(email)}`, {
    method: "POST",
  });
}

export async function forgotPassword(email: string): Promise<void> {
  await apiFetch<void>("/auth/forgot-password", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export async function resetPassword(
  token: string,
  newPassword: string,
  confirmPassword: string,
): Promise<void> {
  await apiFetch<void>("/auth/reset-password", {
    method: "POST",
    body: JSON.stringify({ token, newPassword, confirmPassword }),
  });
}
```

- [ ] **Step 2: Написать `users.ts`**

```ts
import { apiFetch } from "./client";
import type { ProfileResponse, UpdateProfileRequest } from "./types";

export function getMe(): Promise<ProfileResponse> {
  return apiFetch<ProfileResponse>("/user/me", { auth: true });
}

export function updateMe(req: UpdateProfileRequest): Promise<ProfileResponse> {
  return apiFetch<ProfileResponse>("/user/me", {
    method: "PATCH",
    auth: true,
    body: JSON.stringify(req),
  });
}

export async function uploadAvatar(file: File): Promise<string> {
  const form = new FormData();
  form.append("file", file);
  const res = await apiFetch<{ data: string }>("/user/me/avatar", {
    method: "POST",
    auth: true,
    body: form,
  });
  return res.data;
}
```

`uploadAvatar` возвращает поле `data`, потому что этот эндпоинт обёрнут в `ApiResponse<String>`, в отличие от остальных методов профиля.

- [ ] **Step 3: Написать `projects.ts`**

```ts
import { apiFetch } from "./client";
import type { ProjectRequest, ProjectResponse } from "./types";

export function listProjects(): Promise<ProjectResponse[]> {
  return apiFetch<ProjectResponse[]>("/projects", { auth: true });
}

export function createProject(req: ProjectRequest): Promise<ProjectResponse> {
  return apiFetch<ProjectResponse>("/projects", {
    method: "POST",
    auth: true,
    body: JSON.stringify(req),
  });
}

export function updateProject(
  id: string,
  req: Partial<ProjectRequest>,
): Promise<ProjectResponse> {
  return apiFetch<ProjectResponse>(`/projects/${id}`, {
    method: "PATCH",
    auth: true,
    body: JSON.stringify(req),
  });
}

export async function uploadLogo(id: string, file: File): Promise<string> {
  const form = new FormData();
  form.append("file", file);
  return apiFetch<string>(`/projects/${id}/logo`, { method: "POST", auth: true, body: form });
}
```

- [ ] **Step 4: Проверить типы**

Run: `npx tsc --noEmit`
Expected: без ошибок

- [ ] **Step 5: Записать контракт в монорепо**

`docs/api-contract.md` — таблица из спека (экран → метод → тело) плюс раздел «Расхождения с UI»: отчество не принимается, кириллица в имени, формат телефона `79XXXXXXXXX`.

- [ ] **Step 6: Коммит**

```bash
git add lib/api            # во frontend
git commit -m "feat(api): auth, users and projects endpoints"
```

---

### Task 10: Провайдер сессии

**Files:**
- Create: `frontend/lib/session/SessionProvider.tsx`
- Modify: `frontend/app/layout.tsx` (обернуть детей провайдером — вставка 2 строки)

**Interfaces:**
- Consumes: `login`, `logout`, `refresh` из Task 9; `getMe` из Task 9.
- Produces: `useSession(): { user: ProfileResponse | null; status: "loading" | "authenticated" | "anonymous"; signIn(email, password): Promise<void>; signOut(): Promise<void>; reload(): Promise<void> }`

- [ ] **Step 1: Написать `SessionProvider.tsx`**

```tsx
"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { isRealApi } from "@/lib/api/config";
import { apiFetch, setAccessToken } from "@/lib/api/client";
import { login as apiLogin, logout as apiLogout } from "@/lib/api/auth";
import { getMe } from "@/lib/api/users";
import type { JwtResponse, ProfileResponse } from "@/lib/api/types";

type Status = "loading" | "authenticated" | "anonymous";

interface SessionValue {
  user: ProfileResponse | null;
  status: Status;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  reload: () => Promise<void>;
}

const SessionContext = createContext<SessionValue | null>(null);

export function SessionProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<ProfileResponse | null>(null);
  const [status, setStatus] = useState<Status>(isRealApi() ? "loading" : "anonymous");

  const reload = useCallback(async () => {
    try {
      setUser(await getMe());
      setStatus("authenticated");
    } catch {
      setUser(null);
      setStatus("anonymous");
    }
  }, []);

  useEffect(() => {
    // В режиме моков сессии нет — витрина работает как раньше.
    if (!isRealApi()) return;
    // Access-токен живёт в памяти и умирает при перезагрузке страницы,
    // поэтому сессию восстанавливаем по httpOnly-куке.
    (async () => {
      try {
        const res = await apiFetch<JwtResponse>("/auth/refresh", { method: "POST" });
        setAccessToken(res.accessToken);
        await reload();
      } catch {
        setStatus("anonymous");
      }
    })();
  }, [reload]);

  const signIn = useCallback(
    async (email: string, password: string) => {
      await apiLogin({ email, password });
      await reload();
    },
    [reload],
  );

  const signOut = useCallback(async () => {
    await apiLogout();
    setUser(null);
    setStatus("anonymous");
  }, []);

  const value = useMemo(
    () => ({ user, status, signIn, signOut, reload }),
    [user, status, signIn, signOut, reload],
  );

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession(): SessionValue {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error("useSession вне SessionProvider");
  return ctx;
}
```

- [ ] **Step 2: Подключить провайдер в `app/layout.tsx`**

Обернуть текущее содержимое `<body>`:

```tsx
<SessionProvider>{children}</SessionProvider>
```

Импорт добавить рядом с остальными. Никакой другой правки в layout не делать.

- [ ] **Step 3: Проверить, что витрина не сломалась**

Run: `npm run build`
Expected: сборка проходит. Без `NEXT_PUBLIC_API_BASE_URL` провайдер не делает ни одного запроса — статика лендинга остаётся статикой.

- [ ] **Step 4: Коммит**

```bash
git add lib/session app/layout.tsx
git commit -m "feat(session): session provider with cookie-based bootstrap"
```

---

## Фаза 4. Экраны авторизации

### Task 11: Регистрация и подтверждение почты

**Files:**
- Modify: `frontend/app/signup/page.tsx`
- Modify: `frontend/app/signup/verify-email/page.tsx`

**Interfaces:**
- Consumes: `register`, `resendConfirmation` из Task 9; `isRealApi` из Task 8.

- [ ] **Step 1: Перевести форму регистрации на API**

Сейчас `handleSubmit` кладёт email в `sessionStorage` и делает `router.push`. Заменить на асинхронный обработчик, сохранив прежнее поведение в режиме моков:

```tsx
const [pending, setPending] = useState(false);
const [error, setError] = useState<string | null>(null);

const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
  e.preventDefault();
  const data = new FormData(e.currentTarget);
  const email = String(data.get("email") ?? "");
  try {
    sessionStorage.setItem("uc_signup_email", email);
  } catch {}

  if (!isRealApi()) {
    router.push("/signup/verify-email");
    return;
  }

  setPending(true);
  setError(null);
  try {
    await register({
      firstName: String(data.get("firstName") ?? ""),
      lastName: String(data.get("lastName") ?? ""),
      email,
      password: String(data.get("password") ?? ""),
      confirmPassword: String(data.get("confirmPassword") ?? ""),
    });
    router.push("/signup/verify-email");
  } catch (err) {
    setError(toMessage(err));
  } finally {
    setPending(false);
  }
};
```

Полям «Имя», «Фамилия», паролю и подтверждению пароля добавить атрибуты `name="firstName"`, `name="lastName"`, `name="password"`, `name="confirmPassword"` — сейчас их нет, и `FormData` их не увидит. Поле «Отчество» оставить без изменений: бэк его не принимает.

- [ ] **Step 2: Показать ошибку и блокировку кнопки**

Под формой вывести `error` в существующем стиле проекта, кнопку отправки на время запроса перевести в `disabled={pending}` с текстом «Создаём аккаунт…».

- [ ] **Step 3: Оживить кнопку повторной отправки письма**

На `/signup/verify-email` кнопка повторной отправки в режиме реального API вызывает `resendConfirmation(email)`, где email берётся из `sessionStorage.getItem("uc_signup_email")`. После успеха — уведомление через существующий `lib/toast.ts`.

- [ ] **Step 4: Проверить вживую**

При поднятом туннеле и `NEXT_PUBLIC_API_BASE_URL=http://localhost:8080/api/v0` в `.env.local`:

```bash
npm run dev
```

Зарегистрировать аккаунт на реальный адрес. Ожидается: письмо приходит на почту, в `security_service_db` появляется пользователь:

```bash
ssh -i ~/.ssh/ucust_gpu -p 40298 user@195.208.16.1 \
  "docker exec -i \$(docker ps -qf name=postgres-db) psql -U ucust -d security_service_db -c 'select email, is_active from users order by id desc limit 3;'"
```

- [ ] **Step 5: Коммит**

```bash
git add app/signup
git commit -m "feat(auth): real registration and confirmation resend"
```

---

### Task 12: Вход, выход и защита дашборда

**Files:**
- Modify: `frontend/app/login/page.tsx`
- Modify: `frontend/components/dashboard/ProfileMenu.tsx` (кнопка выхода)
- Create: `frontend/components/auth/AuthGuard.tsx`
- Modify: `frontend/app/dashboard/layout.tsx` (обернуть — вставка 2 строки)

**Interfaces:**
- Consumes: `useSession` из Task 10.
- Produces: `AuthGuard` — компонент, который в режиме реального API держит неавторизованных вне дашборда.

- [ ] **Step 1: Перевести форму входа на `signIn`**

По аналогии с Task 11: в режиме моков поведение прежнее, в реальном — `await signIn(email, password)` и переход на `/dashboard`. Ошибку показывать текстом из `toMessage`.

- [ ] **Step 2: Написать `AuthGuard.tsx`**

```tsx
"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { isRealApi } from "@/lib/api/config";
import { useSession } from "@/lib/session/SessionProvider";

/** В режиме моков пропускает всех — витрина должна открываться без бэка. */
export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const { status } = useSession();
  const router = useRouter();

  const blocked = isRealApi() && status === "anonymous";

  useEffect(() => {
    if (blocked) router.replace("/login");
  }, [blocked, router]);

  if (isRealApi() && status === "loading") return null;
  if (blocked) return null;
  return <>{children}</>;
}
```

- [ ] **Step 3: Обернуть дашборд**

В `app/dashboard/layout.tsx` обернуть содержимое в `<AuthGuard>`, снаружи существующего `ProjectGuard`.

- [ ] **Step 4: Оживить выход**

В `ProfileMenu` пункт выхода вызывает `signOut()` и `router.push("/")`.

- [ ] **Step 5: Проверить**

С реальным API: зайти под подтверждённым аккаунтом → попасть на дашборд; открыть `/dashboard` в новой вкладке без входа → редирект на `/login`; после `signOut` дашборд снова недоступен.

- [ ] **Step 6: Коммит**

```bash
git add app/login app/dashboard/layout.tsx components/auth components/dashboard/ProfileMenu.tsx
git commit -m "feat(auth): real login, logout and dashboard guard"
```

---

### Task 13: Восстановление пароля

**Files:**
- Modify: `frontend/app/forgot-password/page.tsx`
- Modify: `frontend/app/forgot-password/reset/page.tsx`

**Interfaces:**
- Consumes: `forgotPassword`, `resetPassword` из Task 9.

- [ ] **Step 1: Отправка письма**

Форма на `/forgot-password` в реальном режиме вызывает `forgotPassword(email)` и переходит на `/forgot-password/check-email`. Ошибку показывать текстом; при 404 (адрес не найден) показывать то же нейтральное сообщение, что и при успехе, — иначе форма превращается в проверку существования аккаунтов.

- [ ] **Step 2: Смена пароля по токену**

Страница `/forgot-password/reset` читает `token` из query (`useSearchParams`) и при отправке вызывает `resetPassword(token, newPassword, confirmPassword)`. При отсутствии токена показывать сообщение «Ссылка недействительна, запросите новую».

- [ ] **Step 3: Проверить сквозной сценарий**

Запросить письмо → перейти по ссылке из почты → задать новый пароль → войти с новым паролем.

- [ ] **Step 4: Коммит**

```bash
git add app/forgot-password
git commit -m "feat(auth): real password recovery flow"
```

---

## Фаза 5. Профиль и бизнес-проект

### Task 14: Поле `brand_profile` в business-service

**Files:**
- Modify: `backend/business-service/.../domain/model/project/Project.java`
- Modify: `backend/business-service/.../dto/ProjectRequest.java`, `UpdateProjectRequest.java`, `ProjectResponse.java`
- Modify: `backend/business-service/.../service/ProjectService.java` (или маппер MapStruct)
- Modify: `docs/backend-patches.md`

**Interfaces:**
- Produces: поле `brandProfile: string | null` в `ProjectRequest`/`ProjectResponse` — фронт кладёт туда сериализованный `BrandProfile`.

- [ ] **Step 1: Добавить колонку в сущность**

```java
@Column(columnDefinition = "jsonb")
@JdbcTypeCode(SqlTypes.JSON)
private String brandProfile;
```

`ddl-auto: update` создаст колонку сама — отдельная миграция не нужна.

- [ ] **Step 2: Добавить поле в DTO**

В `ProjectRequest`, `UpdateProjectRequest` и `ProjectResponse` добавить `String brandProfile`. В `ProjectRequest` ограничить размер: `@Size(max = 20000)`.

- [ ] **Step 3: Пробросить поле в сервисе/маппере**

Если используется MapStruct — поле подхватится по имени автоматически; проверить, что в маппере нет `@Mapping(ignore)` для неизвестных полей. Если маппинг ручной — добавить присваивание в `create` и `update`.

- [ ] **Step 4: Пересобрать и проверить**

```bash
bash ops/deploy.sh business-service
ssh -i ~/.ssh/ucust_gpu -p 40298 user@195.208.16.1 \
  "docker exec -i \$(docker ps -qf name=postgres-db) psql -U ucust -d business_service_db -c '\\d projects'"
```

Expected: в списке колонок присутствует `brand_profile` типа `jsonb`

- [ ] **Step 5: Коммит**

```bash
git add backend/business-service docs/backend-patches.md
git commit -m "backend: store full brand profile as jsonb on project"
```

---

### Task 15: Маппинг онбординга в проект

**Files:**
- Create: `frontend/lib/api/mapProfile.ts`
- Create: `frontend/lib/api/__tests__/mapProfile.test.ts`
- Modify: `frontend/components/onboarding/review/ReviewFlow.tsx` (сохранение — вставка вызова)

**Interfaces:**
- Consumes: `WizardInput`, `BrandProfile` из `lib/onboarding/types`; `createProject` из Task 9.
- Produces: `toProjectRequest(input: WizardInput, profile: BrandProfile): ProjectRequest`

- [ ] **Step 1: Написать падающие тесты**

`lib/api/__tests__/mapProfile.test.ts`:

```ts
import { describe, it, expect } from "vitest";
import { toProjectRequest } from "@/lib/api/mapProfile";
import { EMPTY_INPUT } from "@/lib/onboarding/types";
import type { BrandProfile } from "@/lib/onboarding/types";

const profile: BrandProfile = {
  name: "Кофейня «Пар»",
  field: "Кофейня",
  positioning: "Третье место в спальном районе",
  market: { competitors: [], geography: "Санкт-Петербург", segment: "Жители района 25–40", trends: [] },
  swot: { strengths: ["Обжарка"], weaknesses: [], opportunities: [], threats: [] },
  services: [],
  goals: ["Вернуть гостей"],
  tone: ["дружелюбный"],
};

describe("toProjectRequest", () => {
  it("подбирает отрасль по нише", () => {
    expect(toProjectRequest({ ...EMPTY_INPUT, name: "Пар" }, profile).industry).toBe("CAFE_RESTAURANT");
  });

  it("для незнакомой ниши отдаёт OTHER", () => {
    const other = { ...profile, field: "Ремонт квадрокоптеров" };
    expect(toProjectRequest(EMPTY_INPUT, other).industry).toBe("OTHER");
  });

  it("переводит тон в enum", () => {
    expect(toProjectRequest(EMPTY_INPUT, profile).toneOfVoice).toBe("FRIENDLY");
  });

  it("берёт город из географии, аудиторию из сегмента", () => {
    const req = toProjectRequest(EMPTY_INPUT, profile);
    expect(req.city).toBe("Санкт-Петербург");
    expect(req.targetAudience).toBe("Жители района 25–40");
  });

  it("обрезает описание до 2000 символов", () => {
    const long = { ...EMPTY_INPUT, description: "я".repeat(2500) };
    expect(toProjectRequest(long, profile).description).toHaveLength(2000);
  });

  it("складывает профиль целиком в brandProfile", () => {
    const req = toProjectRequest(EMPTY_INPUT, profile);
    expect(JSON.parse(req.brandProfile!).swot.strengths).toEqual(["Обжарка"]);
  });
});
```

- [ ] **Step 2: Убедиться, что тесты падают**

Run: `npm test -- mapProfile`
Expected: FAIL — модуль не найден

- [ ] **Step 3: Написать `mapProfile.ts`**

```ts
import type { BrandProfile, WizardInput } from "@/lib/onboarding/types";
import type { Industry, ProjectRequest, ToneOfVoice } from "./types";

const INDUSTRY_HINTS: Array<[Industry, RegExp]> = [
  ["CAFE_RESTAURANT", /кофе|кафе|ресторан|бар|пекарн|кондитер|пицц|суши|достав.*ед/i],
  ["BEAUTY_SALON", /салон|красот|барбер|парикмахер|маникюр|ногт|бров|космет|спа/i],
  ["FITNESS", /фитнес|спорт|зал|йог|танц|бассейн|тренаж/i],
  ["MEDICINE", /клиник|медицин|стоматолог|врач|лаборатор|аптек/i],
  ["EDUCATION", /школ|курс|обучен|образован|репетитор|детск.*центр|языков/i],
  ["RETAIL", /магазин|розниц|товар|бутик|шоурум|маркет/i],
  ["SERVICES", /услуг|сервис|ремонт|клининг|ателье|автомой|юридич|бухгалтер/i],
];

const TONE_HINTS: Array<[ToneOfVoice, RegExp]> = [
  ["FRIENDLY", /дружелюб|тёпл|тепл|заботлив|душевн/i],
  ["PROFESSIONAL", /профессионал|эксперт|деловой|официальн|строг/i],
  ["INFORMAL", /неформальн|на «ты»|простой|разговорн|свойск/i],
  ["CREATIVE", /креатив|игрив|смел|нестандартн|ярк/i],
];

function pick<T>(hints: Array<[T, RegExp]>, text: string, fallback: T): T {
  return hints.find(([, re]) => re.test(text))?.[0] ?? fallback;
}

/** Онбординг богаче ProjectRequest, поэтому профиль целиком уезжает в brandProfile. */
export function toProjectRequest(input: WizardInput, profile: BrandProfile): ProjectRequest {
  const nicheText = [profile.field, profile.positioning, input.activity].join(" ");
  const toneText = profile.tone.join(" ");

  return {
    name: (input.name || profile.name).slice(0, 100),
    industry: pick(INDUSTRY_HINTS, nicheText, "OTHER"),
    city: (profile.market.geography || "Не указан").slice(0, 50),
    description: input.description.slice(0, 2000),
    targetAudience: profile.market.segment.slice(0, 500),
    toneOfVoice: pick(TONE_HINTS, toneText, "FRIENDLY"),
    socialLinks: {
      instagram: input.link.startsWith("https://") ? input.link : null,
      telegram: input.socials.includes("telegram") ? "" : null,
      website: null,
    },
    businessHours: null,
    brandProfile: JSON.stringify(profile),
  };
}
```

Поле `brandProfile` добавить в интерфейс `ProjectRequest` в `lib/api/types.ts`:
`brandProfile?: string;`

- [ ] **Step 4: Убедиться, что тесты проходят**

Run: `npm test -- mapProfile`
Expected: PASS, 6 тестов

- [ ] **Step 5: Сохранять проект в конце онбординга**

В `ReviewFlow` при подтверждении профиля в режиме реального API вызвать `createProject(toProjectRequest(input, profile))` и после успеха переходить на дашборд. В режиме моков поведение прежнее (`sessionStorage`).

- [ ] **Step 6: Загружать проекты в дашборд через адаптер**

Правило «не более 3 строк подряд в существующих файлах» здесь важно: `DashboardProvider`
активно правится в витрине. Поэтому вся логика уходит в новый файл
`frontend/lib/dashboard/source.ts`:

```ts
import { isRealApi } from "@/lib/api/config";
import { listProjects } from "@/lib/api/projects";
import type { BrandProfile } from "@/lib/onboarding/types";
import { loadOnboarding } from "@/lib/onboarding/storage";

export interface WorkspaceSnapshot {
  hasProject: boolean;
  profile: BrandProfile | null;
  projectId: string | null;
}

/** Один источник данных рабочей области: сервер в реальном режиме, sessionStorage в моках. */
export async function loadWorkspace(): Promise<WorkspaceSnapshot> {
  if (!isRealApi()) {
    const local = loadOnboarding();
    return { hasProject: Boolean(local?.profile), profile: local?.profile ?? null, projectId: null };
  }

  const projects = await listProjects();
  const first = projects[0];
  if (!first) return { hasProject: false, profile: null, projectId: null };

  let profile: BrandProfile | null = null;
  try {
    // brandProfile мог быть записан старой версией фронта — повреждённый JSON
    // не должен ронять дашборд целиком.
    profile = first.brandProfile ? (JSON.parse(first.brandProfile) as BrandProfile) : null;
  } catch {
    profile = null;
  }
  return { hasProject: true, profile, projectId: first.id };
}
```

В `DashboardProvider` заменяется только источник: вместо `loadOnboarding()` вызывается
`loadWorkspace()`, результат раскладывается в существующее состояние. `hasProject` и
`hydrated` сохраняют прежний смысл, поэтому `ProjectGuard` править не нужно.

Добавить `brandProfile?: string | null` в `ProjectResponse` в `lib/api/types.ts`.

- [ ] **Step 7: Проверить сквозной сценарий**

Пройти онбординг → перезагрузить страницу → профиль на месте:

```bash
ssh -i ~/.ssh/ucust_gpu -p 40298 user@195.208.16.1 \
  "docker exec -i \$(docker ps -qf name=postgres-db) psql -U ucust -d business_service_db -c 'select name, industry, tone_of_voice from projects;'"
```

- [ ] **Step 8: Коммит**

```bash
git add lib/api components/onboarding components/dashboard/DashboardProvider.tsx
git commit -m "feat(projects): persist onboarding brand profile to backend"
```

---

### Task 16: Профиль пользователя

**Files:**
- Modify: `frontend/components/dashboard/account/AccountSettings.tsx`

**Interfaces:**
- Consumes: `getMe`, `updateMe`, `uploadAvatar` из Task 9; `useSession` из Task 10.

- [ ] **Step 1: Заполнять форму данными из сессии**

В реальном режиме начальные значения полей берутся из `useSession().user`, а не из моков.

- [ ] **Step 2: Сохранение**

Кнопка сохранения вызывает `updateMe({ firstName, lastName, phone, position })`, затем `reload()` из сессии.

- [ ] **Step 3: Продублировать валидацию бэка**

Бэк отвергает латиницу в имени и телефон не в формате `79XXXXXXXXX`. Проверять до отправки и показывать подсказку под полем: «Имя кириллицей, можно с дефисом» и «Телефон в формате 79XXXXXXXXX». Иначе пользователь получает 400 без объяснений.

- [ ] **Step 4: Аватар**

Выбор файла вызывает `uploadAvatar(file)`, затем `reload()`. Ограничить размер 10 МБ до отправки — столько принимает Spring.

- [ ] **Step 5: Проверить**

Сменить имя и телефон → перезагрузить страницу → значения сохранились. Загрузить аватар → появился в MinIO:

```bash
ssh -i ~/.ssh/ucust_gpu -p 40298 user@195.208.16.1 \
  "docker exec -i \$(docker ps -qf name=minio) mc ls local/user-service 2>/dev/null || echo 'проверить через консоль MinIO'"
```

- [ ] **Step 6: Коммит**

```bash
git add components/dashboard/account
git commit -m "feat(account): real profile editing with avatar upload"
```

---

## Фаза 6. Фронт в контуре и сквозная проверка

### Task 17: Фронт в Docker за nginx

**Files:**
- Create: `frontend/Dockerfile`, `frontend/.dockerignore`
- Modify: `frontend/next.config.ts` (добавить `output: "standalone"`)
- Modify: `ops/docker-compose.stack.yml`, `ops/deploy.sh`

**Interfaces:**
- Produces: контейнер `frontend`, на который уже указывает `location /` из Task 7.

- [ ] **Step 1: Включить standalone-сборку**

В `next.config.ts` добавить `output: "standalone"` — иначе в образ придётся тащить весь `node_modules`.

- [ ] **Step 2: Написать `Dockerfile`**

```dockerfile
FROM node:24-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:24-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ARG NEXT_PUBLIC_API_BASE_URL
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL
RUN npm run build

FROM node:24-alpine AS run
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
COPY --from=build /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
```

`NEXT_PUBLIC_*` подставляется на этапе сборки, поэтому передаётся как `ARG`, а не как переменная контейнера.

- [ ] **Step 3: Написать `.dockerignore`**

```
node_modules
.next
.git
docs
screenshots
*.log
```

- [ ] **Step 4: Добавить сервис в compose**

```yaml
  frontend:
    build:
      context: ../frontend
      args:
        NEXT_PUBLIC_API_BASE_URL: /api/v0
    depends_on: [api-gateway]
```

Относительный `/api/v0` работает, потому что фронт и API за одним nginx — браузер сам подставит текущий origin.

- [ ] **Step 5: Добавить frontend в rsync**

В `ops/deploy.sh` добавить `frontend` в список каталогов (исключения `node_modules`, `.next` уже прописаны).

- [ ] **Step 6: Собрать и проверить через туннель**

```bash
bash ops/deploy.sh
```

Открыть `http://localhost:8080` при поднятом туннеле.
Expected: лендинг отдаётся; переход на `/login` и вход работают на настоящем API.

- [ ] **Step 7: Коммит**

```bash
git add frontend/Dockerfile frontend/.dockerignore frontend/next.config.ts ops
git commit -m "ops: serve frontend from the same nginx as api"
```

---

### Task 18: Сквозной e2e-сценарий

**Files:**
- Create: `frontend/tests/e2e/signup-to-project.spec.ts`
- Create: `ops/docker-compose.mail-test.yml`

**Interfaces:**
- Consumes: весь стек из предыдущих задач.

- [ ] **Step 1: Добавить профиль с Mailpit**

`ops/docker-compose.mail-test.yml` — оверлей, подменяющий почту на локальный перехватчик:

```yaml
services:
  mailpit:
    image: axllent/mailpit
    ports:
      - "8025:8025"

  notification-service:
    environment:
      MAIL_HOST: mailpit
      MAIL_PORT: 1025
```

Запуск: `docker compose -f ops/docker-compose.stack.yml -f ops/docker-compose.mail-test.yml up -d`

Mailpit нужен потому, что читать реальную почту из теста — это внешняя зависимость, которая делает прогон нестабильным.

- [ ] **Step 2: Написать сценарий**

`frontend/tests/e2e/signup-to-project.spec.ts`:

```ts
import { test, expect } from "@playwright/test";

const BASE = process.env.E2E_BASE_URL ?? "http://localhost:8080";
const MAILPIT = process.env.E2E_MAILPIT_URL ?? "http://localhost:8025";

test("регистрация, подтверждение, вход и создание проекта", async ({ page, request }) => {
  const email = `e2e-${Date.now()}@example.com`;
  const password = "Passw0rd!";

  await page.goto(`${BASE}/signup`);
  await page.fill('input[name="firstName"]', "Иван");
  await page.fill('input[name="lastName"]', "Иванов");
  await page.fill('input[name="email"]', email);
  await page.fill('input[name="password"]', password);
  await page.fill('input[name="confirmPassword"]', password);
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/verify-email/);

  // письмо перехватывает Mailpit — достаём ссылку активации
  const messages = await (await request.get(`${MAILPIT}/api/v1/messages`)).json();
  const id = messages.messages[0].ID;
  const body = await (await request.get(`${MAILPIT}/api/v1/message/${id}`)).json();
  const link = /href="([^"]*confirm\?token=[^"]+)"/.exec(body.HTML)?.[1];
  expect(link).toBeTruthy();
  await request.get(link!);

  await page.goto(`${BASE}/login`);
  await page.fill('input[name="email"]', email);
  await page.fill('input[name="password"]', password);
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/dashboard/);

  // сессия переживает перезагрузку — access-токен восстанавливается по куке
  await page.reload();
  await expect(page).toHaveURL(/dashboard/);
});
```

- [ ] **Step 3: Прогнать**

Run: `npx playwright test tests/e2e/signup-to-project.spec.ts`
Expected: PASS

- [ ] **Step 4: Коммит**

```bash
git add tests/e2e ops/docker-compose.mail-test.yml
git commit -m "test(e2e): signup through project creation against real stack"
```

---

## Что осталось за рамками плана

- Публикация наружу через Cloudflare Tunnel на `app.ucust.online` — делается под демонстрацию, требует перевода NS домена с Reg.ru на Cloudflare.
- OAuth Яндекса: редиректы захардкожены на `localhost:3000`, ключи в репозитории команды. Включать отдельной задачей.
- Контент, промо, отзывы, входящие, аналитика, подписка, ИИ-генерация — бэка нет, остаются моками.
- ML-контур (Saiga, Kandinsky) на V100 — отдельный проект.
