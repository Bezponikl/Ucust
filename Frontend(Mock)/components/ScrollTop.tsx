"use client";

import { useEffect, useState } from "react";
import Icon from "./ui/Icon";

export default function ScrollTop() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    const onScroll = () => setShow(window.scrollY > 500);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <button
      type="button"
      onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
      aria-label="Наверх"
      className={`btn-glass fixed bottom-6 right-6 z-50 hidden h-12 w-12 items-center justify-center transition-all duration-300 lg:flex ${
        show
          ? "translate-y-0 opacity-100"
          : "pointer-events-none translate-y-3 opacity-0"
      }`}
    >
      <Icon name="arrow-up" size={20} />
    </button>
  );
}
