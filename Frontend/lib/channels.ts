export type ChannelId =
  | "vk"
  | "telegram"
  | "max"
  | "ok"
  | "instagram"
  | "whatsapp"
  | "zen"
  | "rutube"
  | "avito";

export interface ChannelMeta {
  id: ChannelId;
  label: string;
  short: string;
  colorVar: string;
  icon?: string;
  iconType?: "square" | "wordmark";
}

export const CHANNELS: Record<ChannelId, ChannelMeta> = {
  vk: { id: "vk", label: "VK", short: "VK", colorVar: "var(--channel-vk)", icon: "/vk.png" },
  telegram: {
    id: "telegram",
    label: "Telegram",
    short: "TG",
    colorVar: "var(--channel-telegram)",
    icon: "/telegram.png",
  },
  max: {
    id: "max",
    label: "MAX",
    short: "MAX",
    colorVar: "var(--channel-max)",
    icon: "/max.png",
  },
  ok: {
    id: "ok",
    label: "Одноклассники",
    short: "OK",
    colorVar: "var(--channel-ok)",
    icon: "/ok.png",
  },
  instagram: {
    id: "instagram",
    label: "Instagram",
    short: "IG",
    colorVar: "var(--channel-rutube)",
    icon: "/instagram.png",
  },
  whatsapp: {
    id: "whatsapp",
    label: "WhatsApp",
    short: "WA",
    colorVar: "var(--channel-whatsapp)",
    icon: "/whatsapp.png",
  },
  zen: {
    id: "zen",
    label: "Дзен",
    short: "Дзен",
    colorVar: "var(--channel-zen)",
    icon: "/zen.png",
  },
  rutube: {
    id: "rutube",
    label: "RuTube",
    short: "RT",
    colorVar: "var(--channel-rutube)",
    icon: "/rutube.png",
    iconType: "wordmark",
  },
  avito: {
    id: "avito",
    label: "Авито",
    short: "АВ",
    colorVar: "var(--channel-avito)",
    icon: "/avito.png",
    iconType: "wordmark",
  },
};

export const CHANNEL_ORDER: ChannelId[] = [
  "vk",
  "telegram",
  "max",
  "ok",
  "instagram",
  "whatsapp",
  "zen",
  "rutube",
  "avito",
];
