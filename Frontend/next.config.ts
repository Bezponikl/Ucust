import type { NextConfig } from "next";

type RemotePattern = NonNullable<NonNullable<NextConfig["images"]>["remotePatterns"]>[number];

/** Базовый origin AI-контура: в dev это мок, в проде — nginx/шлюз (задирается переменной). */
function aiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_AI_BASE_URL ?? "http://localhost:8000";
}

function originPattern(origin: URL): RemotePattern {
  return {
    protocol: origin.protocol === "https:" ? "https" : "http",
    hostname: origin.hostname,
    port: origin.port,
    pathname: "/**",
    search: "",
  };
}

/**
 * Шлюз отдаёт ссылки на файлы абсолютными URL того же origin, что и API
 * (логотип проекта, медиа, аватар — `/s3/...`). next/image в этом проекте
 * локальный путь не трогает, но абсолютный URL без remotePatterns режет 400.
 * Разрешаем только наш же origin: локальный localhost:8100 и прод-домен.
 * В локальной разработке — ещё и origin AI-контура (мок на localhost:8000):
 * старые посты в БД шлюза могут содержать абсолютный image_url с этим хостом.
 */
function remotePatterns(): RemotePattern[] {
  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api/v0";
  // Относительный путь = фронт и шлюз за одним nginx, remote-картинок нет.
  if (!apiBase.startsWith("http://") && !apiBase.startsWith("https://")) return [];

  let apiOrigin: URL | null = null;
  try {
    apiOrigin = new URL(apiBase);
  } catch {
    // Битый адрес из .env.local не должен ронять сборку.
    return [];
  }

  const patterns: RemotePattern[] = [originPattern(apiOrigin)];

  if (isLocalApi()) {
    try {
      const aiOrigin = new URL(aiBaseUrl());
      if (aiOrigin.hostname !== apiOrigin.hostname || aiOrigin.port !== apiOrigin.port) {
        patterns.push(originPattern(aiOrigin));
      }
    } catch {
      // Битый адрес контура — не роняем сборку.
    }
  }

  return patterns;
}

/** Локальный шлюз (localhost/127.0.0.1) — Next 16 режет приватные IP по умолчанию. */
function isLocalApi(): boolean {
  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api/v0";
  try {
    const host = new URL(apiBase).hostname;
    return host === "localhost" || host === "127.0.0.1" || host === "::1";
  } catch {
    return false;
  }
}

/**
 * AI-контур отдаёт сгенерированные фото host-agnostic путями `/output/photos/...`
 * (как реальный контур, photo_generator.py). В проде путь разрешает nginx на
 * origin фронта. В локальной разработке контур живёт на localhost:8000 (мок),
 * поэтому в dev проксируем `/output/**` на него — ровно как это делает nginx.
 */
async function rewrites(): Promise<{ source: string; destination: string }[]> {
  const aiBase = aiBaseUrl();
  return [
    {
      source: "/output/:path*",
      destination: `${aiBase}/output/:path*`,
    },
  ];
}

const nextConfig: NextConfig = {
  // Скрываем dev-индикатор Next.js (кружок «N» в углу) — только в разработке.
  devIndicators: false,
  // Отдельный сервер для Docker: .next/standalone + public + static копируются
  // в образ и запускаются одним процессом без установки node_modules.
  output: "standalone",
  ...(isLocalApi() ? { rewrites } : {}),
  images: {
    ...(isLocalApi() ? { dangerouslyAllowLocalIP: true } : {}),
    remotePatterns: remotePatterns(),
  },
};

export default nextConfig;
