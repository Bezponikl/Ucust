"use client";

import dynamic from "next/dynamic";

// Клиентский слой mesh-шейдера: монтируется после гидрации (ssr:false),
// чтобы не ловить hydration mismatch. Переиспользуется в Hero и Footer.
const ShaderBackground = dynamic(
  () => import("./hero-shader").then((m) => m.ShaderBackground),
  {
    ssr: false,
    loading: () => <div className="absolute inset-0 bg-brand/10" />,
  }
);

export default function ShaderLayer({ className = "" }: { className?: string }) {
  return (
    <div aria-hidden className={className}>
      <ShaderBackground />
    </div>
  );
}
