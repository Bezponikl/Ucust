import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Скрываем dev-индикатор Next.js (кружок «N» в углу) — только в разработке.
  devIndicators: false,
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
