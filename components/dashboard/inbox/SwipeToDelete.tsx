"use client";

import { useRef, useState, type ReactNode } from "react";
import Icon from "@/components/ui/Icon";

/** Ход, после которого свайп считается подтверждённым. */
const COMMIT_PX = 96;
/** Насколько строка может уехать влево. */
const MAX_PX = 120;
/** Порог, ниже которого движение считаем скроллом, а не свайпом. */
const START_PX = 12;

/**
 * Свайп влево по строке списка — удаление, как в Telegram.
 *
 * На мобилке кнопка удаления жила на :hover и была недостижима: пальцем
 * навести нельзя. Здесь строка тянется за пальцем, под ней открывается
 * красная зона, а отпускание за порогом удаляет. Вертикальный скроллинг не
 * перехватываем: пока жест ближе к вертикали, отдаём его списку.
 */
export default function SwipeToDelete({
  onDelete,
  label,
  children,
}: {
  onDelete: () => void;
  /** Подпись для скринридера — что именно удаляем. */
  label: string;
  children: ReactNode;
}) {
  const [dx, setDx] = useState(0);
  const start = useRef<{ x: number; y: number } | null>(null);
  const axis = useRef<"none" | "x" | "y">("none");
  // После свайпа браузер всё равно шлёт click по строке — он бы открыл диалог.
  // Гасим ровно один клик, следующий за горизонтальным жестом.
  const swallowClick = useRef(false);

  const onPointerDown = (e: React.PointerEvent) => {
    // Мышь не трогаем: на десктопе остаётся обычная кнопка удаления.
    if (e.pointerType === "mouse") return;
    start.current = { x: e.clientX, y: e.clientY };
    axis.current = "none";
  };

  const onPointerMove = (e: React.PointerEvent) => {
    if (!start.current) return;
    const deltaX = e.clientX - start.current.x;
    const deltaY = e.clientY - start.current.y;

    if (axis.current === "none") {
      if (Math.abs(deltaX) < START_PX && Math.abs(deltaY) < START_PX) return;
      axis.current = Math.abs(deltaX) > Math.abs(deltaY) ? "x" : "y";
    }
    if (axis.current !== "x") return;

    swallowClick.current = true;
    // Тянем только влево, дальше предела строка не уезжает.
    setDx(Math.max(-MAX_PX, Math.min(0, deltaX)));
  };

  const finish = () => {
    const commit = dx <= -COMMIT_PX;
    setDx(0);
    start.current = null;
    axis.current = "none";
    if (commit) onDelete();
  };

  const onClickCapture = (e: React.MouseEvent) => {
    if (!swallowClick.current) return;
    swallowClick.current = false;
    e.preventDefault();
    e.stopPropagation();
  };

  const armed = dx <= -COMMIT_PX;

  return (
    <div className="relative overflow-hidden rounded-xl">
      {/* Зона удаления открывается по мере сдвига строки */}
      <div
        aria-hidden="true"
        className={`absolute inset-y-0 right-0 flex items-center justify-end pr-4 transition-colors ${
          armed ? "bg-red-500" : "bg-red-500/70"
        }`}
        style={{ width: MAX_PX, opacity: dx < 0 ? 1 : 0 }}
      >
        <Icon name="trash" size={16} className="text-white" />
      </div>

      <div
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={finish}
        onPointerCancel={finish}
        onClickCapture={onClickCapture}
        style={{
          transform: `translateX(${dx}px)`,
          transition: dx === 0 ? "transform 0.18s ease-out" : "none",
          // Разрешаем браузеру вести вертикальный скролл, горизонталь берём себе
          touchAction: "pan-y",
        }}
        className="relative"
      >
        {children}
      </div>

      {/* Тот же путь для клавиатуры и скринридеров: свайп — не единственный способ */}
      <span className="sr-only">
        <button type="button" onClick={onDelete}>
          {label}
        </button>
      </span>
    </div>
  );
}
