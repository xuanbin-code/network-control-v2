---
name: stitch-design-taste
description: Semantic Design System Skill for Google Stitch. Generates agent-friendly DESIGN.md files that enforce premium, anti-generic UI standards — strict typography, calibrated color, asymmetric layouts, perpetual micro-motion, and hardware-accelerated performance.
---

# Stitch Design Taste — Semantic Design System Skill

## Overview
This skill generates `DESIGN.md` files optimized for Google Stitch screen generation. It translates the battle-tested anti-slop frontend engineering directives into Stitch's native semantic design language.

The generated `DESIGN.md` serves as the **single source of truth** for prompting Stitch to generate new screens that align with a curated, high-agency design language.

## Prerequisites
- Access to Google Stitch via [labs.google/stitch](https://labs.google/stitch)
- Optionally: Stitch MCP Server for programmatic integration

## The Goal
Generate a `DESIGN.md` file that encodes:
1. **Visual atmosphere** — the mood, density, and design philosophy
2. **Color calibration** — neutrals, accents, and banned patterns with hex codes
3. **Typographic architecture** — font stacks, scale hierarchy, and anti-patterns
4. **Component behaviors** — buttons, cards, inputs with interaction states
5. **Layout principles** — grid systems, spacing philosophy, responsive strategy
6. **Motion philosophy** — animation engine specs, spring physics, perpetual micro-interactions
7. **Anti-patterns** — explicit list of banned AI design clichés

## Analysis & Synthesis Instructions

### 1. Define the Atmosphere
Evaluate the target project's intent. Use evocative adjectives:
- **Density:** "Art Gallery Airy" (1–3) → "Daily App Balanced" (4–7) → "Cockpit Dense" (8–10)
- **Variance:** "Predictable Symmetric" (1–3) → "Offset Asymmetric" (4–7) → "Artsy Chaotic" (8–10)
- **Motion:** "Static Restrained" (1–3) → "Fluid CSS" (4–7) → "Cinematic Choreography" (8–10)

Default baseline: Variance 8, Motion 6, Density 4. Adapt dynamically based on user's vibe description.

### 2. Map the Color Palette
For each color provide: **Descriptive Name** + **Hex Code** + **Functional Role**.

**Mandatory constraints:**
- Maximum 1 accent color. Saturation below 80%
- The "AI Purple/Blue Neon" aesthetic is strictly BANNED
- Use absolute neutral bases (Zinc/Slate) with high-contrast singular accents
- Stick to one palette for the entire output
- Never use pure black (`#000000`)

### 3. Establish Typography Rules
- **Display/Headlines:** Track-tight, controlled scale. Hierarchy through weight and color, not just massive size
- **Body:** Relaxed leading, max 65 characters per line
- **Font Selection:** `Inter` is BANNED for premium/creative contexts. Use `Geist`, `Outfit`, `Cabinet Grotesk`, or `Satoshi`
- **Serif Ban:** Generic serif fonts BANNED. If serif is needed, use only distinctive modern serifs: `Fraunces`, `Gambarino`, `Editorial New`, or `Instrument Serif`. Serif always BANNED in dashboards or software UIs
- **Dashboard Constraint:** Use Sans-Serif pairings exclusively
- **High-Density Override:** When density exceeds 7, all numbers must use Monospace

### 4. Define the Hero Section
- **Inline Image Typography:** Embed small photos or visuals between words in the headline
- **No Overlapping:** Text never overlaps images or other text
- **No Filler Text:** "Scroll to explore", "Swipe down", scroll arrows are BANNED
- **Asymmetric Structure:** Centered Hero layouts BANNED when variance exceeds 4
- **CTA Restraint:** Maximum one primary CTA. No secondary "Learn more" links

### 5. Describe Component Stylings
- **Buttons:** Tactile push feedback on active state. No neon outer glows
- **Cards:** Use ONLY when elevation communicates hierarchy. Tint shadows to background hue
- **Inputs/Forms:** Label above input, helper text optional, error text below
- **Loading States:** Skeletal loaders matching layout dimensions — no circular spinners
- **Empty States:** Composed compositions indicating how to populate data
- **Error States:** Clear, inline error reporting

### 6. Define Layout Principles
- No overlapping elements — every element occupies its own clear spatial zone
- Centered Hero sections BANNED when variance exceeds 4
- "3 equal cards" feature row BANNED — use 2-column Zig-Zag, asymmetric grid, or horizontal scroll
- CSS Grid over Flexbox math — never use `calc()` percentage hacks
- Contain layouts using max-width constraints (e.g., 1400px centered)
- Full-height sections must use `min-h-[100dvh]` — never `h-screen`

### 7. Define Responsive Rules
- **Mobile-First Collapse (< 768px):** All multi-column layouts collapse to single column
- **No Horizontal Scroll:** Horizontal overflow on mobile is critical failure
- **Typography Scaling:** Headlines via `clamp()`. Body text minimum `1rem`/`14px`
- **Touch Targets:** All interactive elements minimum `44px` tap target
- **Navigation:** Desktop nav collapses to clean mobile menu

### 8. Encode Motion Philosophy
- **Spring Physics default:** `stiffness: 100, damping: 20` — premium, weighty feel. No linear easing
- **Perpetual Micro-Interactions:** Every active component has an infinite loop state
- **Staggered Orchestration:** Cascade delays for waterfall reveals
- **Performance:** Animate exclusively via `transform` and `opacity`

### 9. List Anti-Patterns (AI Tells)
- No emojis anywhere
- No `Inter` font
- No generic serif fonts
- No pure black (`#000000`)
- No neon/outer glow shadows
- No oversaturated accents
- No excessive gradient text on large headers
- No custom mouse cursors
- No overlapping elements
- No 3-column equal card layouts
- No generic names ("John Doe", "Acme", "Nexus")
- No fake round numbers (`99.99%`, `50%`)
- No AI copywriting clichés ("Elevate", "Seamless", "Unleash", "Next-Gen")
- No filler UI text: "Scroll to explore", "Swipe down", scroll arrows
- No broken Unsplash links — use `picsum.photos` or SVG avatars
- No centered Hero sections (for high-variance projects)

## Output Format (DESIGN.md Structure)

```markdown
# Design System: [Project Title]

## 1. Visual Theme & Atmosphere
(Evocative description of mood, density, variance, and motion intensity.)

## 2. Color Palette & Roles
- **Canvas White** (#F9FAFB) — Primary background surface
- **Pure Surface** (#FFFFFF) — Card and container fill
- **Charcoal Ink** (#18181B) — Primary text
- **Muted Steel** (#71717A) — Secondary text
- **Whisper Border** (rgba(226,232,240,0.5)) — Structural lines
- **[Accent Name]** (#XXXXXX) — Single accent for CTAs

## 3. Typography Rules
- **Display:** [Font Name] — Track-tight, controlled scale
- **Body:** [Font Name] — Relaxed leading, 65ch max-width
- **Mono:** [Font Name] — Code, metadata, timestamps

## 4. Component Stylings
* **Buttons:** Flat, no outer glow. Tactile -1px translate on active
* **Cards:** Generously rounded (2.5rem). Diffused whisper shadow
* **Inputs:** Label above, error below. Focus ring in accent color
* **Loaders:** Skeletal shimmer matching layout dimensions

## 5. Layout Principles
(Grid-first responsive architecture. Asymmetric Hero splits. Strict single-column collapse.)

## 6. Motion & Interaction
(Spring physics. Staggered cascade reveals. Perpetual micro-loops. Hardware-accelerated transforms.)

## 7. Anti-Patterns (Banned)
(Explicit list of forbidden patterns.)
```

## Best Practices
- **Be Descriptive:** "Deep Charcoal Ink (#18181B)" — not just "dark text"
- **Be Functional:** Explain what each element is used for
- **Be Consistent:** Same terminology throughout
- **Be Precise:** Include exact hex codes, rem values, pixel values
- **Be Opinionated:** Enforce a specific, premium aesthetic

## Tips for Success
1. Start with the atmosphere — understand the vibe before detailing tokens
2. Look for patterns — identify consistent spacing, sizing, and styling
3. Think semantically — name colors by purpose, not just appearance
4. Consider hierarchy — document how visual weight communicates importance
5. Encode the bans — anti-patterns are as important as the rules themselves
