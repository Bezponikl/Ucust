import ComingSoon from "@/components/dashboard/ComingSoon";
import PageWindow from "@/components/dashboard/PageWindow";

export default function InboxPage() {
  return (
    <PageWindow>
      <div className="flex flex-col gap-6">
        <div>
          <h1 className="text-xl font-bold text-ink sm:text-2xl">Входящие</h1>
          <p className="mt-0.5 text-sm text-ink-muted">Сообщения и комментарии из соцсетей</p>
        </div>

        <ComingSoon
          icon="message"
          title="Входящие скоро появятся"
          text="Как только подключим площадки, здесь будут сообщения, комментарии и отзывы клиентов из соцсетей — с ответами в одном окне. Пока без выдуманных переписок."
        />
      </div>
    </PageWindow>
  );
}