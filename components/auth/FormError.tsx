/**
 * Сообщение об ошибке формы. role="alert" нужен, чтобы скринридер объявил
 * текст сразу после неудачной отправки — иначе ошибку заметит только зрячий.
 */
export default function FormError({ children }: { children?: string | null }) {
  if (!children) return null;

  return (
    <p
      role="alert"
      className="rounded-2xl bg-[color:var(--error,#e5484d)]/10 px-4 py-3 text-sm text-[color:var(--error,#e5484d)]"
    >
      {children}
    </p>
  );
}
