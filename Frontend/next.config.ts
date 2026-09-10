import type { NextConfig } from "next";

type RemotePattern = NonNullable<NonNullable<NextConfig["images"]>["remotePatterns"]>[number];

/**
 * Шлюз отдаёт ссылки на файлы абсолютными URL того же origin, что и API
 * (логотип проекта, медиа, аватар — `/s3/...`). next/image в этом проекте
 * локальный путь не трогает, но абсолютный URL без remotePatterns режет 400.
 * Разрешаем только наш же origin: локальный localhost:8100 и прод-домен.
 */
function remotePatterns(): RemotePattern[] {
  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api/v0";
  // Относительный путь = фронт и шлюз за одним nginx, remote-картинок нет.
  if (!apiBase.startsWith("http://") && !apiBase.startsWith("https://")) return [];

  try {
    const origin = new URL(apiBase);
    return [
      {
        protocol: origin.protocol === "https:" ? "https" : "http",
        hostname: origin.hostname,
        port: origin.port,
        pathname: "/**",
        search: "",
      },
    ];
  } catch {
    // Битый адрес из .env.local не должен ронять сборку.
    return [];
  }
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

const nextConfig: NextConfig = {
  // Скрываем dev-индикатор Next.js (кружок «N» в углу) — только в разработке.
  devIndicators: false,
  // Отдельный сервер для Docker: .next/standalone + public + static копируются
  // в образ и запускаются одним процессом без установки node_modules.
  output: "standalone",
  images: {
    ...(isLocalApi() ? { dangerouslyAllowLocalIP: true } : {}),
    remotePatterns: remotePatterns(),
  },
};

export default nextConfig;
