"use client";

import { useRouter } from "next/navigation";
import Icon from "@/components/ui/Icon";

/** Пустой дашборд (нет проекта или нет профиля бренда): активности вроде
 *  генерации недоступны — вместо мёртвых действий показываем пояснение
 *  и кнопку создания проекта. */
export default function CreateProjectNotice() {
  const router = useRouter();

  const goCreate = () => {
    try {
      sessionStorage.setItem("uc_show_setup", "1");
    } catch {}
    router.push("/onboarding");
  };

  return (
    <div className="rounded-[24px] border border-dashed border-brand/40 bg-brand/6 p-6 sm:p-8">
      <div className="flex flex-col items-start gap-5 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-start gap-4">
          <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-brand/12 text-brand">
            <Icon name="buildings" size={20} aria-hidden="true" />
          </span>
          <div className="max-w-xl">
            <h2 className="text-base font-bold text-ink sm:text-lg">Для этого нужен проект</h2>
            <p className="mt-1 text-sm leading-relaxed text-ink-muted">
              Генерация контента, подключение соцсетей, входящие и аналитика
              появятся после создания профиля проекта — расскажите о деле, и UCust
              поймёт, что за бизнес вести.
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={goCreate}
          className="btn-glass-blue inline-flex shrink-0 items-center justify-center gap-2 px-6 py-3 text-sm font-semibold"
        >
          <Icon name="plus" size={16} aria-hidden="true" /> Создать проект
        </button>
      </div>
    </div>
  );
}