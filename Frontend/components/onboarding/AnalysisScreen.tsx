"use client";

import { useEffect } from "react";
import { Sparkles } from "lucide-react";
import { motion } from "framer-motion";

export default function AnalysisScreen({ onDone }: { onDone: () => void }) {
  useEffect(() => {
    const t = setTimeout(onDone, 2600);
    return () => clearTimeout(t);
  }, [onDone]);

  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <motion.span
        className="mb-5 text-brand"
        animate={{ scale: [1, 1.15, 1], opacity: [0.7, 1, 0.7] }}
        transition={{ duration: 1.6, repeat: Infinity, ease: "easeInOut" }}
      >
        <Sparkles size={44} aria-hidden="true" />
      </motion.span>
      <h1 className="text-2xl font-bold text-ink sm:text-3xl">Анализируем ваш бизнес</h1>
      <p className="mt-2 text-sm text-ink-muted">Это займёт несколько секунд…</p>
      <div className="mt-6 h-1.5 w-64 overflow-hidden rounded-full bg-border">
        <motion.div
          className="h-full rounded-full bg-brand"
          initial={{ width: "5%" }}
          animate={{ width: "100%" }}
          transition={{ duration: 2.5, ease: "easeInOut" }}
        />
      </div>
    </div>
  );
}
