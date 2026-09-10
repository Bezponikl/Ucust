"use client";

import { useEffect, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { AnimatePresence, motion } from "framer-motion";
import Icon from "@/components/ui/Icon";

export default function ModalShell({
  open,
  onClose,
  labelledBy,
  aside,
  children,
}: {
  open: boolean;
  onClose: () => void;
  labelledBy: string;
  /** Брендовая панель слева (десктоп). Если передана — модалка широкая, в две колонки. */
  aside?: ReactNode;
  children: ReactNode;
}) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!open) return;

    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };

    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [open, onClose]);

  if (!mounted) return null;

  const wide = Boolean(aside);

  return createPortal(
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={onClose}
            aria-hidden="true"
            className="absolute inset-0 bg-ink/40 backdrop-blur-sm"
          />

          <motion.div
            role="dialog"
            aria-modal="true"
            aria-labelledby={labelledBy}
            initial={{ opacity: 0, scale: 0.96, y: 16 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: 16 }}
            transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
            className={`relative max-h-[92vh] w-full overflow-hidden rounded-[28px] bg-card shadow-lift ${
              wide ? "max-w-4xl" : "max-w-md"
            }`}
          >
            <button
              type="button"
              onClick={onClose}
              aria-label="Закрыть"
              className="absolute right-4 top-4 z-20 flex h-9 w-9 items-center justify-center rounded-full bg-white/60 text-ink-muted backdrop-blur transition-colors hover:bg-surface-soft hover:text-ink dark:bg-white/10 dark:hover:bg-white/15"
            >
              <Icon name="close" size={20} aria-hidden="true" />
            </button>

            {wide ? (
              <div className="grid lg:grid-cols-[0.92fr_1fr]">
                <aside className="relative hidden overflow-hidden bg-gradient-to-br from-hero-from via-hero-via to-hero-to p-9 text-white lg:flex lg:flex-col xl:p-10">
                  <div
                    aria-hidden="true"
                    className="pointer-events-none absolute inset-0 overflow-hidden"
                  >
                    <div className="absolute -left-16 -top-16 h-64 w-64 rotate-[18deg] rounded-[56px] bg-[var(--hero-chevron)]" />
                    <div className="absolute -bottom-20 -right-12 h-56 w-56 rounded-full bg-[var(--hero-chevron-soft)] blur-2xl" />
                  </div>
                  <div className="relative flex h-full flex-col">{aside}</div>
                </aside>

                <div className="max-h-[92vh] overflow-y-auto p-7 sm:p-10">
                  {children}
                </div>
              </div>
            ) : (
              <div className="max-h-[92vh] overflow-y-auto p-7 sm:p-8">{children}</div>
            )}
          </motion.div>
        </div>
      )}
    </AnimatePresence>,
    document.body
  );
}
