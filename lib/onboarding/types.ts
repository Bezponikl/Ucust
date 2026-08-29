import type { ChannelId } from "@/lib/channels";

export type AboutMode = "link" | "manual";

export interface WizardInput {
  name: string;
  aboutMode: AboutMode;
  link: string;
  activity: string;
  difference: string;
  socials: ChannelId[];
  files: string[];
}

export interface MarketInfo {
  competitors: string[];
  geography: string;
  segment: string;
  trends: string[];
}

export interface SwotInfo {
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  threats: string[];
}

export interface ServiceItem {
  title: string;
  items: string;
}

export interface BrandProfile {
  name: string;
  field: string;
  positioning: string;
  market: MarketInfo;
  swot: SwotInfo;
  services: ServiceItem[];
  goals: string[];
  tone: string[];
}

export const EMPTY_INPUT: WizardInput = {
  name: "",
  aboutMode: "link",
  link: "",
  activity: "",
  difference: "",
  socials: [],
  files: [],
};
