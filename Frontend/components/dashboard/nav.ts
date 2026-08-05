import type { IconName } from "@/lib/icons/solar";

export interface NavChild {
  href: string;
  label: string;
}

export interface NavItem {
  href: string;
  label: string;
  icon: IconName;
  children?: NavChild[];
  /** Якорь для интерактивных подсказок, см. lib/dashboard/tour.ts */
  tourId?: string;
}

export const NAV_ITEMS: NavItem[] = [
  { href: "/dashboard", label: "Дашборд", icon: "dashboard", tourId: "nav-home" },
  { href: "/dashboard/content", label: "Контент", icon: "file-text", tourId: "nav-content" },
  { href: "/dashboard/inbox", label: "Входящие", icon: "message", tourId: "nav-inbox" },
  { href: "/dashboard/promos", label: "Акции", icon: "gift", tourId: "nav-promos" },
  { href: "/dashboard/analytics", label: "Аналитика", icon: "bar-chart", tourId: "nav-analytics" },
];

// Пути, которые «принадлежат» секции (для подсветки родителя)
const ITEM_PATHS: Record<string, string[]> = {
  "/dashboard/content": ["/dashboard/content", "/dashboard/create"],
  "/dashboard/promos":  ["/dashboard/promos",  "/dashboard/promos/create"],
};

/** Разделы, которые появляются только вместе с проектом («мозгом бренда»). */
const PROJECT_PREFIXES = [
  "/dashboard/content",
  "/dashboard/create",
  "/dashboard/inbox",
  "/dashboard/promos",
  "/dashboard/analytics",
  "/dashboard/reviews",
  "/dashboard/business",
];

/** До создания проекта такие пути закрыты: показывать там нечего. */
export function requiresProject(href: string): boolean {
  return PROJECT_PREFIXES.some((p) => href === p || href.startsWith(p + "/"));
}

export const LOCKED_HINT = "Доступно после создания профиля проекта";

export function isNavActive(pathname: string, href: string): boolean {
  const paths = ITEM_PATHS[href];
  if (paths) return paths.some((p) => pathname === p || pathname.startsWith(p + "?") || pathname.startsWith(p + "/"));
  return href === "/dashboard" ? pathname === "/dashboard" : pathname.startsWith(href);
}
