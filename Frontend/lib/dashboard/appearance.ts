export interface BackgroundPreset {
  id: string;
  label: string;
  src: string;
}

export const BACKGROUND_PRESETS: BackgroundPreset[] = [
  { id: "bg-1", label: "Осенняя долина", src: "/backgrounds/bg-1.jpg" },
  { id: "bg-2", label: "Лесная тропа", src: "/backgrounds/bg-2.jpg" },
  { id: "bg-3", label: "Стеклянный небоскрёб", src: "/backgrounds/bg-3.jpg" },
  { id: "bg-4", label: "Горный фьорд", src: "/backgrounds/bg-4.jpg" },
  { id: "bg-5", label: "Пастельный рассвет", src: "/backgrounds/bg-5.jpg" },
  { id: "bg-6", label: "Мраморные волны", src: "/backgrounds/bg-6.jpg" },
  { id: "bg-7", label: "Шёлковые волны", src: "/backgrounds/bg-7.jpg" },
  { id: "bg-8", label: "Розовые дюны", src: "/backgrounds/bg-8.jpg" },
];
