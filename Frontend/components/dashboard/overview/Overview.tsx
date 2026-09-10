"use client";

import { useDashboard } from "../DashboardProvider";
import ComingSoon from "../ComingSoon";
import CreateProjectNotice from "../CreateProjectNotice";
import OverviewHeader from "./OverviewHeader";
import InlineAiPrompt from "./InlineAiPrompt";
import StatCards from "./StatCards";
import AiTips from "./AiTips";
import WeekPreview from "./WeekPreview";
import ActivityFeed from "./ActivityFeed";
import EmptyOverview from "./EmptyOverview";

export default function Overview() {
  const { data, hasProject, hydrated } = useDashboard();

  if (!data || !hydrated) {
    return <div className="h-40 animate-pulse rounded-[20px] bg-surface-soft" />;
  }

  // Сразу после регистрации проекта ещё нет: показываем каркас дашборда
  // с приглашением создать профиль вместо чужих цифр.
  if (!hasProject) return <EmptyOverview />;

  // Проект есть, но без профиля бренда (у бэка нет имени): активности вроде
  // генерации не работают. Вместо них — пояснение и кнопка «Создать проект».
  // Заглушки «Скоро» оставляем как есть.
  if (!data.businessName?.trim()) {
    return (
      <div className="flex flex-col gap-6 sm:gap-8">
        <div data-tour="overview">
          <OverviewHeader businessName={null} />
        </div>

        <CreateProjectNotice />

        <ComingSoon
          icon="trending"
          title="Статистика и рекомендации"
          text="Как только подключим метрики площадок, здесь появятся охваты и реакции, контент-план недели и советы UCust — пока без выдуманных цифр."
        />
      </div>
    );
  }

  // Метрики, рекомендации и план недели пока не приходят с бэка — вместо
  // выдуманных цифр показываем честную заглушку «Скоро».
  const hasInsights =
    data.stats.length > 0 ||
    data.tips.length > 0 ||
    data.week.length > 0 ||
    data.activity.length > 0;

  return (
    <div className="flex flex-col gap-6 sm:gap-8">
      <div data-tour="overview">
        <OverviewHeader businessName={data.businessName} />
      </div>

      {hasInsights ? (
        <>
          <StatCards stats={data.stats} />
          <div data-tour="ai-prompt">
            <InlineAiPrompt />
          </div>
          <AiTips tips={data.tips} />
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 [&>*]:min-w-0">
            <WeekPreview week={data.week} />
            <ActivityFeed items={data.activity} />
          </div>
        </>
      ) : (
        <>
          <div data-tour="ai-prompt">
            <InlineAiPrompt />
          </div>
          <ComingSoon
            icon="trending"
            title="Статистика и рекомендации"
            text="Как только подключим метрики площадок, здесь появятся охваты и реакции, контент-план недели и советы UCust — пока без выдуманных цифр."
          />
        </>
      )}
    </div>
  );
}