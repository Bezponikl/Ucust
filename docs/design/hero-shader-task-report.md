# Hero Shader Task Report — 2026-07-03

## Summary

Tasks 1–4 from `2026-07-03-hero-shader-plan.md` implemented using the fallback path (manual npm install + hand-written component). All verification checks pass.

---

## Files Changed / Created

| File | Action |
|------|--------|
| `package.json` | Modified — `@paper-design/shaders-react` added via `npm install` |
| `components/ui/hero-shader.tsx` | Created — `ShaderBackground` wrapper with MeshGradient, theme-aware palette, reduced-motion fallback |
| `lib/useIsDark.ts` | Created — `useIsDark(): boolean` hook via MutationObserver on `<html>` class |
| `components/Hero.tsx` | Modified — dynamic import of `ShaderBackground` (ssr:false), content wrapped as children, `HeroArt` removed |
| `components/ProductShowcase.tsx` | Fixed — pre-existing TS bug: destructured `{ icon: Icon }` shadowed the imported `Icon` component; renamed to `{ icon }` and used `<Icon name={icon} …/>` |
| `components/TariffConfigurator.tsx` | Fixed — pre-existing TS bug: `HelpCircle` (from lucide-react, never imported) replaced with `<Icon name="help" …/>` |

---

## Real `MeshGradient` API

Package version installed: (latest at time of task, `@paper-design/shaders-react`)

From `node_modules/@paper-design/shaders/dist/shaders/mesh-gradient.d.ts`:

```ts
export interface MeshGradientParams extends ShaderSizingParams, ShaderMotionParams {
  colors?: string[];      // array of hex/CSS color strings (up to 10)
  distortion?: number;    // 0–1, organic noise distortion
  swirl?: number;         // 0–1, vortex distortion
  grainMixer?: number;    // 0–1, grain on shape edges
  grainOverlay?: number;  // 0–1, post-process grain overlay
}
// ShaderMotionParams:
// speed?: number;   // animation speed multiplier (0 = paused, negatives = reverse)
// frame?: number;   // starting frame offset
```

**Verdict:** The plan's assumed props `colors={string[]}` and `speed={number}` **are correct** — they match the installed API exactly. No adaptation needed.

The React component additionally accepts all standard `<div>` props (including `className`, `style`) plus `width`, `height`, `minPixelRatio`, `maxPixelCount`, `webGlContextAttributes`, and `ref?: React.Ref<PaperShaderElement>`.

---

## Implementation Notes

### Task 1 (fallback path)
Used `npm install @paper-design/shaders-react` (no 21st CLI). Created `components/ui/hero-shader.tsx` manually with the exact fallback code from the plan, then extended it with Task 3 color logic in the same file.

### Task 2
`lib/useIsDark.ts` created exactly as specified — MutationObserver on `document.documentElement`, initial `useState(false)` for SSR stability.

### Task 3
Combined into `hero-shader.tsx`:
- `DARK_COLORS = ["#0a0b14", "#4f7dff", "#7b5cff", "#ff5fa2", "#ff8c4b"]`
- `LIGHT_COLORS = ["#f5f7ff", "#c9d6ff", "#d7ccff", "#ffd0e2", "#ffe0cc"]`
- `useReducedMotion()` hook (client-only, effect-based, initial `false` → no hydration mismatch)
- Fallback: static `radial-gradient` CSS div
- `ShaderBackground` div uses `relative w-full overflow-hidden` (no fixed height) so children-driven height works correctly

### Task 4 (clean single-wrapper variant)
`Hero.tsx` restructured:
- `HeroArt` import and usage removed
- `ShaderBackground` dynamically imported with `ssr: false` and a simple loading fallback (`bg-brand/10`)
- **Hero content is wrapped as `children` inside `<ShaderBackground>`** (single-wrapper pattern, not dual-layer)
- Scrim (`bg-white/40 dark:bg-black/40`) placed as `absolute inset-0` child of ShaderBackground
- Content container uses `relative z-10 min-h-[85vh]` to sit above the canvas and scrim
- `<section>` uses `relative overflow-hidden` (no explicit height — ShaderBackground div sizes to content)

### Pre-existing TypeScript errors fixed
Two files had pre-existing type errors that blocked the build:
1. `ProductShowcase.tsx:70` — destructuring `{ icon: Icon }` created a local `string` variable named `Icon` that shadowed the React component import, causing TypeScript to infer JSX tag type as string (HTML element). Fixed by using `{ icon }` + `<Icon name={icon} …/>`.
2. `TariffConfigurator.tsx:176` — `HelpCircle` referenced but never imported (likely leftover from a lucide-react draft). Replaced with the project's own `<Icon name="help" …/>`.

---

## Verification Results

### `npx tsc --noEmit`
```
(no output — exit code 0)
```
**PASS** — zero TypeScript errors.

### `npm run build`
```
▲ Next.js 16.2.9 (Turbopack)
- Environments: .env.local

  Creating an optimized production build ...
✓ Compiled successfully in 3.5s
  Running TypeScript ...
  Finished TypeScript in 6.6s ...
  Collecting page data using 19 workers ...
  Generating static pages using 19 workers (0/20) ...
  Generating static pages using 19 workers (5/20)
  Generating static pages using 19 workers (10/20)
  Generating static pages using 19 workers (15/20)
✓ Generating static pages using 19 workers (20/20) in 1474ms
  Finalizing page optimization ...

Route (app)
┌ ○ /
├ ○ /_not-found
...
└ ○ /verify-email
```
**PASS** — all 20 pages generated, no errors or warnings.

---

## Concerns

None blocking. One cosmetic note: during the brief period while the dynamic `ShaderBackground` chunk loads (first visit), the hero shows `bg-brand/10` (a very light blue tint). This is intentional per the plan's `loading:` prop and resolves within milliseconds.

The `prefers-reduced-motion` fallback renders a static CSS radial-gradient using the same color palette — no WebGL canvas is instantiated, so GPU load is zero for affected users.

---

## Fix pass — 2026-07-03

### Findings addressed

**Finding 1 (Important) + Finding 2 (Important):** Both caused by Hero content being rendered as `children` inside the `dynamic(..., {ssr:false})` component, making headline/CTAs absent from server HTML and causing the section to collapse to 0px height during SSR.

**Finding 3 (Minor):** `ShaderBackground` prop type required `children` unconditionally, forcing callers to pass children even when used in background-only role.

### Changes made

**`components/Hero.tsx`** — dual-layer restructure:

```tsx
<section className="relative min-h-[85vh] overflow-hidden">
  {/* shader — background-only, no children */}
  <div aria-hidden className="absolute inset-0">
    <ShaderBackground />
  </div>

  {/* readability scrim */}
  <div
    aria-hidden
    className="pointer-events-none absolute inset-0 bg-white/40 dark:bg-black/40"
  />

  {/* content — server-rendered sibling above the shader */}
  <div className="relative z-10 mx-auto flex min-h-[85vh] max-w-(--container-page) items-center px-4 py-16 sm:px-6">
    {/* kicker, GradientScrollText h1, subtext, CTA buttons */}
  </div>
</section>
```

Key changes vs. previous structure:
- `<section>` gains `min-h-[85vh]` so the section has height during SSR before the shader loads.
- `<ShaderBackground />` moved into an `aria-hidden absolute inset-0` wrapper with **no children** — background-only role.
- Scrim and all content are now **server-rendered siblings** of the shader wrapper, not its children.
- The `dynamic(..., { ssr:false, loading: ... })` wrapper for the shader is unchanged.

**`components/ui/hero-shader.tsx`** — children made optional:

```tsx
import type { ReactNode } from "react";
// ...
export function ShaderBackground({ children }: { children?: ReactNode }) {
```

Added explicit `import type { ReactNode } from "react"` and changed `children: React.ReactNode` → `children?: ReactNode`. Removes reliance on global `React` namespace and allows the component to be rendered with no children (background-only).

### Verification

#### `npx tsc --noEmit`
```
(no output — exit code 0)
```
**PASS**

#### `npm run build` (last 12 lines)
```
├ ● /legal/[slug]
│ ├ /legal/offer
│ ├ /legal/privacy
│ └ /legal/pdn-consent
├ ○ /onboarding
├ ○ /onboarding/review
└ ○ /verify-email


○  (Static)  prerendered as static content
●  (SSG)     prerendered as static HTML (uses generateStaticParams)
```
**PASS** — all 20 pages generated, no errors.
