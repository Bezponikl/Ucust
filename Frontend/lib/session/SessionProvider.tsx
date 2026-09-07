"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { login as apiLogin, logout as apiLogout, refresh } from "@/lib/api/auth";
import { getMe } from "@/lib/api/users";
import type { ProfileResponse } from "@/lib/api/types";

type Status = "loading" | "authenticated" | "anonymous";

interface SessionValue {
  user: ProfileResponse | null;
  status: Status;
  signIn: (email: string, password: string, rememberMe?: boolean) => Promise<void>;
  signOut: () => Promise<void>;
  reload: () => Promise<void>;
}

const SessionContext = createContext<SessionValue | null>(null);

export function SessionProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<ProfileResponse | null>(null);
  const [status, setStatus] = useState<Status>("loading");

  const reload = useCallback(async () => {
    try {
      setUser(await getMe());
      setStatus("authenticated");
    } catch {
      setUser(null);
      setStatus("anonymous");
    }
  }, []);

  useEffect(() => {
    // Access-токен живёт в памяти и умирает при перезагрузке страницы,
    // поэтому сессию восстанавливаем по httpOnly-куке.
    (async () => {
      const token = await refresh();
      if (token) await reload();
      else setStatus("anonymous");
    })();
  }, [reload]);

  const signIn = useCallback(
    async (email: string, password: string, rememberMe?: boolean) => {
      await apiLogin({ email, password, rememberMe });
      await reload();
    },
    [reload],
  );

  const signOut = useCallback(async () => {
    await apiLogout();
    setUser(null);
    setStatus("anonymous");
  }, []);

  const value = useMemo(
    () => ({ user, status, signIn, signOut, reload }),
    [user, status, signIn, signOut, reload],
  );

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession(): SessionValue {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error("useSession вызван вне SessionProvider");
  return ctx;
}
