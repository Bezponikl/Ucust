import Icon from "../ui/Icon";
import type { IconName } from "@/lib/icons/solar";

export default function SectionStub({ title, icon }: { title: string; icon: IconName }) {
  return (
    <div className="grid min-h-[60vh] place-items-center text-center">
      <div>
        <span className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-tint text-brand">
          <Icon name={icon} size={28} aria-hidden="true" />
        </span>
        <h1 className="text-2xl font-bold text-ink sm:text-3xl">{title}</h1>
        <p className="mx-auto mt-2 max-w-sm text-sm text-ink-muted">
          Раздел в разработке — появится в ближайшем обновлении.
        </p>
      </div>
    </div>
  );
}
