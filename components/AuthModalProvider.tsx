"use client";

import { createContext, useContext, type ReactNode } from "react";
import { useRouter } from "next/navigation";

interface AuthModalContextValue {
  openLogin: () => void;
  openSignup: () => void;
}

const AuthModalContext = createContext<AuthModalContextValue | null>(null);

export function useAuthModal() {
  const ctx = useContext(AuthModalContext);
  if (!ctx) {
    throw new Error("useAuthModal must be used within AuthModalProvider");
  }
  return ctx;
}

export default function AuthModalProvider({ children }: { children: ReactNode }) {
  const router = useRouter();

  const value: AuthModalContextValue = {
    openLogin: () => router.push("/login"),
    openSignup: () => router.push("/signup"),
  };

  return <AuthModalContext.Provider value={value}>{children}</AuthModalContext.Provider>;
}
