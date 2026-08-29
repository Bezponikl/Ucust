import type { Metadata } from "next";
import type { ReactNode } from "react";
import AuthGuard from "@/components/auth/AuthGuard";
import { DashboardProvider } from "@/components/dashboard/DashboardProvider";
import DashboardShell from "@/components/dashboard/DashboardShell";

export const metadata: Metadata = { robots: { index: false, follow: true } };

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <AuthGuard>
      <DashboardProvider>
        <DashboardShell>{children}</DashboardShell>
      </DashboardProvider>
    </AuthGuard>
  );
}
