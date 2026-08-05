"use client";

import { useEffect, useState } from "react";
import Icon from "./ui/Icon";

export default function ThemeToggle({ className = "", glass = true }: { className?: string; glass?: boolean }) {
  const [dark, setDark] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    setDark(document.documentElement.classList.contains("dark"));
  }, []);

  const toggle = () => {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.toggle("dark", next);
    try {
      localStorage.setItem("theme", next ? "dark" : "light");
    } catch {}
  };

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={dark ? "Светлая тема" : "Тёмная тема"}
      className={`${glass ? "btn-glass" : "btn-solid"} flex h-9 w-9 items-center justify-center ${className}`}
    >
      {/* до монтирования рендерим нейтральную иконку, чтобы избежать рассинхрона гидрации */}
      {mounted && dark ? (
        <Icon name="sun" size={17} />
      ) : (
        <Icon name="moon" size={17} />
      )}
    </button>
  );
}
