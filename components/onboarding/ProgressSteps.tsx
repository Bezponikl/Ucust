export default function ProgressSteps({ current, labels }: { current: number; labels: string[] }) {
  return (
    <div aria-label="Прогресс онбординга" className="mx-auto max-w-xl">
      <div className="mb-2.5 flex items-baseline justify-between gap-3">
        <span className="text-sm font-semibold text-ink">
          {labels[current] ?? labels[labels.length - 1]}
        </span>
        <span className="text-xs font-medium text-ink-muted">
          Шаг {Math.min(current + 1, labels.length)} из {labels.length}
        </span>
      </div>
      <div className="flex gap-1.5">
        {labels.map((label, i) => (
          <div
            key={label}
            aria-current={i === current ? "step" : undefined}
            className={`h-1.5 flex-1 rounded-full transition-all duration-500 ${
              i < current ? "bg-brand/45" : i === current ? "bg-brand" : "bg-border"
            }`}
          />
        ))}
      </div>
    </div>
  );
}
