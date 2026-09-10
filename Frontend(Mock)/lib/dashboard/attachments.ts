"use client";

import { useCallback, useEffect, useRef, useState } from "react";

/** Фото, приложенное к запросу для нейросети (контекст, а не медиа публикации). */
export interface Attachment {
  id: string;
  url: string;
  name: string;
}

export const MAX_ATTACHMENTS = 4;

/**
 * Вложения к текстовому запросу: хранит object URL'ы и освобождает их при размонтировании.
 * Возвращает готовые обработчики для PromptComposer.
 */
export function useAttachments(max = MAX_ATTACHMENTS) {
  const [items, setItems] = useState<Attachment[]>([]);
  const urls = useRef<string[]>([]);

  useEffect(() => {
    const created = urls.current;
    return () => created.forEach((u) => URL.revokeObjectURL(u));
  }, []);

  const add = useCallback(
    (files: File[]) => {
      setItems((prev) => {
        const room = max - prev.length;
        if (room <= 0) return prev;
        const next = files.slice(0, room).map((f, i) => {
          const url = URL.createObjectURL(f);
          urls.current.push(url);
          return { id: `${f.name}-${prev.length + i}-${f.size}`, url, name: f.name };
        });
        return [...prev, ...next];
      });
    },
    [max],
  );

  const remove = useCallback((id: string) => {
    setItems((prev) => prev.filter((x) => x.id !== id));
  }, []);

  const clear = useCallback(() => setItems([]), []);

  return { items, add, remove, clear, max };
}
