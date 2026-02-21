# DotSpeak / Deets Logo Guide

## Primary Logo: Ripple Drop ⭐

**Concept:** A teardrop shape with ripples spreading outward, and a dot in the center.

### Symbolism
- **Drop** = Sharing knowledge (the phrase "drop a deet"), spreading information
- **Ripple rings** = Viral spread (each person passing to the next creates ripples outward)
- **Center dot** = The deet itself (core claim, the fundamental unit of truth)
- **Motion** = Growth and network expansion

### Design Details
- **Primary color:** `#1d9bf0` (Twitter/Threads blue = trust, information, social)
- **Center dot:** White for contrast
- **Scalable:** Works at any size (favicon to billboard)
- **Wordless:** Universal appeal, no language barrier

### Usage
- **Landing page hero:** 80×80px
- **Favicon:** 16×16px (simplified background variant)
- **Header:** 24×24px (inline with text)
- **Mobile app icon:** 180×180px (full-bleed with safe zone)
- **Marketing:** 512×512px

### Files
- `static/logo_ripple_drop.svg` — Full resolution
- `static/favicon.svg` — Favicon variant (blue background)
- Embedded in `templates/landing.html`, `templates/dashboard_v2.html`

---

## Alternative: Double Drop Handoff

**Concept:** Two drops with a handoff curve, representing the "pass" mechanic.

### When to use
- If you want to emphasize **person-to-person sharing** over viral spread
- Marketing materials highlighting the interactive/social aspect
- User onboarding (shows the mechanic clearly)

### Files
- `static/logo_double_drop.svg` — Full resolution

---

## Color Palette

| Element | Color | Hex | Usage |
|---------|-------|-----|-------|
| Primary | Twitter Blue | `#1d9bf0` | Logo, accents, active states |
| Contrast | White | `#ffffff` | Center dot, light backgrounds |
| Background | Light Gray | `#f7f9fa` | Feed backgrounds |
| Border | Light Gray | `#e1e8ed` | Card borders, dividers |
| Text | Dark | `#1a1a1a` | Primary text |
| Muted | Gray | `#666` | Secondary text |

---

## Related: Logo Concepts Viewed

6 concepts were designed and evaluated:
1. **Ripple Drop** ⭐ — CHOSEN (best balance of symbolism + scalability)
2. **Cascading Dots** — Shows network growth (alternative)
3. **Chat Bubble Drop** — Direct message metaphor
4. **Credibility Shield** — Emphasizes trust/validation
5. **Dot Trail** — Growth visualization
6. **Double Drop Handoff** — Person-to-person sharing (alternative)

View all at: `logo_concepts.html` (open in browser for interactive preview)

---

## Typography

- **Font stack:** `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
- **Headlines:** 700 weight (bold)
- **Body:** 400 weight (regular)
- **Sizes:**
  - H1: 40px
  - H2: 20px (dashboard header with logo)
  - Body: 14px
  - Small: 13px

---

## Implementation Notes

### Favicon
The favicon uses a simplified variant:
- Solid `#1d9bf0` background circle
- White drop shape
- Blue center dot
- Works at 16×16px (crisp, clear)

### Inline SVGs
Logos embedded directly in HTML (no external requests):
- Faster load times
- Single-source-of-truth for styling
- Easy to animate if needed

### Future: Animation
Consider subtle animations for the ripple rings (expand → fade) on hover/interaction to emphasize the "spreading" metaphor.

---

## Brand Guidelines Summary

✅ **DOs:**
- Use `#1d9bf0` consistently
- Keep center dot white for contrast
- Maintain drop shape proportions
- Include ripples in primary lockup (adds movement)
- Pair with "Deets" wordmark in Segoe UI / system fonts

❌ **DON'Ts:**
- Don't change the color scheme (use approved palette)
- Don't remove the ripples (they're the "viral" part)
- Don't skew or distort the drop
- Don't use shadow/3D effects (keep it flat, modern)
- Don't place on competing colors without sufficient contrast

---

**Created:** 2026-02-21 | **Status:** Ready for launch | **Files:** SVG (vector, scalable) + Favicon
