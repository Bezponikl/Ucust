"use client";

import { useDashboard } from "../DashboardProvider";
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

  return (
    <div className="flex flex-col gap-6 sm:gap-8">
      <div data-tour="overview">
        <OverviewHeader businessName={data.businessName} />
      </div>
      <StatCards stats={data.stats} />
      <div data-tour="ai-prompt">
        <InlineAiPrompt />
      </div>
      <AiTips tips={data.tips} />
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 [&>*]:min-w-0">
        <WeekPreview week={data.week} />
        <ActivityFeed items={data.activity} />
      </div>
    </div>
  );
}
