export default function ProgressSteps({ current, labels }: { current: number; labels: string[] }) {
  return (
    <div aria-label="Прогресс онбординга" className="mx-auto flex max-w-xl gap-2">
      {labels.map((label, i) => (
        <div key={label} className="flex-1">
          <div
            className={`h-1.5 rounded-full transition-colors ${i <= current ? "bg-brand" : "bg-border"}`}
            aria-current={i === current ? "step" : undefined}
          />
          <span className={`mt-2 hidden text-xs sm:block ${i <= current ? "text-ink" : "text-ink-muted"}`}>
            {label}
          </span>
        </div>
      ))}
    </div>
  );
}
