"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Icon from "./ui/Icon";
import { loadOnboarding } from "@/lib/onboarding/storage";

// Возврат со страницы «О нас»: авторизованного (есть сессия онбординга) — в дашборд, иначе — на лендинг.
export default function AboutBackLink() {
  const [authed, setAuthed] = useState(false);

  useEffect(() => {
    /* eslint-disable react-hooks/set-state-in-effect */
    setAuthed(Boolean(loadOnboarding()));
    /* eslint-enable react-hooks/set-state-in-effect */
  }, []);

  const href = authed ? "/dashboard" : "/";
  const label = authed ? "В дашборд" : "На главную";

  return (
    <Link href={href} className="inline-flex items-center gap-1.5 text-sm font-medium text-ink-muted transition-colors hover:text-brand">
      <Icon name="arrow-left" size={16} aria-hidden="true" /> {label}
    </Link>
  );
}
