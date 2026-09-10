import type { ChannelId } from "@/lib/channels";
import { isoOffset, parseRuShort } from "@/lib/dashboard/date";
import type { Promo, PromoStatus, PromoType } from "@/lib/dashboard/promos";

/** Черновик акции — всё, что редактируется на пяти вкладках. */
export interface PromoDraft {
  // Информация
  title: string;
  description: string;
  type: PromoType;
  discount: string;
  hasCode: boolean;
  code: string;
  dateFrom: string; // ISO
  dateTo: string;   // ISO
  timeStart: string; // «ЧЧ:ММ»
  goal: string;
  status: PromoStatus;

  // Механика — показываем только поля выбранного типа
  minOrder: string;
  giftItem: string;
  giftCondition: string;
  eventPlace: string;
  eventCapacity: string;
  codeLimit: string;

  // Контент
  image?: string;
  headline: string;
  subheadline: string;
  bodyText: string;

  // Публикация
  channels: ChannelId[];
  publishDate: string;
  publishTime: string;
}

export function draftFromPromo(p: Promo): PromoDraft {
  const [rawFrom = "", rawTo = ""] = p.period.split("—").map((s) => s.trim());
  const dateFrom = parseRuShort(rawFrom) ?? isoOffset(0);
  const dateTo = parseRuShort(rawTo) ?? isoOffset(14);

  return {
    title: p.title,
    description: p.description,
    type: p.type,
    discount: p.discount ?? "",
    hasCode: Boolean(p.code),
    code: p.code ?? "",
    dateFrom,
    dateTo,
    timeStart: "10:00",
    goal: p.goal?.toString() ?? "",
    status: p.status,

    minOrder: "",
    giftItem: p.type === "gift" ? "Второй напиток" : "",
    giftCondition: p.type === "gift" ? "При покупке любого напитка" : "",
    eventPlace: p.type === "event" ? "Кофейня на Немиге" : "",
    eventCapacity: "",
    codeLimit: "",

    image: p.image,
    headline: p.title,
    subheadline: p.discount ? `${p.discount} на всё меню` : "",
    bodyText: p.description,

    channels: p.channels,
    publishDate: dateFrom,
    publishTime: "10:00",
  };
}
