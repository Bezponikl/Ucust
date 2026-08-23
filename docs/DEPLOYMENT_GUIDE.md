# 🚀 Руководство по развертыванию и запуску UCust на 2 серверах

Данная инструкция описывает пошаговый процесс запуска production-окружения проекта **UCust** на двух выделенных серверах.

---

## 🗺️ Топология серверов

```
┌─────────────────────────────────────────────────────────────┐
│               СЕРВЕР 1: БЭКЕНД + БАЗЫ ДАННЫХ                │
│             (IP: 1.1.1.1, Домен: api.ucust.ru)              │
│                                                             │
│  • Java Spring Boot микросервисы (security, user, business, │
│    billing, generative-orchestration, notification)         │
│  • PostgreSQL 16 (Порт 5432)                                │
│  • MinIO / S3 (Порт 9000/9001 - Хранилище медиа)            │
│  • Nginx Reverse Proxy (SSL HTTPS / Let's Encrypt)          │
└───────────────────────┬───────────────────▲─────────────────┘
                        │                   │
        1. Публикация   │                   │ 3. Получение
           задач в      │                   │    результатов
           RabbitMQ     │                   │    генерации
                        ▼                   │
┌───────────────────────────────────────────┴─────────────────┐
│             СЕРВЕР 2: ФРОНТЕНД + ИИ + RABBITMQ              │
│               (IP: 2.2.2.2, Домен: ucust.ru)                │
│                                                             │
│  • Next.js 15 Frontend (Порт 3000 -> 80/443)                │
│  • RabbitMQ Message Broker (Порт 5672)                      │
│  • Python FastAPI AI Service Gateway (Порт 8000 + GPU)      │
│  • ComfyUI / PyTorch / Saiga / LTX-2                        │
│  • Nginx Reverse Proxy (SSL HTTPS / Let's Encrypt)          │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 1. Системные требования

| Сервер | Назначение | Рекомендуемые характеристики | ОС |
| :--- | :--- | :--- | :--- |
| **Сервер 1** | Бэкенд + БД + MinIO | 4–8 CPU, 16–32 GB RAM, 100+ GB NVMe SSD | Ubuntu 22.04 / 24.04 LTS |
| **Сервер 2** | Фронтенд + AI + RabbitMQ | 8+ CPU, 32–64 GB RAM, 1x GPU (NVIDIA RTX 3090 / 4090 / A100), 200+ GB SSD | Ubuntu 22.04 / 24.04 LTS + NVIDIA Drivers |

---

## ⚙️ 2. Подготовка обоих серверов (Базовая настройка)

Выполните на **обоих серверах**:

```bash
# 1. Обновление пакетов
sudo apt update && sudo apt upgrade -y

# 2. Установка Docker и Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 3. Установка Git и утилит
sudo apt install -y git ufw htop curl
```

### Дополнительно для Сервера 2 (Установка драйверов GPU и NVIDIA Docker Toolkit):
```bash
# Установка драйверов NVIDIA
sudo apt install -y nvidia-driver-535 nvidia-utils-535

# Установка NVIDIA Container Toolkit (для проброса GPU в Docker)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt update
sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

---

## 🗄️ 3. Развертывание Сервера 1 (Бэкенд + БД + MinIO)

### Шаг 3.1. Клонирование репозитория
```bash
git clone https://github.com/Bezponikl/Ucust.git /opt/ucust
cd /opt/ucust
git checkout develop  # или ваша релизная ветка
```

### Шаг 3.2. Файл окружения `.env.backend`
Создайте файл `/opt/ucust/.env.backend`:
```env
# База данных PostgreSQL
POSTGRES_DB=ucust_db
POSTGRES_USER=ucust_user
POSTGRES_PASSWORD=StrongDevPassword2026!
POSTGRES_PORT=5432

# Брокер RabbitMQ (указываем IP Сервера 2)
RABBITMQ_HOST=2.2.2.2
RABBITMQ_PORT=5672
RABBITMQ_USER=ucust_rabbit
RABBITMQ_PASS=RabbitSecretPass2026!

# MinIO (S3 хранилище)
MINIO_ROOT_USER=admin_minio
MINIO_ROOT_PASSWORD=MinioSecretPass2026!
MINIO_PORT=9000
MINIO_CONSOLE_PORT=9001
MINIO_ENDPOINT=http://1.1.1.1:9000

# JWT Секреты
JWT_SECRET=super_secret_jwt_key_at_least_256_bits_long_ucust_2026
JWT_EXPIRATION_MS=86400000

# CORS (Адрес фронтенда на Сервере 2)
CORS_ALLOWED_ORIGINS=https://ucust.ru,http://2.2.2.2:3000
```

### Шаг 3.3. Запуск инфраструктуры и микросервисов
```bash
cd /opt/ucust/src/N4d3sh1k4-UCust_Dev

# Запуск БД, MinIO и микросервисов
docker compose -f docker-compose.yml up -d --build

# Проверка статуса контейнеров
docker compose ps
```

---

## 🎨 4. Развертывание Сервера 2 (Фронтенд + AI + RabbitMQ)

### Шаг 4.1. Клонирование репозитория
```bash
git clone https://github.com/Bezponikl/Ucust.git /opt/ucust
cd /opt/ucust
git checkout integration-test
```

### Шаг 4.2. Настройка окружения Фронтенда
Создайте файл `/opt/ucust/Frontend/.env.production`:
```env
# Адрес API бэкенда на Сервере 1
NEXT_PUBLIC_API_URL=https://api.ucust.ru/api/v1

# Адрес AI Gateway на этом же сервере
NEXT_PUBLIC_AI_URL=https://ucust.ru/ai-api
NEXT_PUBLIC_AI_WS_URL=wss://ucust.ru/ws
```

### Шаг 4.3. Настройка окружения AI-модуля
Создайте файл `/opt/ucust/ai/.env`:
```env
UCUST_ENV=production
UCUST_PORT=8000
UCUST_HOST=0.0.0.0

# Локальный RabbitMQ на этом же сервере
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=ucust_rabbit
RABBITMQ_PASSWORD=RabbitSecretPass2026!

# Связь с MinIO на Сервере 1
S3_ENDPOINT=http://1.1.1.1:9000
S3_ACCESS_KEY=admin_minio
S3_SECRET_KEY=MinioSecretPass2026!
S3_BUCKET_NAME=generative-orchestration

# Связь с бэкендом для вебхуков
JAVA_BACKEND_URL=https://api.ucust.ru
```

### Шаг 4.4. Запуск RabbitMQ, AI Gateway и Next.js

1. **Запуск RabbitMQ (в Docker):**
```bash
docker run -d --name ucust-rabbitmq \
  --restart unless-stopped \
  -p 5672:5672 \
  -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=ucust_rabbit \
  -e RABBITMQ_DEFAULT_PASS=RabbitSecretPass2026! \
  rabbitmq:3-management
```

2. **Запуск AI Gateway (Python FastAPI):**
```bash
cd /opt/ucust/ai
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Фоновый запуск FastAPI через uvicorn / gunicorn
nohup uvicorn api_gateway:app --host 0.0.0.0 --port 8000 --workers 2 > ai_gateway.log 2>&1 &
```

3. **Сборка и запуск Frontend (Next.js):**
```bash
cd /opt/ucust/Frontend
npm install
npm run build

# Установка PM2 для автоперезапуска
sudo npm install -g pm2
pm2 start npm --name "ucust-frontend" -- start -- -p 3000
pm2 save
pm2 startup
```

---

## 🔒 5. Настройка Firewall (UFW) и безопасность

### На Сервере 1 (Бэкенд + БД):
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp                # SSH
sudo ufw allow 80/tcp                # HTTP
sudo ufw allow 443/tcp               # HTTPS

# Разрешаем доступ к MinIO только для IP Сервера 2
sudo ufw allow from 2.2.2.2 to any port 9000 proto tcp

sudo ufw enable
```

### На Сервере 2 (Фронтенд + AI + RabbitMQ):
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp                # SSH
sudo ufw allow 80/tcp                # HTTP для пользователей
sudo ufw allow 443/tcp               # HTTPS для пользователей

# Разрешаем доступ к RabbitMQ ТОЛЬКО для IP Сервера 1
sudo ufw allow from 1.1.1.1 to any port 5672 proto tcp

sudo ufw enable
```

---

## 🌐 6. Конфигурация Nginx и SSL

### Nginx на Сервере 1 (`/etc/nginx/sites-available/api.ucust.ru`):
```nginx
server {
    server_name api.ucust.ru;

    location / {
        proxy_pass http://localhost:8080; # Gateway бэкенда
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Nginx на Сервере 2 (`/etc/nginx/sites-available/ucust.ru`):
```nginx
server {
    server_name ucust.ru;

    # 1. Фронтенд Next.js
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 2. Проксирование WebSocket для AI-онбординга
    location /ws/ {
        proxy_pass http://localhost:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }

    # 3. Проксирование REST AI Gateway
    location /ai-api/ {
        proxy_pass http://localhost:8000/api/v1/ai/;
        proxy_set_header Host $host;
    }
}
```

### Выпуск SSL сертификатов (Let's Encrypt):
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d ucust.ru          # на Сервере 2
sudo certbot --nginx -d api.ucust.ru      # на Сервере 1
```

---

## ✅ 7. Чек-лист проверки работоспособности

1. **Проверка бэкенда (Сервер 1):**
   ```bash
   curl -I https://api.ucust.ru/actuator/health
   ```
2. **Проверка AI Gateway (Сервер 2):**
   ```bash
   curl https://ucust.ru/ai-api/health
   # Ответ: {"status":"healthy","service":"UCust AI Gateway", ...}
   ```
3. **Проверка RabbitMQ (Связь между серверами):**
   На Сервере 1 выполнить проверку порта брокера:
   ```bash
   nc -zv 2.2.2.2 5672
   # Должно вернуть: Connection to 2.2.2.2 5672 port [tcp/*] succeeded!
   ```
4. **Проверка UI:**
   Открыть `https://ucust.ru/dashboard/create`, ввести текст и нажать **«Сгенерировать»**.
