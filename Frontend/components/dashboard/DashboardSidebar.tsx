"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import Icon from "../ui/Icon";
import ProjectSwitcher from "./ProjectSwitcher";
import { LOCKED_HINT, NAV_ITEMS, isNavActive, requiresProject } from "./nav";
import { useDashboard } from "./DashboardProvider";

export default function DashboardSidebar() {
  const pathname = usePathname();
  const { surfaceStyle, data, hasProject } = useDashboard();
  const businessName = data?.businessName ?? "Ваш бизнес";
  const businessInitial = businessName.slice(0, 1).toUpperCase();
  const [collapsed, setCollapsed] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    try {
      if (localStorage.getItem("uc_sidebar") === "collapsed") setCollapsed(true);
    } catch {}
  }, []);

  const toggle = () => {
    const next = !collapsed;
    setCollapsed(next);
    try { localStorage.setItem("uc_sidebar", next ? "collapsed" : "expanded"); } catch {}
  };

  const w = collapsed ? "w-14" : "w-72";

  return (
    <aside
      className={`hidden lg:flex h-full flex-col border-r border-border/40 ${surfaceStyle === "glass" ? "bg-card/80 dark:bg-card/62 backdrop-blur-2xl" : "bg-card"} transition-[width] duration-200 shrink-0 ${w}`}
      style={{ minWidth: collapsed ? 56 : 288 }}
    >
      {/* Логотип + проект */}
      <div className={`flex h-16 shrink-0 items-center border-b border-border/40 ${collapsed ? "justify-center px-3" : "px-4"}`}>
        {collapsed ? (
          <Link
            href="/dashboard"
            title={businessName}
            aria-label={`${businessName} — на главную дашборда`}
            className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-tint text-sm font-bold text-brand transition hover:brightness-95"
          >
            {businessInitial}
          </Link>
        ) : (
          <div className="min-w-0 flex-1">
            {mounted && <ProjectSwitcher />}
          </div>
        )}
      </div>

      {/* Навигация */}
      <nav className="flex-1 overflow-y-auto overflow-x-hidden py-3 px-2.5 flex flex-col gap-0.5">
        {NAV_ITEMS.map((item) => {
          const active = isNavActive(pathname, item.href);
          const locked = !hasProject && requiresProject(item.href);

          if (locked) {
            return (
              <span
                key={item.href}
                aria-disabled="true"
                title={collapsed ? `${item.label} — ${LOCKED_HINT}` : LOCKED_HINT}
                className={`flex min-h-11 cursor-not-allowed items-center gap-3 rounded-2xl px-3 py-3 text-sm font-medium text-ink-muted/45 ${
                  collapsed ? "justify-center" : ""
                }`}
              >
                <Icon name={item.icon} size={20} aria-hidden="true" className="shrink-0" />
                {!collapsed && (
                  <>
                    <span className="truncate">{item.label}</span>
                    <Icon name="lock" size={14} aria-hidden="true" className="ml-auto shrink-0" />
                  </>
                )}
              </span>
            );
          }

          return (
            <Link
              key={item.href}
              href={item.href}
              data-tour={item.tourId}
              aria-current={active ? "page" : undefined}
              title={collapsed ? item.label : undefined}
              className={`flex min-h-11 items-center gap-3 rounded-2xl px-3 py-3 text-sm font-medium transition-colors ${
                active
                  ? "bg-brand/10 text-brand"
                  : "text-ink-muted hover:bg-surface-soft hover:text-ink"
              } ${collapsed ? "justify-center" : ""}`}
            >
              <Icon name={item.icon} size={20} aria-hidden="true" className="shrink-0" />
              {!collapsed && <span className="truncate">{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Нижняя секция: настройки + свернуть */}
      <div className="shrink-0 border-t border-border/40 p-2.5 flex flex-col gap-0.5">
        {hasProject ? (
          <Link
            href="/dashboard/business"
            title={collapsed ? "Настройки бизнеса" : undefined}
            className={`flex min-h-11 items-center gap-3 rounded-2xl px-3 py-3 text-sm font-medium text-ink-muted transition-colors hover:bg-surface-soft hover:text-ink ${
              collapsed ? "justify-center" : ""
            }`}
          >
            <Icon name="settings" size={20} aria-hidden="true" className="shrink-0" />
            {!collapsed && <span className="truncate">Настройки бизнеса</span>}
          </Link>
        ) : (
          <span
            aria-disabled="true"
            title={collapsed ? `Настройки бизнеса — ${LOCKED_HINT}` : LOCKED_HINT}
            className={`flex min-h-11 cursor-not-allowed items-center gap-3 rounded-2xl px-3 py-3 text-sm font-medium text-ink-muted/45 ${
              collapsed ? "justify-center" : ""
            }`}
          >
            <Icon name="settings" size={20} aria-hidden="true" className="shrink-0" />
            {!collapsed && (
              <>
                <span className="truncate">Настройки бизнеса</span>
                <Icon name="lock" size={14} aria-hidden="true" className="ml-auto shrink-0" />
              </>
            )}
          </span>
        )}

        <button
          type="button"
          onClick={toggle}
          title={collapsed ? "Развернуть меню" : undefined}
          className={`flex min-h-11 w-full items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium text-ink-muted transition-colors hover:bg-surface-soft hover:text-ink ${
            collapsed ? "justify-center" : ""
          }`}
        >
          <Icon name={collapsed ? "arrow-right" : "arrow-left"} size={20} aria-hidden="true" className="shrink-0" />
          {!collapsed && <span className="truncate">Скрыть меню</span>}
        </button>
      </div>
    </aside>
  );
}
