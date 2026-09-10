"use client";

import { useEffect, useRef, useState, type ChangeEvent } from "react";
import Image from "next/image";
import Icon from "@/components/ui/Icon";
import { SettingsCard, Field, Toggle, SaveButton } from "@/components/dashboard/settings/primitives";
import ChangeEmailModal from "@/components/dashboard/account/ChangeEmailModal";
import { toast } from "@/lib/toast";
import { toMessage } from "@/lib/api/errors";
import { getSessions, revokeAllSessions, revokeSession } from "@/lib/api/auth";
import { updateMe, uploadAvatar } from "@/lib/api/users";
import { normalizePhone, validateProfileFields } from "@/lib/api/profileFields";
import type { SessionResponse } from "@/lib/api/types";
import { useSession } from "@/lib/session/SessionProvider";

/** User-Agent → «Chrome · Windows» без сторонних библиотек. */
function describeUserAgent(ua: string | null): string {
  if (!ua) return "Неизвестное устройство";
  const browser = ua.includes("Edg/") ? "Edge"
    : ua.includes("Chrome/") ? "Chrome"
    : ua.includes("Firefox/") ? "Firefox"
    : ua.includes("Safari/") ? "Safari"
    : ua.includes("OPR/") ? "Opera"
    : "Браузер";
  const os = /Windows NT/.test(ua) ? "Windows"
    : /Mac OS X/.test(ua) ? "macOS"
    : /Android/.test(ua) ? "Android"
    : /iPhone|iPad/.test(ua) ? "iOS"
    : /Linux/.test(ua) ? "Linux"
    : "другая ОС";
  return `${browser} · ${os}`;
}

/** Время создания сессии — коротко: «9 сен, 07:09». */
function formatWhen(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  const date = d.toLocaleDateString("ru-RU", { day: "numeric", month: "short" });
  const time = d.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" });
  return `${date}, ${time}`;
}

export default function AccountSettings() {
  const { user, reload } = useSession();
  const [firstName, setFirstName] = useState("Анна");
  const [lastName, setLastName] = useState("Иванова");
  const [middleName, setMiddleName] = useState(""); // отчество — опционально
  const [role, setRole] = useState("Маркетолог");
  const [email, setEmail] = useState("anna@example.com");
  const [phone, setPhone] = useState("+7 900 000-00-00");
  const [avatar, setAvatar] = useState<string | undefined>();
  const [twoFa, setTwoFa] = useState(false);
  // Почта меняется не через updateMe, а отдельной цепочкой из трёх шагов бэка.
  const [emailFlowOpen, setEmailFlowOpen] = useState(false);
  const [sessions, setSessions] = useState<SessionResponse[] | null>(null);

  // Сессии тянем с бэка (security-service), а не из демо-массива.
  useEffect(() => {
    if (!user) return;
    let alive = true;
    setSessions(null);
    getSessions()
      .then((list) => {
        if (alive) setSessions(list);
      })
      .catch((err) => {
        if (alive) toast(toMessage(err));
      });
    return () => {
      alive = false;
    };
  }, [user]);

  const endSession = async (id: string) => {
    try {
      await revokeSession(id);
    } catch (err) {
      toast(toMessage(err));
      return;
    }
    setSessions((list) => (list ? list.filter((s) => s.id !== id) : list));
    toast("Сессия завершена");
  };

  const endAllSessions = async () => {
    try {
      await revokeAllSessions();
    } catch (err) {
      toast(toMessage(err));
      return;
    }
    // Текущая сессия остаётся — бэк не тронул её токен.
    setSessions((list) => (list ? list.filter((s) => s.current) : list));
    toast("Все сессии, кроме текущей, завершены");
  };

  // С настоящим бэком поля заполняются данными аккаунта, а не демо-значениями.
  useEffect(() => {
    if (!user) return;
    /* eslint-disable react-hooks/set-state-in-effect */
    setFirstName(user.firstName ?? "");
    setMiddleName(user.middleName ?? "");
    setLastName(user.lastName ?? "");
    setEmail(user.email ?? "");
    setPhone(user.phone ?? "");
    setRole(user.position ?? "");
    if (user.fullAvatarUrl) setAvatar(user.fullAvatarUrl);
    /* eslint-enable react-hooks/set-state-in-effect */
  }, [user]);

  const saveProfile = async () => {
    // Правила бэка проверяем до отправки: иначе пользователь получит сухой 400.
    const normalizedPhone = normalizePhone(phone);
    const problem = validateProfileFields({ firstName, middleName, lastName, phone: normalizedPhone });
    if (problem) {
      toast(problem);
      return;
    }

    try {
      await updateMe({
        firstName,
        middleName: middleName || undefined,
        lastName,
        phone: normalizedPhone || undefined,
        position: role || undefined,
      });
      await reload();
    } catch (err) {
      toast(toMessage(err));
    }
  };

  const avatarInput = useRef<HTMLInputElement>(null);
  const urls = useRef<string[]>([]);
  useEffect(() => () => urls.current.forEach((u) => URL.revokeObjectURL(u)), []);
  const onAvatar = async (e: ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    e.target.value = "";
    if (!f) return;

    // Показываем выбранный файл сразу, не дожидаясь ответа сервера.
    const u = URL.createObjectURL(f);
    urls.current.push(u);
    setAvatar(u);

    if (f.size > 10 * 1024 * 1024) {
      toast("Файл больше 10 МБ — сервер его не примет");
      return;
    }
    try {
      await uploadAvatar(f);
      await reload();
    } catch (err) {
      toast(toMessage(err));
    }
  };

  // Имя = Фамилия Имя [Отчество] — отчество только если заполнено
  const fullName = [lastName, firstName, middleName].filter(Boolean).join(" ") || "Имя не указано";
  const initials = ((lastName[0] ?? "") + (firstName[0] ?? "")).toUpperCase() || "U";

  return (
    <div className="flex flex-col gap-5">
      <div>
        <h1 className="text-xl font-bold text-ink sm:text-2xl">Настройки аккаунта</h1>
        <p className="mt-0.5 text-sm text-ink-muted">Личные данные, уведомления и безопасность</p>
      </div>

      {/* Шапка: аватар + имя — без карточки */}
      <div className="flex items-center gap-5">
        <span className="relative flex h-24 w-24 shrink-0 items-center justify-center overflow-hidden rounded-full bg-brand text-3xl font-bold text-white">
          {avatar ? <Image src={avatar} alt="" fill unoptimized className="object-cover" /> : initials}
        </span>
        <div className="min-w-0">
          <p className="truncate text-xl font-bold text-ink">{fullName}</p>
          <p className="text-sm text-ink-muted">{role}</p>
          <div className="mt-2 flex items-center gap-3 text-sm">
            <button type="button" onClick={() => avatarInput.current?.click()} className="inline-flex items-center gap-1.5 font-medium text-brand hover:text-brand-hover"><Icon name="image-plus" size={15} /> Загрузить</button>
            {avatar && <button type="button" onClick={() => setAvatar(undefined)} className="text-ink-muted hover:text-ink">Удалить</button>}
          </div>
        </div>
        <input ref={avatarInput} type="file" accept="image/*" hidden onChange={onAvatar} />
      </div>

      {/* Профиль */}
      <SettingsCard title="Профиль">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="Фамилия" value={lastName} onChange={setLastName} />
          <Field label="Имя" value={firstName} onChange={setFirstName} />
          <Field label="Отчество" hint="(не обязательно)" value={middleName} onChange={setMiddleName} placeholder="Отчество" />
          <Field label="Должность" value={role} onChange={setRole} />
          <div>
            <Field label="Email" type="email" editable={false} value={email} onChange={setEmail} />
            <button
              type="button"
              onClick={() => setEmailFlowOpen(true)}
              className="mt-1.5 inline-flex items-center gap-1.5 text-sm font-medium text-brand hover:text-brand-hover"
            >
              <Icon name="edit" size={14} aria-hidden="true" /> Сменить почту
            </button>
          </div>
          <Field label="Телефон" value={phone} onChange={setPhone} />
        </div>
        <div className="mt-5"><SaveButton onSave={saveProfile} /></div>
      </SettingsCard>

      {/* Безопасность */}
      <SettingsCard title="Безопасность">
        <div>
          <div className="flex items-center justify-between gap-4">
            <div>
              <span className="block text-sm font-semibold text-ink">Двухфакторная аутентификация</span>
              <span className="text-xs text-ink-muted">Дополнительная защита при входе</span>
            </div>
            <Toggle checked={twoFa} onChange={setTwoFa} label="Двухфакторная аутентификация" />
          </div>
          <span className="mb-2 mt-6 block text-sm font-semibold text-ink">Активные сессии</span>
          {sessions === null ? (
            <p className="text-sm text-ink-muted">Загружаем сессии…</p>
          ) : sessions.length === 0 ? (
            <p className="text-sm text-ink-muted">Активных сессий нет</p>
          ) : (
            <ul className="flex flex-col gap-2">
              {sessions.map((s) => (
                <li key={s.id} className="flex items-center gap-3 rounded-2xl border border-border bg-surface-soft px-4 py-3">
                  <Icon name="monitor" size={18} className="shrink-0 text-ink-muted" aria-hidden="true" />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-ink">{describeUserAgent(s.userAgent)} {s.current && <span className="text-xs font-normal text-success">· текущая</span>}</p>
                    <p className="truncate text-xs text-ink-muted">{[s.ip, s.city, formatWhen(s.createdAt)].filter(Boolean).join(" · ")}</p>
                  </div>
                  {!s.current && (
                    <button
                      type="button"
                      onClick={() => void endSession(s.id)}
                      aria-label="Завершить сессию"
                      className="text-ink-muted transition-colors hover:text-red-500"
                    >
                      <Icon name="logout" size={16} />
                    </button>
                  )}
                </li>
              ))}
            </ul>
          )}
          <button
            type="button"
            onClick={() => void endAllSessions()}
            className="mt-3 inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold text-red-500 transition hover:bg-red-500/10"
          >
            <Icon name="logout" size={16} aria-hidden="true" /> Выйти со всех устройств
          </button>
        </div>
      </SettingsCard>

      <ChangeEmailModal
        open={emailFlowOpen}
        currentEmail={email}
        onClose={() => setEmailFlowOpen(false)}
        onChanged={() => void reload()}
      />
    </div>
  );
}
