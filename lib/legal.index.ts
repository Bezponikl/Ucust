// АВТОГЕНЕРАЦИЯ — не редактировать вручную. Пересобрать: node scripts/build-legal.mjs

export interface LegalLink {
  slug: string;
  title: string;
  short: string;
  desc: string;
}

export const LEGAL_UPDATED = "27 августа 2026 г.";
export const LEGAL_COMPANY = "ООО «ЕТА СОФТ ГРУПП»";
export const LEGAL_EMAIL = "ucust@yandex.ru";

export const LEGAL_INDEX: LegalLink[] = [
  {
    "slug": "offer",
    "title": "Публичная оферта",
    "short": "Оферта",
    "desc": "Условия платного доступа: тарифы, оплата, автопродление и возврат средств."
  },
  {
    "slug": "terms",
    "title": "Пользовательское соглашение",
    "short": "Соглашение",
    "desc": "Правила работы с сервисом: регистрация, права сторон, ИИ-инструменты, контент."
  },
  {
    "slug": "privacy",
    "title": "Политика конфиденциальности",
    "short": "Конфиденциальность",
    "desc": "Какие данные собираем, зачем, где храним и как их защищаем."
  },
  {
    "slug": "pdn-consent",
    "title": "Согласие на обработку персональных данных",
    "short": "Согласие на ПДн",
    "desc": "Перечень данных, цели и способы обработки, срок действия согласия."
  },
  {
    "slug": "cookie",
    "title": "Соглашение об использовании cookie",
    "short": "Cookie",
    "desc": "Какие cookie-файлы используются на сайте и как ими управлять."
  },
  {
    "slug": "marketing-consent",
    "title": "Согласие на рекламную и новостную рассылку",
    "short": "Рассылка",
    "desc": "Условия рассылок и порядок отказа от них."
  }
];
