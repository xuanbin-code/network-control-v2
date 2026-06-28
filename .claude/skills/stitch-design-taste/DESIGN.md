# Design System: Taste Standard
**Skill:** stitch-design-taste

---

## Configuration — Set Your Style
Adjust these dials before using this design system. They control how creative, dense, and animated the output should be.

| Dial | Level | Description |
|------|-------|-------------|
| **Creativity** | `8` | `1` = Ultra-minimal, Swiss, silent. `5` = Balanced. `10` = Expressive, editorial, bold typography. Default: `8` |
| **Density** | `4` | `1` = Gallery-airy. `5` = Balanced. `10` = Cockpit-dense. Default: `4` |
| **Variance** | `8` | `1` = Predictable, symmetric. `5` = Subtle offsets. `10` = Artsy chaotic. Default: `8` |
| **Motion Intent** | `6` | `1` = Static. `5` = Subtle hover/entrance cues. `10` = Cinematic orchestration. Default: `6` |

## 1. Visual Theme & Atmosphere
A restrained, gallery-airy interface with confident asymmetric layouts and fluid spring-physics motion. The atmosphere is clinical yet warm — like a well-lit architecture studio where every element earns its place through function.

## 2. Color Palette & Roles
- **Canvas White** (#F9FAFB) — Primary background surface
- **Pure Surface** (#FFFFFF) — Card and container fill
- **Charcoal Ink** (#18181B) — Primary text. Zinc-950 depth. Never pure black
- **Steel Secondary** (#71717A) — Body text, descriptions, metadata
- **Muted Slate** (#94A3B8) — Tertiary text, timestamps, disabled states
- **Whisper Border** (rgba(226,232,240,0.5)) — Card borders, 1px structural lines
- **Diffused Shadow** (rgba(0,0,0,0.05)) — Card elevation. 40px blur, -15px offset

### Accent Selection (Pick ONE per project)
- **Emerald Signal** (#10B981) — Growth, success, positive data
- **Electric Blue** (#3B82F6) — Productivity, SaaS, developer tools
- **Deep Rose** (#E11D48) — Creative, editorial, fashion
- **Amber Warmth** (#F59E0B) — Community, social, warm-toned

### Banned Colors
- Purple/Violet neon gradients — "AI Purple" aesthetic
- Pure Black (#000000) — always Off-Black or Zinc-950
- Oversaturated accents above 80% saturation
- Mixed warm/cool gray systems within one project

## 3. Typography Rules
- **Display:** `Geist`, `Satoshi`, `Cabinet Grotesk`, or `Outfit` — Track-tight (`-0.025em`), fluid scale, weight-driven hierarchy (700-900). Leading compressed (`1.1`). `Inter` is BANNED.
- **Body:** Same family weight 400 — Relaxed leading (`1.65`), 65ch max-width, Steel Secondary (#71717A)
- **Mono:** `Geist Mono` or `JetBrains Mono` — Code blocks, metadata, timestamps
- **Scale:** Display `clamp(2.25rem, 5vw, 3.75rem)`. Body `1rem/1.125rem`. Mono `0.8125rem`

### Banned Fonts
- `Inter` — banned in premium/creative contexts
- Generic serif (`Times New Roman`, `Georgia`, `Garamond`) — use `Fraunces`, `Instrument Serif` only if needed
- Serif always banned in dashboards or software UIs

## 4. Component Stylings
* **Buttons:** Flat surface, no outer glow. Primary: accent fill, white text. Secondary: ghost/outline. Active: `-1px translateY` or `scale(0.98)`. Hover: subtle background shift.
* **Cards:** Rounded corners (`2.5rem`). Pure white fill. Whisper border. Diffused shadow. Internal padding `2rem-2.5rem`. Used ONLY when elevation communicates hierarchy.
* **Inputs:** Label above input. Error text below in Deep Rose. Focus ring in accent color, `2px` offset. Standard `0.5rem` gap.
* **Navigation:** Sleek, sticky. Icons scale on hover. No hamburger on desktop.
* **Loaders:** Skeletal shimmer matching layout dimensions. Never circular spinners.
* **Empty States:** Composed illustration or icon composition with guidance text.
* **Error States:** Inline, contextual. Red accent underline or border. Clear recovery action.

## 5. Hero Section
- **Inline Image Typography:** Embed small photos between words in headlines — images inline at type-height, rounded.
- **No Overlapping:** Text never overlaps images. Every element has its own clear spatial zone.
- **No Filler Text:** "Scroll to explore", "Swipe down", scroll arrows — all BANNED.
- **Asymmetric Structure:** Centered Hero layouts BANNED at high variance. Use Split Screen, Left-Aligned, or Asymmetric Whitespace.
- **CTA Restraint:** Maximum one primary CTA button.

## 6. Layout Principles
- **Grid-First:** CSS Grid for all structural layouts. Never flexbox percentage math.
- **No Overlapping:** Elements never overlap each other. Clean spatial separation.
- **Feature Sections:** "3 equal cards" pattern BANNED. Use 2-column Zig-Zag, asymmetric Bento grids.
- **Containment:** All content within `max-width: 1400px`, centered.
- **Full-Height:** Use `min-height: 100dvh` — never `height: 100vh`.

## 7. Responsive Rules
- **Mobile-First Collapse (< 768px):** All multi-column layouts collapse to single column.
- **No Horizontal Scroll:** Horizontal overflow on mobile is critical failure.
- **Typography Scaling:** Headlines via `clamp()`. Body text minimum `1rem`.
- **Touch Targets:** All interactive elements minimum `44px` tap target.
- **Navigation:** Desktop nav collapses to clean mobile menu.
- **Testing Viewports:** 375px, 390px, 768px, 1024px, 1440px

## 8. Motion & Interaction (Code-Phase Intent)
- **Physics Engine:** Spring-based. `stiffness: 100, damping: 20`. No linear easing.
- **Perpetual Micro-Loops:** Pulse on status dots, Typewriter on search bars, Float on icons, Shimmer on loaders.
- **Staggered Orchestration:** Cascade delays (`animation-delay: calc(var(--index) * 100ms)`).
- **Hardware Rules:** Animate ONLY `transform` and `opacity`. Never `top`, `left`, `width`, `height`.
- **Performance:** CPU-heavy animations isolated in leaf components. Target 60fps.

## 9. Anti-Patterns (Banned)
- No emojis anywhere in UI, code, or alt text
- No `Inter` font — use `Geist`, `Outfit`, `Cabinet Grotesk`, `Satoshi`
- No generic serif fonts — use distinctive modern serifs only if needed
- No pure black (`#000000`) — Off-Black or Zinc-950 only
- No neon outer glows or default box-shadow glows
- No oversaturated accents above 80%
- No excessive gradient text on large headers
- No custom mouse cursors
- No overlapping elements — clean spatial separation always
- No 3-column equal card layouts for features
- No centered Hero sections (at high variance)
- No filler UI text: "Scroll to explore", "Swipe down", scroll arrows — all BANNED
- No generic names: "John Doe", "Acme", "Nexus"
- No fake round numbers: `99.99%`, `50%` — use `47.2%`, `+1 (312) 847-1928`
- No AI copywriting clichés: "Elevate", "Seamless", "Unleash", "Next-Gen"
- No broken Unsplash links — use `picsum.photos/seed/{id}/800/600`
- No generic `shadcn/ui` defaults — customize radii, colors, shadows
- No `z-index` spam — use only for Navbar, Modal, Overlay contexts
- No `h-screen` — always `min-h-[100dvh]`
- No circular loading spinners — skeletal shimmer only
