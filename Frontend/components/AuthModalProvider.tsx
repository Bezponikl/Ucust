"use client";

import { createContext, useContext, useState, type ReactNode } from "react";
import LoginModal from "./LoginModal";
import SignupModal from "./SignupModal";

type AuthView = "login" | "signup" | null;

interface AuthModalContextValue {
  openLogin: () => void;
  openSignup: () => void;
  close: () => void;
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
  const [view, setView] = useState<AuthView>(null);

  const value: AuthModalContextValue = {
    openLogin: () => setView("login"),
    openSignup: () => setView("signup"),
    close: () => setView(null),
  };

  return (
    <AuthModalContext.Provider value={value}>
      {children}
      <LoginModal
        open={view === "login"}
        onClose={() => setView(null)}
        onSwitchToSignup={() => setView("signup")}
      />
      <SignupModal
        open={view === "signup"}
        onClose={() => setView(null)}
        onSwitchToLogin={() => setView("login")}
      />
    </AuthModalContext.Provider>
  );
}
