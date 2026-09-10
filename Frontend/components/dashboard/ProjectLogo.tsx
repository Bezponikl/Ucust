"use client";

import { useState } from "react";
import Image from "next/image";

/**
 * Логотип проекта с заглушкой. Пока картинки нет — первая буква названия
 * (цвет/фон задаёт родитель). Если ссылка битая — например MinIO не отдаёт
 * файл браузеру, — onError переводит на ту же заглушку, битой иконки не видно.
 * Запомненные битые адреса не «оживают» при повторном рендере.
 */
export default function ProjectLogo({
  src,
  name,
  fill = false,
  unoptimized = true,
  className,
  letterClassName,
  alt = "",
}: {
  src?: string | null;
  name: string;
  fill?: boolean;
  unoptimized?: boolean;
  className?: string;
  letterClassName?: string;
  alt?: string;
}) {
  const [failed, setFailed] = useState<Record<string, boolean>>({});

  if (!src || failed[src]) {
    return <span className={letterClassName}>{name.trim().slice(0, 1).toUpperCase() || "U"}</span>;
  }

  const onError = () => setFailed((f) => (f[src] ? f : { ...f, [src]: true }));

  return fill ? (
    <Image src={src} alt={alt} fill unoptimized={unoptimized} onError={onError} className={`object-cover ${className ?? ""}`} />
  ) : (
    <Image src={src} alt={alt} width={64} height={64} unoptimized={unoptimized} onError={onError} className={`object-cover ${className ?? ""}`} />
  );
}