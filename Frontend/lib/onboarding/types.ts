import type { ChannelId } from "@/lib/channels";

export type AboutMode = "link" | "manual";

/** Файл с реальным содержимым (data-URL) для отправки в AI-анализ бизнеса. */
export interface UploadedFile {
  name: string;
  dataUrl: string;
}

export interface WizardInput {
  name: string;
  aboutMode: AboutMode;
  link: string;
  activity: string;
  difference: string;
  socials: ChannelId[];
  /** Введённые пользователем @хэндлы/ссылки подключённых соцсетей. */
  channelHandles: Partial<Record<ChannelId, string>>;
  /** Имена прикреплённых документов — только для отображения в UI. */
  files: string[];
  /** Прикреплённые документы с содержимым (data-URL, до 2 МБ), уходят в анализ. */
  fileData: UploadedFile[];
}

export interface MarketInfo {
  competitors: string[];
  geography: string;
  segment: string;
  trends: string[];
}

export interface SwotInfo {
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  threats: string[];
}

export interface ServiceItem {
  title: string;
  items: string;
}

export interface BrandProfile {
  name: string;
  field: string;
  positioning: string;
  market: MarketInfo;
  swot: SwotInfo;
  services: ServiceItem[];
  goals: string[];
  tone: string[];
}

export const EMPTY_INPUT: WizardInput = {
  name: "",
  aboutMode: "link",
  link: "",
  activity: "",
  difference: "",
  socials: [],
  channelHandles: {},
  files: [],
  fileData: [],
};
