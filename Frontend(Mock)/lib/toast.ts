type Listener = (msg: string) => void;

const listeners = new Set<Listener>();

/** Показать всплывающее уведомление (toast). */
export function toast(message: string): void {
  listeners.forEach((l) => l(message));
}

export function subscribeToast(l: Listener): () => void {
  listeners.add(l);
  return () => {
    listeners.delete(l);
  };
}
