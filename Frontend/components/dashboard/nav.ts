import { LayoutDashboard, FileText, Gift, Star, BarChart3, type LucideIcon } from "lucide-react";

export interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
}

export const NAV_ITEMS: NavItem[] = [
  { href: "/dashboard", label: "Дашборд", icon: LayoutDashboard },
  { href: "/dashboard/content", label: "Контент", icon: FileText },
  { href: "/dashboard/promos", label: "Акции", icon: Gift },
  { href: "/dashboard/reviews", label: "Отзывы", icon: Star },
  { href: "/dashboard/analytics", label: "Аналитика", icon: BarChart3 },
];

// /dashboard активен только при точном совпадении (он префикс всех остальных).
export function isNavActive(pathname: string, href: string): boolean {
  return href === "/dashboard" ? pathname === "/dashboard" : pathname.startsWith(href);
}
