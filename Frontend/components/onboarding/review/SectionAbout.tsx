"use client";

import type { BrandProfile } from "@/lib/onboarding/types";
import { Field, TextArea, TextInput } from "@/components/onboarding/Field";

export default function SectionAbout({ profile }: { profile: BrandProfile }) {
  return (
    <div className="flex flex-col gap-5">
      <header>
        <h1 className="text-2xl font-bold text-ink sm:text-3xl">О проекте</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Проверьте информацию. Если что-то неправильно — отредактируйте.
        </p>
      </header>
      <div className="flex aspect-[2/1] max-w-sm items-center justify-center rounded-2xl bg-brand-tint px-6 text-center">
        <span className="font-display text-2xl font-extrabold text-brand">{profile.name}</span>
      </div>
      <Field label="Название">
        <TextInput defaultValue={profile.name} />
      </Field>
      <Field label="Сфера деятельности">
        <TextInput defaultValue={profile.field} />
      </Field>
      <Field label="Позиционирование">
        <TextArea defaultValue={profile.positioning} />
      </Field>
    </div>
  );
}
