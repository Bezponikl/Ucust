"use client";

import Icon from "@/components/ui/Icon";
import { TextInput } from "@/components/onboarding/Field";

/** Редактируемый список строк: правка каждой, удаление, добавление новой. */
export default function EditableList({
  value,
  onChange,
  placeholder,
  addLabel = "Добавить",
}: {
  value: string[];
  onChange: (next: string[]) => void;
  placeholder?: string;
  addLabel?: string;
}) {
  const setAt = (i: number, v: string) => onChange(value.map((x, idx) => (idx === i ? v : x)));
  const removeAt = (i: number) => onChange(value.filter((_, idx) => idx !== i));
  const add = () => onChange([...value, ""]);

  return (
    <div className="flex flex-col gap-2">
      {value.map((item, i) => {
        const urlMatch = item.match(/https?:\/\/[^\s\)]+/);
        const url = urlMatch ? urlMatch[0] : null;

        return (
          <div key={i} className="flex items-center gap-1.5">
            <div className="relative flex-1">
              <TextInput value={item} placeholder={placeholder} onChange={(e) => setAt(i, e.target.value)} />
            </div>
            {url && (
              <a
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                title="Перейти по ссылке"
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-brand/20 bg-brand/10 text-brand transition hover:bg-brand/20"
              >
                <Icon name="link" size={15} aria-hidden="true" />
              </a>
            )}
            <button
              type="button"
              onClick={() => removeAt(i)}
              aria-label="Удалить"
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-ink-muted transition hover:bg-red-500/10 hover:text-red-500"
            >
              <Icon name="close" size={16} aria-hidden="true" />
            </button>
          </div>
        );
      })}
      <button
        type="button"
        onClick={add}
        className="inline-flex w-fit items-center gap-1.5 rounded-full px-3 py-2 text-sm font-medium text-brand transition hover:bg-brand/10"
      >
        <Icon name="plus" size={16} aria-hidden="true" /> {addLabel}
      </button>
    </div>
  );
}
