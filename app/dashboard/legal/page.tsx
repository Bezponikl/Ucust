import { redirect } from "next/navigation";
import { LEGAL_LINKS } from "@/lib/legal";

/**
 * В меню профиля «Правовое» — один пункт, а документов шесть. Раздел без слага
 * раньше отдавал 404; теперь он ведёт на первый документ, дальше переключение
 * вкладками внутри страницы.
 */
export default function DashboardLegalIndex() {
  redirect(`/dashboard${LEGAL_LINKS[0].href}`);
}
