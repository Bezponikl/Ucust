"use client";

import Icon from "@/components/ui/Icon";
import type { IconName } from "@/lib/icons/solar";
import { useOnboarding } from "@/components/onboarding/OnboardingProvider";
import { Field, TextInput } from "@/components/onboarding/Field";
import FileUpload from "@/components/onboarding/FileUpload";
import type { AboutMode } from "@/lib/onboarding/types";

export default function StepAbout() {
  const { input, updateInput } = useOnboarding();
  const tab = (mode: AboutMode, label: string, icon: IconName) => (
    <button
      type="button"
      role="tab"
      aria-selected={input.aboutMode === mode}
      onClick={() => updateInput({ aboutMode: mode })}
      className={`flex flex-1 items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium transition ${
        input.aboutMode === mode ? "bg-brand text-white" : "bg-surface-soft text-ink hover:text-brand"
      }`}
    >
      <Icon name={icon} size={16} aria-hidden="true" />
      {label}
    </button>
  );

  return (
    <div className="flex flex-col gap-5">
      <header>
        <h1 className="text-2xl font-bold text-ink sm:text-3xl">Расскажите о бизнесе</h1>
        <p className="mt-2 text-sm text-ink-muted sm:text-base">
          Проще всего — дать ссылку на сайт или соцсеть, система сама всё найдёт
        </p>
      </header>
      <div role="tablist" className="flex gap-2">
        {tab("link", "По ссылке", "link")}
        {tab("manual", "Вручную", "file-text")}
      </div>
      {/* Документы бизнеса заменяют поле «описание»: прайс или презентация
          рассказывают о бизнесе точнее, чем абзац в текстареа. Нужны в обоих
          сценариях — и когда есть ссылка, и когда заполняют вручную. */}
      {input.aboutMode === "link" ? (
        <div className="flex flex-col gap-5">
          <Field
            label="Ссылка на сайт или соцсеть"
            hint="Можно указать ссылку на сайт, группу ВКонтакте, страницу в Instagram или Telegram-канал"
          >
            <TextInput
              value={input.link}
              onChange={(e) => updateInput({ link: e.target.value })}
              placeholder="https://example.com или ссылка на VK/Instagram"
            />
          </Field>
          <FileUpload />
        </div>
      ) : (
        <div className="flex flex-col gap-5">
          <Field label="Чем занимается бизнес">
            <TextInput
              value={input.activity}
              onChange={(e) => updateInput({ activity: e.target.value })}
              placeholder="Например: кофейня, салон красоты, юридические услуги"
            />
          </Field>
          <FileUpload />
        </div>
      )}
    </div>
  );
}
