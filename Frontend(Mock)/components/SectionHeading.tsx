import type { ReactNode } from "react";
import Reveal from "./Reveal";

/**
 * Единый стиль заголовков секций лендинга: жирный ink-заголовок с одним
 * словом-акцентом в фирменном градиенте (span.accent-gradient). Один размер
 * везде — чтобы все секции звучали в одном ритме (приём Apple / референс Poe).
 */
export default function SectionHeading({
  kicker,
  children,
  subtitle,
  align = "left",
  className = "",
}: {
  kicker?: string;
  children: ReactNode;
  subtitle?: ReactNode;
  align?: "left" | "center";
  className?: string;
}) {
  const center = align === "center";
  return (
    <Reveal className={className}>
      {kicker && (
        <p className={`kicker mb-4 text-xs text-brand sm:text-sm ${center ? "text-center" : ""}`}>
          {kicker}
        </p>
      )}
      <h2
        className={`text-3xl font-bold leading-tight tracking-tight text-ink sm:text-4xl ${
          center ? "mx-auto max-w-3xl text-center" : "max-w-2xl"
        }`}
      >
        {children}
      </h2>
      {subtitle && (
        <p
          className={`mt-4 text-base leading-relaxed text-ink-muted sm:text-lg ${
            center ? "mx-auto max-w-xl text-center" : "max-w-xl"
          }`}
        >
          {subtitle}
        </p>
      )}
    </Reveal>
  );
}
