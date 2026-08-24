import type { AccentColor, ActivityItem } from "./types";

const STORAGE_KEY = "uc_activities";

export function loadActivities(): ActivityItem[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function saveActivities(items: ActivityItem[]): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  } catch {}
}

export function addActivity(entry: { text: string; color?: AccentColor; time?: string }): void {
  if (typeof window === "undefined") return;
  const current = loadActivities();
  const newItem: ActivityItem = {
    id: `act_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
    text: entry.text,
    time: entry.time || "только что",
    color: entry.color || "brand",
  };
  const updated = [newItem, ...current].slice(0, 15);
  saveActivities(updated);
}

export function clearActivities(): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {}
}
