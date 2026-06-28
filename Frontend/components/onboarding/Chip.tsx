import { X } from "lucide-react";
import type { ReactNode } from "react";

const COLORS = {
  brand: "bg-brand/12 text-brand",
  purple: "bg-brand-purple/15 text-brand-purple",
  pink: "bg-brand-pink/15 text-brand-pink",
  orange: "bg-brand-orange/15 text-brand-orange",
  success: "bg-success/15 text-success",
} as const;

export default function Chip({
  children,
  color = "brand",
  onRemove,
}: {
  children: ReactNode;
  color?: keyof typeof COLORS;
  onRemove?: () => void;
}) {
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ${COLORS[color]}`}>
      {children}
      {onRemove && (
        <button type="button" onClick={onRemove} aria-label="Удалить" className="opacity-70 hover:opacity-100">
          <X size={12} aria-hidden="true" />
        </button>
      )}
    </span>
  );
}
