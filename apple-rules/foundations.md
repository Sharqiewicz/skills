# Foundations

The visual and structural bedrock: color, dark mode, materials, typography, layout, icons, images, accessibility, RTL, privacy, writing, branding, inclusion. Apple values in pt; web equivalent inline. Rules read as build guidance and as review checks.

## Accessibility (the through-line)

- **Never encode meaning in one channel** — pair color with shape/icon/text (status, validation, charts). Watch red-green and blue-orange confusion pairs. `[1.4.1]`
- **Contrast:** 4.5:1 body / 3:1 large (≥18pt/24px or bold). Ship a higher-contrast variant under `prefers-contrast: more`. `[1.4.3]`
- **Targets ≥ 44×44px** (28px floor). Spacing matters as much as size: ~12px padding around bezeled controls, ~24px around icon-only ones, to prevent mis-taps.
- **Support 200% text enlargement** without loss of content/function. Use `rem`, not `px`, for font sizes; never cap containers so they truncate at 200% zoom. `[1.4.4 / 1.4.10]`
- **Never ship body text below ~11pt (≈15px)** equivalent.
- **Keyboard-only navigation** must work; don't override standard shortcuts; visible focus rings; no keyboard traps.
- **Reduce Motion:** replace slides/springs/parallax with fades; drop z-axis and blur animation. `prefers-reduced-motion: reduce`.
- **Don't auto-dismiss on a timer** (toasts/tooltips) — some users need more time; prefer explicit dismissal or generous, adjustable timing.
- **No strobing** (>3 flashes/sec — seizure risk). No autoplay audio/video without a visible stop/pause control.
- Every meaningful icon/image needs a text alternative (`aria-label`); decorative ones get `aria-hidden`.

## Color

- **Reference semantic tokens, never hard-code hex in components.** Use CSS custom properties resolved per theme: `--text-primary`, `--separator`, `--surface-1`. A token adapts across light/dark/contrast; a baked hex doesn't.
- **Never use one color to mean two things** in the same UI; never repurpose a token's semantic meaning (a "background" token as text color).
- **Every color works in light, dark, and increased-contrast.** Ship the pairs; don't compute one from the other.
- **Background hierarchy:** primary/secondary/tertiary surface levels convey nesting → `--surface-1/2/3`.
- **Label hierarchy:** primary/secondary/tertiary/quaternary label colors, decreasing emphasis → `--text-primary…quaternary`.
- **Apply color sparingly** — put accent color on the primary CTA, not on many controls at once (visual competition).
- Wide gamut where supported: `color(display-p3 …)` with an sRGB fallback.
- Color carries **cultural** meaning (red = danger vs. luck) — validate per locale if you localize.
- Prefer a single derived **accent color** (`--accent`) over spraying brand colors everywhere.

## Dark Mode

- **Respect the system preference** (`prefers-color-scheme: dark`). A manual override is allowed but secondary — default to the system, don't make the in-app toggle the source of truth.
- **Dark ≠ inverted.** Light and dark are independently designed pairs. Never `filter: invert()`.
- **Contrast in dark mode:** ≥4.5:1, aim **7:1 for small custom text** — dark backgrounds hide low-contrast text.
- **Convey z-order by luminance:** base surfaces are dimmer/receded, elevated surfaces (modals, popovers) are brighter → `--surface-base` vs `--surface-elevated`.
- **Soften pure-white** embedded content (images with white backgrounds "glow" against dark chrome) — tint/darken slightly.
- **Test the compound case:** dark mode + `prefers-contrast: more` + `prefers-reduced-transparency` together — they stack and can crush contrast.

## Materials & translucency

Two-layer mental model: a floating **controls/chrome** layer (sticky headers, toolbars, tab bars) above a **content** layer that visibly scrolls underneath.

- **Translucency only on functional chrome** (nav, toolbar, sheet) — not on general content cards. Overusing blur is distracting.
- Approximate with `backdrop-filter: blur()` + a semi-transparent background so content peeks through — not an opaque bar consuming a fixed strip.
- **More opaque/blurred variant** for text-heavy overlays (alerts, sidebars, popovers) where legibility rules; **more transparent variant** over rich media where context matters. Thicker material = better contrast; thinner = better context.
- **Scrim over bright/media backgrounds:** ~35% dark scrim (`rgba(0,0,0,.35)`) behind glass text for legibility.
- **Vibrant/adaptive foreground** over materials — don't hard-code white; test against your busiest expected background.
- **`prefers-reduced-transparency: reduce`** → fall back to a solid, opaque background; drop the blur.
- **Scroll edge effect, not a hard 1px divider:** the header gains a blur/shadow only after the user scrolls past the top, where floating chrome overlaps content.

```css
.toolbar { background: rgba(255,255,255,.6); backdrop-filter: blur(20px) saturate(180%); }
@media (prefers-reduced-transparency: reduce) { .toolbar { background: #fff; backdrop-filter: none; } }
```

## Typography

- **A semantic type scale of named tokens**, each bundling size + weight + line-height — not bare `font-size` values. Apple's canonical scale (default "Large"), a good benchmark:

  | Style | Weight | Size | Line height |
  | --- | --- | --- | --- |
  | Large Title | Regular | 34 | 41 |
  | Title 1 / 2 / 3 | Regular | 28 / 22 / 20 | 34 / 28 / 25 |
  | Headline | Semibold | 17 | 22 |
  | Body / Callout | Regular | 17 / 16 | 22 / 21 |
  | Subhead / Footnote | Regular | 15 / 13 | 20 / 18 |
  | Caption 1 / 2 | Regular | 12 / 11 | 16 / 13 |

  Line-height ≈ **1.25–1.3×** the size across the scale.
- **No weights below 400 for body** — avoid Ultralight/Thin/Light, especially under ~16px.
- **Tracking is size-specific:** tighten large display text (`letter-spacing: -0.02em`), keep body near `0`. A single fixed `letter-spacing` is wrong somewhere.
- **`rem` for font sizes** so browser zoom / user text-size settings work; not everything must scale uniformly — chrome (tab labels) can stay fixed while body content scales.
- **Prevent truncation at large sizes** — let labels wrap, don't ellipsis-clip. At large scale, switch inline row layouts to **stacked**, reduce columns.
- **Minimize typefaces** — 1 display + 1 body is the ceiling. Prefer `system-ui` before a custom face; it ships optical sizing and legibility tuning.
- **Keep hierarchy order** regardless of scale — most important stays toward the top.

```css
:root { font: 100%/1.5 system-ui, sans-serif; }
.display { font-size: clamp(2rem,5vw,4rem); line-height: 1.05; letter-spacing: -0.02em; font-optical-sizing: auto; }
```

## Layout

- **Group related items** (spacing, shared background, separators); keep controls visually distinct from content.
- **Most important info gets the most space**; push secondary detail to another view.
- **Extend backgrounds/content to the edges**; layer controls above content (z-index), don't share their plane.
- **Reading-order = importance:** top and leading (start) side — and this **flips in RTL**, so never hard-code "important = left." Use logical properties (`margin-inline-start`, `inset-inline-start`), not `left`/`right`.
- **Safe areas:** `env(safe-area-inset-*)` so content clears notches/home-indicators.
- **Content-driven breakpoints:** design the full layout first and collapse to compact only when it no longer fits (container queries), rather than guessing a device breakpoint early.
- **Never distort aspect ratio** to fit — `object-fit: contain/cover`, not independent width/height.
- **Progressive disclosure** — signal there's more (peek, "show more", scroll affordance) instead of silently truncating.
- Apple's spacing vocabulary (useful precedent for an 8pt-style scale): 12 / 24 control padding, 40 gutter, 60 / 80 TV safe margins, 100 min vertical.
- **Test every breakpoint** you support, including the largest and smallest.

## Icons

- **Radical simplicity**, one concept, familiar metaphor; consistent size/detail/**stroke weight**/perspective across the set.
- **Match icon weight to adjacent text weight**; size icons in `em` tied to `--font-size` so they scale with the text they sit beside.
- **Optical over geometric alignment** — asymmetric glyphs (download arrow, play triangle) need internal padding/nudging; don't trust the `viewBox` center.
- **SVG over raster**; color via `currentColor` (monochrome), optional opacity-hierarchy or multi-tone variant for depth.
- **No text inside icons** (won't localize, illegible small). Prefer gender-neutral, culturally portable imagery.
- Filled vs. outline is a legitimate state axis (outline = default, filled = selected/active, e.g. tab bars).

## Images

- **Density variants:** `srcset`/`image-set()` with `1x/2x/3x`; `sizes`/`<picture>` for responsive.
- **Format by content:** photos → AVIF/WebP (or JPEG); flat/vector art → SVG; embed the color profile (sRGB or explicit P3).
- Design source art at the lowest resolution first, scale up (keeps control points on whole pixels).
- **Always QA on real devices**, not just the design tool.

## Right to Left

- **Flip layout wholesale** via logical properties + `dir="rtl"` / `:dir()`; leading/trailing is the mental model.
- **Numerals never internally reverse** ("541", phone numbers stay); only the order of separate numeral groups flips. Use `unicode-bidi: isolate` for embedded numbers/data.
- **Flip** directional/progress controls (sliders, progress, next/back) and reading-direction icons; **don't flip** photos, logos, universal symbols (checkmark), real-world-direction icons ("turn right"), or handedness objects (scissors).
- Paragraphs (3+ lines) align to *their own* language, not the surrounding context.
- Mixed script: bump RTL font-size ~+2pt next to all-caps Latin.

## Privacy & permission copy

- **Request access only when the feature needs it**, at the moment it's invoked — not preemptively on load.
- **Justification copy = an active, specific, complete sentence** ending in a period, saying exactly why. ✅ "The app records at night to detect snoring." ❌ "Microphone access is needed for a better experience."
- **Custom pre-permission screen:** exactly one neutral button ("Continue"), never mimicking the real "Allow" button; no fake incentives, screenshots of the real dialog, or arrows pointing at "Allow" (dark patterns).
- Never store secrets in plaintext (`localStorage`); prefer httpOnly secure cookies / WebAuthn passkeys over custom password schemes. Process on-device where feasible.

## Writing (microcopy)

- **One voice, tone varies by context** (calm for a health alert, light for a win).
- **Verb-first action labels** ("Send", not "Let's do it!"). **Never "Click here"** — descriptive link text (screen readers navigate by link list). `[2.4.4]`
- **Consistent capitalization per element type**; consistent verbs across a flow ("Continue"… "Done").
- **Strip first-person plural from system/errors:** "Unable to load content", not "We're having trouble…". Use "your" sparingly ("Favorites" > "Your Favorites").
- **Error formula:** state the actionable fix, not the rule broken, no blame, no "oops". ❌ "That password is too short" → ✅ "Choose a password with at least 8 characters."
- **Placeholders show a concrete example** ("name@example.com"), not "Enter your email". Validation instructs, doesn't scold.
- **Empty states need a clear next action**, not a bare "Nothing here".
- Match the verb to the input ("tap" on touch, "click" on pointer) or use neutral "select"/"choose".

## Branding

- **Defer to content** — resist showing your logo throughout the chrome; people know what app they're in.
- **One accent color** the UI derives from; custom fonts for headlines, system/optimized font for body.
- **No splash screen as a branding moment** — it's too brief; make a real welcome/onboarding screen if you want one.
- Familiar, standard placement of components makes even a stylized brand feel comfortable.

## Inclusion

- Address people as **"you"**; define/avoid jargon; avoid idioms/colloquialisms (hard to translate, sometimes exclusionary).
- **Avoid unnecessary gendering** in copy/imagery; if collecting gender, offer nonbinary / self-identify / decline, plus optional pronouns.
- Represent human diversity; avoid stereotyped occupation pairings and culturally-specific examples ("first car"). People-first disability language. Inclusive copy is also more translatable.
