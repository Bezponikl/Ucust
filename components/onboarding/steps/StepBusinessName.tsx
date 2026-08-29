"use client";

import { useOnboarding } from "@/components/onboarding/OnboardingProvider";
import { Field, TextInput } from "@/components/onboarding/Field";

export default function StepBusinessName() {
  const { input, updateInput } = useOnboarding();
  return (
    <div className="flex flex-col gap-5">
      <header>
        <h1 className="text-2xl font-bold text-ink sm:text-3xl">Как называется ваш бизнес?</h1>
        <p className="mt-2 text-sm text-ink-muted sm:text-base">
          С него начнём — остальное соберём на следующих шагах
        </p>
      </header>
      <Field label="Название">
        <TextInput
          value={input.name}
          onChange={(e) => updateInput({ name: e.target.value })}
          placeholder="Например: Кофейня Аромат"
        />
      </Field>
    </div>
  );
}
