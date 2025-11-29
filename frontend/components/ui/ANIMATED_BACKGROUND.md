# AnimatedBackground component

This component provides a lightweight animated background designed for the splash screen or hero areas. It uses SVG blobs and CSS keyframe animations to create a calming, attractive motion effect.

Features
- Animated gradient blurs + 3 layered SVG blobs.
- Subtle particle overlay to add texture.
- Helper classes `headlineReveal` and `ctaPop` for subtle text/CTA animations.
- Respects `prefers-reduced-motion` — if the user has reduced motion enabled the animations are disabled.

How to use
1. Import and render the component anywhere behind your content (it is `position:absolute` by default):

```tsx
import AnimatedBackground from "@/components/ui/animated-background";

function Hero() {
  return (
    <div className="relative min-h-screen">
      <AnimatedBackground />
      <div className="relative z-10">{/* your content */}</div>
    </div>
  );
}
```

Customization tips
- Colors: modify the gradient colors or SVG fills in `animated-background.module.css`.
- Movement: tweak animation durations & transforms to make motion faster or slower.
- Accessibility: do not reduce animation duration below 250ms; always respect `prefers-reduced-motion`.

Performance
- Everything is CSS + SVG to keep it lightweight — no external libs required. Keep `filter: blur()` sizes reasonable to avoid GPU pressure on older devices.
