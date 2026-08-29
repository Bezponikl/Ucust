"use client";

import { useEffect, useState } from "react";
import Icon from "./Icon";
import { subscribeToast } from "@/lib/toast";

type Item = { id: number; msg: string };

export default function Toaster() {
  const [items, setItems] = useState<Item[]>([]);

  useEffect(
    () =>
      subscribeToast((msg) => {
        const id = Date.now() + Math.random();
        setItems((x) => [...x, { id, msg }]);
        setTimeout(() => setItems((x) => x.filter((i) => i.id !== id)), 2600);
      }),
    []
  );

  return (
    <div className="pointer-events-none fixed bottom-24 left-1/2 z-[100] flex -translate-x-1/2 flex-col items-center gap-2 lg:bottom-6">
      {items.map((i) => (
        <div
          key={i.id}
          className="uc-fade-in pointer-events-auto flex items-center gap-2 rounded-full border border-border bg-card px-4 py-2.5 text-sm font-medium text-ink shadow-lift"
        >
          <Icon name="check-bold" size={15} className="text-brand" aria-hidden="true" />
          {i.msg}
        </div>
      ))}
    </div>
  );
}
