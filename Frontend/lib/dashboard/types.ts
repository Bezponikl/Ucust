import type { ChannelId } from "@/lib/channels";
import type { IconName } from "@/lib/icons/solar";

/** Проект в переключателе: имя и аватар показываются без чтения brandProfile каждого. */
export interface ProjectListItem {
  id: string;
  name: string;
  logo: string | null;
}

export type AccentColor = "brand" | "purple" | "pink" | "orange" | "success";
export type StatIcon = "views" | "engagement" | "subscribers" | "reviews";

export interface Stat {
  id: string;
  label: string;
  value: string;
  hint: string;
  delta?: string;
  icon: StatIcon;
  color: AccentColor;
  hintTone?: "warning";
  sparkline?: number[];
}

export type ChartTab = "reach" | "engagement" | "clicks";

export interface AiTip {
  id: string;
  title: string;
  text: string;
  color: AccentColor;
  href: string;
  /** Иконка по смыслу совета — одинаковые значки сливались в один ряд. */
  icon: IconName;
}

export type PostStatus = "published" | "scheduled" | "draft" | "none";

export interface PlanDay {
  weekday: string;
  day: number;
  status: PostStatus;
  channels: ChannelId[];
}

export interface ActivityItem {
  id: string;
  text: string;
  time: string;
  color: AccentColor;
}

export interface DashboardData {
  businessName: string | null;
  /** Аватар проекта с сервера /s3/... — null, когда логотипа нет. */
  businessLogo: string | null;
  /** Все проекты аккаунта для переключателя. */
  projects: ProjectListItem[];
  stats: Stat[];
  chart: Record<ChartTab, number[]>;
  tips: AiTip[];
  week: PlanDay[];
  activity: ActivityItem[];
}
