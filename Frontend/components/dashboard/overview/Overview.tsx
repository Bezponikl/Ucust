"use client";

import { useDashboard } from "../DashboardProvider";
import OverviewHeader from "./OverviewHeader";
import StatCards from "./StatCards";
import ReachChart from "./ReachChart";
import AiTips from "./AiTips";
import WeekPreview from "./WeekPreview";
import ActivityFeed from "./ActivityFeed";

export default function Overview() {
  const { data } = useDashboard();

  if (!data) {
    return <div className="h-40 animate-pulse rounded-[20px] bg-surface-soft" />;
  }

  return (
    <div className="flex flex-col gap-6 sm:gap-8">
      <OverviewHeader businessName={data.businessName} />
      <StatCards stats={data.stats} />
      <ReachChart chart={data.chart} />
      <AiTips tips={data.tips} />
      <div className="grid gap-6 lg:grid-cols-2">
        <WeekPreview week={data.week} />
        <ActivityFeed items={data.activity} />
      </div>
    </div>
  );
}
