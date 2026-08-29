import type { SVGProps } from "react";
import { ICONS, type IconName } from "@/lib/icons/solar";

type IconProps = Omit<SVGProps<SVGSVGElement>, "name"> & {
  name: IconName;
  size?: number;
};

/**
 * Иконки Solar (скруглённый iOS-стиль). Тела извлечены локально скриптом
 * scripts/gen-icons.mjs — весь набор в бандл не тащим. Цвет — через currentColor.
 */
export default function Icon({ name, size = 24, className, ...rest }: IconProps) {
  const ic = ICONS[name];
  // Размер в rem, а не в px: на 2K/4K корневой кегль растёт (globals.css),
  // и иконки масштабируются вместе с текстом. Класс w-*/h-* по-прежнему перебивает.
  const px = `${size / 16}rem`;
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={px}
      height={px}
      viewBox={`0 0 ${ic.w} ${ic.h}`}
      fill="currentColor"
      aria-hidden={rest["aria-label"] ? undefined : true}
      focusable="false"
      className={className}
      dangerouslySetInnerHTML={{ __html: ic.body }}
      {...rest}
    />
  );
}
