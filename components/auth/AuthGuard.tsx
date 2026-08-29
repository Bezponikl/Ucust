"use client";

import { useEffect, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "@/lib/session/SessionProvider";

/** Держит неавторизованных вне дашборда. */
export default function AuthGuard({ children }: { children: ReactNode }) {
  const { status } = useSession();
  const router = useRouter();

  const blocked = status === "anonymous";

  useEffect(() => {
    if (blocked) router.replace("/login");
  }, [blocked, router]);

  // Пока сессия восстанавливается по куке, не показываем ни дашборд, ни редирект:
  // иначе пользователь с живой сессией на миг увидит страницу входа.
  if (status === "loading") return null;
  if (blocked) return null;

  return <>{children}</>;
}
