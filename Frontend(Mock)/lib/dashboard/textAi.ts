import type { IconName } from "@/lib/icons/solar";

/**
 * Действия ИИ над текстом публикации — один список на создание и редактирование.
 * Меню касается только текста: медиа меняется своими кнопками у изображения.
 */
export interface TextAiAction {
  key: string;
  label: string;
  icon: IconName;
}

export const TEXT_AI_ACTIONS: TextAiAction[] = [
  { key: "improve", label: "Улучшить текст", icon: "sparkles" },
  { key: "short", label: "Сделать короче", icon: "arrow-up" },
  { key: "long", label: "Сделать длиннее", icon: "plus" },
  { key: "sell", label: "Сделать продающим", icon: "trending" },
  { key: "warm", label: "Сделать дружелюбнее", icon: "heart" },
  { key: "cta", label: "Добавить призыв к действию", icon: "megaphone" },
  { key: "fix", label: "Исправить ошибки", icon: "check-bold" },
  { key: "rewrite", label: "Переписать полностью", icon: "refresh" },
];

// Мок «отполированных» вариантов: в проде здесь ответ модели.
const POLISHED = [
  "Заходите на чашечку ароматного кофе — у нас тепло, уютно и всегда рады гостям ☕",
  "Начните день с любимого напитка. Готовим с заботой специально для вас!",
  "Свежая обжарка, домашняя выпечка и хорошее настроение — всё это ждёт вас сегодня.",
  "Немного тепла в каждой чашке. Приходите за отличным кофе и уютной атмосферой ✨",
];

/** Применяет действие к тексту. `note` — короткое подтверждение для тоста. */
export function applyTextAi(key: string, text: string): { text: string; note?: string } {
  const trimmed = text.trim();
  const paras = text.split("\n\n");

  switch (key) {
    case "improve": {
      const i = POLISHED.indexOf(trimmed);
      if (i >= 0) return { text: POLISHED[(i + 1) % POLISHED.length] };
      return { text: `${trimmed}\n\nЗаходите — будем рады каждому гостю ☕` };
    }
    case "short":
      return { text: [paras[0], paras[paras.length - 1]].filter(Boolean).join("\n\n") };
    case "long":
      return { text: `${text}\n\nА ещё вас ждёт уютная атмосфера, любимая музыка и аромат свежей обжарки — идеальный повод сделать паузу в течение дня.` };
    case "sell":
      return { text: `🔥 Только сейчас!\n\n${text}` };
    case "warm":
      return { text: `${text}\n\nБудем рады каждому — обнимаем 🤗` };
    case "cta":
      return { text: `${text}\n\n👉 Забронируйте столик или просто загляните к нам на чашечку кофе!` };
    case "fix":
      return { text, note: "Готово — текст проверен, ошибок не найдено" };
    case "rewrite":
      return { text: `✨ Небольшая история для вас.\n\n${paras[1] ?? text}\n\nЗаходите — будем рады встрече!` };
    default:
      return { text };
  }
}
