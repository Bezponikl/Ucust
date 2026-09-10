export default function OverviewHeader({ businessName }: { businessName: string | null }) {
  return (
    <div>
      <h1 className="text-xl font-bold text-ink sm:text-2xl">Добрый день!</h1>
      {businessName && (
        <p className="mt-0.5 text-sm text-ink-muted">
          Вот что происходит с бизнесом «{businessName}»
        </p>
      )}
    </div>
  );
}
