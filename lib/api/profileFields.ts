/**
 * Правила, которые бэк применяет к профилю, продублированы здесь: без этого
 * пользователь получает сухой 400 уже после отправки формы.
 * Имя и фамилия — только кириллица, телефон — строго 79XXXXXXXXX.
 */

const CYRILLIC_NAME = /^[а-яА-ЯёЁ]+(-[а-яА-ЯёЁ]+)?$/;
const PHONE = /^79[0-9]{9}$/;

/** «+7 900 000-00-00» и «8 (900) 123-45-67» → «79000000000». */
export function normalizePhone(raw: string): string {
  const digits = raw.replace(/\D/g, "");
  if (digits.length !== 11) return raw.trim();
  return digits.startsWith("8") ? `7${digits.slice(1)}` : digits;
}

export interface ProfileFields {
  firstName: string;
  lastName: string;
  phone?: string;
}

/** null — данные корректны; иначе текст ошибки для пользователя. */
export function validateProfileFields({ firstName, lastName, phone }: ProfileFields): string | null {
  if (!CYRILLIC_NAME.test(firstName)) {
    return "Имя — кириллицей, можно с дефисом";
  }
  if (!CYRILLIC_NAME.test(lastName)) {
    return "Фамилия — кириллицей, можно с дефисом";
  }
  if (phone && !PHONE.test(phone)) {
    return "Телефон в формате 79XXXXXXXXX";
  }
  return null;
}
