---
name: apple-rules
description: "Apple's Human Interface Guidelines translated for the web (CSS/HTML/JS/React), for frontend and design engineers. Use when building OR reviewing Apple-style interfaces: color & semantic tokens, dark mode, materials/translucency/backdrop-filter, typography & type scale, layout & safe areas, SF-style icons, accessibility, RTL, privacy/permission copy, UX writing — plus UX patterns (onboarding, loading/skeletons, feedback, modality, data entry & inline validation, search, settings, accounts/sign-in, notifications, undo/redo, drag & drop) — components (buttons, sheets, popovers, alerts, action sheets, menus, toggles, sliders, steppers, text fields, pickers, lists & tables, tab bars, toolbars, sidebars, search fields, segmented controls, progress indicators, badges) — inputs (gestures, keyboard, pointer/hover, focus & selection) — motion (springs, velocity, interruptibility, momentum, reduced-motion) — and Apple technologies on the web (Sign in with Apple, Apple Pay on the Web). Triggers on: Apple design, HIG, Human Interface Guidelines, iOS/macOS/iPadOS look, native-feeling web UI, Apple-style component, tap target, 44px, contrast ratio, prefers-color-scheme, prefers-reduced-motion, prefers-reduced-transparency, prefers-contrast, dark mode, backdrop-filter, translucency, vibrancy, Dynamic Type, safe-area-inset, semantic color, sheet, action sheet, popover, alert dialog, segmented control, tab bar, toolbar, sidebar, skeleton screen, inline validation, modal usage, delayed sign-in, Sign in with Apple, Apple Pay web."
---

# Apple HIG (for the web)

Apple's Human Interface Guidelines, distilled and translated into web platform primitives (CSS, HTML, ARIA, Pointer Events, `rem`, media queries, React). Complete and standalone — foundations, patterns, components, inputs, motion, and web-relevant technologies all live here.

Every rule below is written to work **both ways**: as build guidance ("do X") and as a review check ("flag when not X"). Apple's canonical values are in points (pt); on the web, **1pt ≈ 1 CSS px at 1×**, and type scales in `rem`.

## The 7 principles (the reasoning vocabulary)

Apple's current framework (updated June 2026 — this replaces the older Clarity/Deference/Depth and the 8-principle "Delight-as-separate" framings). Use these as the names you reason with; every tactical rule serves one of them.

1. **Purpose** — Make something meaningful. Decide what *not* to build; every feature spends the user's time, attention, and trust.
2. **Agency** — Let people do things their own way. Offer choices, don't force one path; back it with forgiveness (easy undo). "Recovering from the unexpected shouldn't cost people their work."
3. **Responsibility** — Act in people's best interest. Collect only what's needed, be transparent about why, keep data safe. Anticipate misuse.
4. **Familiarity** — Build on what people know. Consistent visuals/interactions, clear feedback on state changes. Break a familiar pattern only if you can prove it's better.
5. **Flexibility** — Adapt to diverse contexts, devices, inputs, and abilities. Accessibility from the start, not bolt-on. Support voice, touch, keyboard, pointer — more input methods = more people can use it.
6. **Simplicity** — Be clear and direct. "Simplicity isn't minimalism" — include just what's necessary, establish hierarchy so the most important thing is the most obvious.
7. **Craft** — Care about every detail. Nothing random — every spacing/timing/alignment value is a deliberate, defensible choice. Shipping isn't the finish line. (**Delight** is a sub-theme of Craft: decide the emotion you want people to feel, and don't mistake delight for decoration.)

## The 4 load-bearing rules (always true, keep in context)

These recur across nearly every HIG article. If you check nothing else, check these.

1. **Interactive targets ≥ 44×44px** (28px absolute floor; 60px in spatial UI). Add hit-slop/padding rather than growing the visual. `[WCAG 2.5.5 / 2.5.8]`
2. **Contrast: 4.5:1** for body text, **3:1** for large (≥18pt/24px or bold) text; aim **7:1** for custom small text in dark mode. `[WCAG 1.4.3]`
3. **Start from the system preference — don't build a competing in-app toggle.** Honor `prefers-color-scheme`, `prefers-reduced-motion`, `prefers-contrast`, `prefers-reduced-transparency` first; a manual override is secondary, never the default source of truth.
4. **Never encode meaning in a single channel** (color alone, motion alone, sound alone). Always pair with icon + shape + text. `[WCAG 1.4.1 / 1.1.1]`

## Platform & input adaptation

Design for the actual **device + input combination** a person is using, not one default mode.

- **Touch** (phone): thumb-reachable controls (middle/bottom), generous targets, quick focused tasks.
- **Pointer** (desktop/trackpad): hover is **additive, never the only path** to an action; precise targets allowed but keep the touch minimum; support keyboard-only workflows and standard shortcuts.
- **Keyboard**: everything reachable via Tab/Enter/Space, no traps; don't override standard shortcuts (Cmd/Ctrl+Z/F/C…).
- On the web: prefer content-driven breakpoints / container queries and logical CSS properties over guessing a device from viewport width.

## Where to look (routing)

| Task | File |
| --- | --- |
| Color, dark mode, materials/translucency, typography, layout/safe-areas, icons, app icons/favicons, images, accessibility, RTL, privacy/permission copy, UX writing, branding, inclusion | [foundations.md](foundations.md) |
| Onboarding, loading, feedback, modality, data entry/validation, search, settings, accounts/sign-in, notifications, undo/redo, drag & drop, collaboration, file management/autosave, offering help/tooltips, full-screen, launching | [patterns.md](patterns.md) |
| Buttons, menus, sheets, popovers, alerts, action sheets, toggles, sliders, steppers, text fields, pickers, lists/tables, tab bars, toolbars, sidebars, search fields, token fields, segmented controls, split views, scroll views, charts, progress, badges, page controls, rating indicators | [components.md](components.md) |
| Gestures, keyboard, pointer/hover hit-slop, focus & selection | [inputs.md](inputs.md) |
| Springs, velocity handoff, interruptibility, momentum, reduced-motion, fps | [motion.md](motion.md) |
| Sign in with Apple, Apple Pay on the Web, ML/GenAI UX methodology | [technologies.md](technologies.md) |
