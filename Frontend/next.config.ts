import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Скрываем dev-индикатор Next.js (кружок «N» в углу) — только в разработке.
  devIndicators: false,
  images: {
    unoptimized: true,
  },
  async rewrites() {
    return [
      {
        source: "/api/v1/ai/:path*",
        destination: "http://127.0.0.1:8000/api/v1/ai/:path*",
      },
      {
        source: "/output/:path*",
        destination: "http://127.0.0.1:8000/output/:path*",
      },
    ];
  },
};

export default nextConfig;
