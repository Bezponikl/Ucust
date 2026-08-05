"use client";

import { useEffect, useRef, useState, type ChangeEvent } from "react";
import Image from "next/image";
import Icon from "@/components/ui/Icon";
import { SettingsCard, Field, Toggle, SaveButton } from "@/components/dashboard/settings/primitives";
import ModalShell from "@/components/ModalShell";
import { toast } from "@/lib/toast";

const SESSIONS = [
  { device: "Samsung Galaxy A23", os: "Android 10.10.1", city: "Минск, Беларусь", time: "07:09", current: true },
  { device: "MacBook Pro", os: "Chrome · macOS", city: "Минск, Беларусь", time: "вчера", current: false },
];

export default function AccountSettings() {
  const [firstName, setFirstName] = useState("Анна");
  const [lastName, setLastName] = useState("Иванова");
  const [middleName, setMiddleName] = useState(""); // отчество — опционально
  const [role, setRole] = useState("Маркетолог");
  const [email, setEmail] = useState("anna@example.com");
  const [phone, setPhone] = useState("+7 900 000-00-00");
  const [avatar, setAvatar] = useState<string | undefined>();
  const [twoFa, setTwoFa] = useState(false);

  // Смена пароля
  const [currentPw, setCurrentPw] = useState("");
  const [newPw, setNewPw] = useState("");
  const [confirmPw, setConfirmPw] = useState("");
  const [pwDone, setPwDone] = useState(false);

  const submitPassword = () => {
    if (!currentPw || !newPw || !confirmPw) { toast("Заполните все поля"); return; }
    if (newPw.length < 8) { toast("Новый пароль — минимум 8 символов"); return; }
    if (newPw !== confirmPw) { toast("Пароли не совпадают"); return; }
    setCurrentPw(""); setNewPw(""); setConfirmPw("");
    setPwDone(true);
  };

  const avatarInput = useRef<HTMLInputElement>(null);
  const urls = useRef<string[]>([]);
  useEffect(() => () => urls.current.forEach((u) => URL.revokeObjectURL(u)), []);
  const onAvatar = (e: ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) { const u = URL.createObjectURL(f); urls.current.push(u); setAvatar(u); }
    e.target.value = "";
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
          <Field label="Email" type="email" value={email} onChange={setEmail} />
          <Field label="Телефон" value={phone} onChange={setPhone} />
        </div>
        <div className="mt-5"><SaveButton /></div>
      </SettingsCard>

      {/* Безопасность */}
      <SettingsCard title="Безопасность">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div className="flex flex-col gap-3">
            <span className="text-sm font-semibold text-ink">Смена пароля</span>
            <Field label="Текущий пароль" type="password" editable={false} value={currentPw} onChange={setCurrentPw} placeholder="Текущий пароль" />
            <Field label="Новый пароль" type="password" editable={false} value={newPw} onChange={setNewPw} placeholder="Новый пароль" />
            <Field label="Повторите новый пароль" type="password" editable={false} value={confirmPw} onChange={setConfirmPw} placeholder="Повторите новый пароль" />
            <button type="button" onClick={submitPassword} className="btn-glass inline-flex w-fit items-center justify-center px-4 py-2.5 text-sm font-semibold">Обновить пароль</button>
          </div>
          <div>
            <div className="flex items-center justify-between gap-4">
              <div>
                <span className="block text-sm font-semibold text-ink">Двухфакторная аутентификация</span>
                <span className="text-xs text-ink-muted">Дополнительная защита при входе</span>
              </div>
              <Toggle checked={twoFa} onChange={setTwoFa} label="Двухфакторная аутентификация" />
            </div>
            <span className="mb-2 mt-6 block text-sm font-semibold text-ink">Активные сессии</span>
            <ul className="flex flex-col gap-2">
              {SESSIONS.map((s) => (
                <li key={s.device} className="flex items-center gap-3 rounded-2xl border border-border bg-surface-soft px-4 py-3">
                  <Icon name="monitor" size={18} className="shrink-0 text-ink-muted" aria-hidden="true" />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-ink">{s.device} {s.current && <span className="text-xs font-normal text-success">· текущая</span>}</p>
                    <p className="truncate text-xs text-ink-muted">{s.os} · {s.city} · {s.time}</p>
                  </div>
                  {!s.current && <button type="button" onClick={() => toast("Сессия завершена")} aria-label="Завершить сессию" className="text-ink-muted hover:text-red-500"><Icon name="logout" size={16} /></button>}
                </li>
              ))}
            </ul>
            <button type="button" onClick={() => toast("Вы вышли со всех устройств")} className="mt-3 inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold text-red-500 transition hover:bg-red-500/10">
              <Icon name="logout" size={16} aria-hidden="true" /> Выйти со всех устройств
            </button>
          </div>
        </div>
      </SettingsCard>

      {/* Успешная смена пароля */}
      <ModalShell open={pwDone} onClose={() => setPwDone(false)} labelledBy="pw-success-title">
        <div className="flex flex-col items-center text-center">
          <span className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-success/15 text-success">
            <Icon name="check" size={28} aria-hidden="true" />
          </span>
          <h2 id="pw-success-title" className="text-lg font-bold text-ink">Пароль обновлён</h2>
          <p className="mt-1.5 text-sm text-ink-muted">
            Пароль успешно изменён. Используйте новый пароль при следующем входе.
          </p>
          <button
            type="button"
            onClick={() => setPwDone(false)}
            className="btn-glass-blue mt-6 inline-flex items-center justify-center px-5 py-3 text-sm font-semibold"
          >
            Готово
          </button>
        </div>
      </ModalShell>
    </div>
  );
}
