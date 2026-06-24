import { ShieldCheck, FileLock2, Cpu } from "lucide-react";
import Reveal from "./Reveal";

const ITEMS = [
  { icon: ShieldCheck, label: "Данные на серверах в РФ", gradient: "from-sky-400 to-blue-600" },
  { icon: FileLock2, label: "Соответствие 152-ФЗ", gradient: "from-emerald-400 to-teal-500" },
  { icon: Cpu, label: "Работает на отечественных ИИ-моделях", gradient: "from-violet-400 to-purple-600" },
];

export default function TrustStrip() {
  return (
    <section className="px-4 pt-6 sm:px-6 sm:pt-8">
      <Reveal className="mx-auto max-w-(--container-page) rounded-2xl bg-card px-6 py-5 shadow-soft sm:px-8 sm:py-6">
        <ul className="flex flex-col flex-wrap items-center justify-center gap-x-10 gap-y-3 text-sm font-medium text-ink sm:flex-row">
          {ITEMS.map(({ icon: Icon, label, gradient }) => (
            <li key={label} className="flex items-center gap-2.5">
              <span className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br shadow-soft ${gradient}`}>
                <Icon size={15} className="text-white" aria-hidden="true" />
              </span>
              {label}
            </li>
          ))}
        </ul>
      </Reveal>
    </section>
  );
}
