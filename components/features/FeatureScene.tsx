"use client";

import { memo, useEffect, useRef, useState } from "react";
import { SCENES, type SceneId } from "./scenes.data";

/* Пауза анимаций неактивной карточки + freeze при reduced-motion.
   Инъектится в scoped <style> сцены (Tailwind его не трогает). */
const CONTROL_CSS =
  // Отложенные анимации (animation-delay) должны показывать НУЛЕВОЙ кадр во время
  // задержки, а не базовый inline-стиль. В шорткате сцен fill-mode = none, поэтому
  // до старта элемент рисовал своё базовое состояние (opacity:1) — стек «Опубликовано»
  // вспыхивал поверх «Запланировано». backwards чинит это во всех сценах; !important
  // перебивает inline-значение none.
  '.fscene [style*="animation"]{animation-fill-mode:backwards!important}' +
  '.fscene-paused [style*="animation"]{animation-play-state:paused!important}' +
  '@media(prefers-reduced-motion:reduce){.fscene [style*="animation"]{animation-play-state:paused!important;animation-delay:-4s!important}}';

/**
 * Анимированная «сюжетная» сцена возможности.
 * - На ПК (pauseInactive=false, active=true): анимация идёт непрерывно, не прерывается при листании.
 * - На мобилке (pauseInactive=true): неактивная карточка заморожена; при переключении на неё
 *   анимация стартует с нуля (remount по runKey).
 */
function FeatureScene({
  id,
  active = true,
  pauseInactive = false,
}: {
  id: SceneId;
  active?: boolean;
  pauseInactive?: boolean;
}) {
  const scene = SCENES[id];
  const ref = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(0);
  const [runKey, setRunKey] = useState(0);
  const prevActive = useRef(active);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const measure = () => setScale(el.clientWidth / 420);
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  // Мобилка: при любой смене активности пересобираем сцену (remount по runKey),
  // чтобы анимация начиналась строго с нулевого кадра — и активная играет с начала,
  // и неактивная застывает на чистом старте. Делаем это во время рендера (паттерн
  // «сброс состояния при смене пропа»), а не в useEffect: иначе размороженный на
  // середине кадр успевал бы прорисоваться до ремоунта — тот самый эффект «наслаивания».
  if (active !== prevActive.current) {
    prevActive.current = active;
    if (pauseInactive) setRunKey((k) => k + 1);
  }

  const paused = pauseInactive && !active;

  return (
    <div
      ref={ref}
      className={`fscene relative w-full overflow-hidden rounded-[28px] shadow-soft ${paused ? "fscene-paused" : ""}`}
      style={{ aspectRatio: "420 / 525" }}
    >
      <div
        key={runKey}
        className="absolute left-0 top-0 origin-top-left"
        style={{
          width: 420,
          height: 525,
          transform: `scale(${scale || 0.001})`,
          visibility: scale ? "visible" : "hidden",
        }}
      >
        <div className="dark:hidden" dangerouslySetInnerHTML={{ __html: scene.lightHtml }} />
        <div className="hidden dark:block" dangerouslySetInnerHTML={{ __html: scene.darkHtml }} />
      </div>
      <style dangerouslySetInnerHTML={{ __html: scene.keyframes + CONTROL_CSS }} />
    </div>
  );
}

// memo: на десктопе пропсы стабильны при листании → нет ре-рендера → CSS-анимации не сбрасываются.
export default memo(FeatureScene);
