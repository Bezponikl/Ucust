"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import Icon from "../ui/Icon";
import { LOCKED_HINT, NAV_ITEMS, isNavActive, requiresProject } from "./nav";
import { useDashboard } from "./DashboardProvider";

export default function DashboardBottomNav() {
  const pathname = usePathname();
  const { mobileChromeHidden, surfaceStyle, hasProject } = useDashboard();
  const surfaceClass =
    surfaceStyle === "glass"
      ? "border-white/10 bg-card/70 ring-1 ring-white/5 backdrop-blur-xl"
      : "border-border bg-card";
  return (
    <nav className={`fixed inset-x-3 bottom-[calc(0.6rem+env(safe-area-inset-bottom))] z-40 items-stretch gap-1 rounded-[24px] border p-1.5 shadow-lift lg:hidden ${surfaceClass} ${mobileChromeHidden ? "hidden" : "flex"}`}>
      {NAV_ITEMS.map(({ href, label, icon, tourId }) => {
        const active = isNavActive(pathname, href);
        const locked = !hasProject && requiresProject(href);

        if (locked) {
          return (
            <span
              key={href}
              aria-disabled="true"
              title={LOCKED_HINT}
              className="relative flex flex-1 cursor-not-allowed flex-col items-center gap-1 rounded-2xl py-2 text-[0.6875rem] font-medium text-ink-muted/40"
            >
              <Icon name={icon} size={20} aria-hidden="true" />
              {label}
              <Icon name="lock" size={11} aria-hidden="true" className="absolute right-1.5 top-1.5" />
            </span>
          );
        }

        return (
          <Link
            key={href}
            href={href}
            data-tour={tourId}
            aria-current={active ? "page" : undefined}
            className={`flex flex-1 flex-col items-center gap-1 rounded-2xl py-2 text-[0.6875rem] font-medium transition ${
              active ? "bg-brand-tint text-brand" : "text-ink-muted"
            }`}
          >
            <Icon name={icon} size={20} aria-hidden="true" />
            {label}
          </Link>
        );
      })}
    </nav>
  );
}
