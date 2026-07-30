# rules-apple

Apple's **Human Interface Guidelines**, distilled and translated for the **web** (CSS / HTML / JS / React) — a complete, standalone skill for frontend and design engineers. Every rule works in **two modes**: as build guidance ("do X") and as a review check ("flag when not X").

Apple's canonical values are in points (pt); on the web, **1pt ≈ 1 CSS px at 1×**, and type scales in `rem`.

## What's inside

Progressive-disclosure structure: `SKILL.md` is always loaded and routes to the reference file for your task.

| File | Covers |
| --- | --- |
| `SKILL.md` | The 7 Apple principles · 4 load-bearing rules (44px targets, 4.5:1/3:1 contrast, system-prefs-first, never one channel) · platform/input adaptation · routing table |
| `foundations.md` | Color & semantic tokens · dark mode · materials/translucency · typography & type scale · layout & safe areas · icons · images · accessibility · RTL · privacy/permission copy · UX writing · branding · inclusion |
| `patterns.md` | Onboarding · loading/skeletons · feedback · modality · data entry & inline validation · search · settings · accounts/sign-in · notifications · undo/redo · drag & drop · full-screen · launching |
| `components.md` | Buttons · menus · sheets · popovers · alerts · action sheets · toggles · sliders · steppers · text fields · pickers · lists/tables · tab bars · toolbars · sidebars · search fields · segmented controls · progress · badges (each mapped to its web/ARIA equivalent) |
| `inputs.md` | Gestures · keyboard · pointer/hover hit-slop · focus & selection |
| `motion.md` | Springs · velocity handoff · interruptibility · momentum projection · reduced-motion · fps |
| `technologies.md` | Sign in with Apple · Apple Pay on the Web · ML/GenAI UX methodology |

## How to invoke it

**Automatically** — Claude pulls the skill in when your prompt matches its triggers (Apple/iOS/macOS look, HIG, tap target, dark mode, `backdrop-filter`, sheet, modal, inline validation, `prefers-*`, …). You don't have to name it.

**Explicitly** — type `/rules-apple` to force the Apple lens. Use this when your prompt is generic ("review this component") but you want it judged against Apple's rules specifically.

> Rule of thumb: let it auto-fire for obvious cases; invoke explicitly when you want to guarantee this skill's lens.

## Using it — build mode

Name the component + your constraints (framework, mobile vs. desktop):

```
/rules-apple build a bottom sheet with medium/large detents, a grabber,
and swipe-to-dismiss. React + Tailwind.
```

You get the detent/snap-point rules, one-sheet-at-a-time, focus trapping + restore, and the reduced-motion fallback — baked in, not forgotten.

Targeted questions don't need the slash command — just ask, and the skill auto-fires:

```
What's the minimum tap target, and how do I add it without growing
the button visually?
```

## Using it — review mode

The mode most people underuse. Because every rule is also a check, point it at a file or PR:

```
/rules-apple review src/components/Dialog.tsx against Apple's HIG
```

Typical flags: destructive action styled as the primary button · modal missing focus restore · color-only state · `backdrop-filter` with no `prefers-reduced-transparency` fallback · tap targets under 44px · placeholder used as the only label.

Design decisions work too:

```
Should "delete draft" be an alert, an action sheet, or a modal?
```

## Combining with other skills

rules-apple is self-contained but stacks well:

- **+ rules-design-engineering** — rules-apple for *Apple's opinion* (semantic tokens, materials, dark-mode elevation); `rules-design-engineering` for *generic web craft* (concentric radii, APCA contrast, virtualization).
- **+ oklch-skill** — rules-apple sets the color rules ("semantic tokens, 4.5:1, P3 + sRGB fallback"); oklch generates the actual palette.
- **+ shadcn** — scaffold with shadcn, then "make these components follow Apple's HIG."
- **+ /code-review** — build with rules-apple, then run code-review for logic/bugs the design skill doesn't hunt for.

## A workflow that sticks

**New UI:**
1. Build → `/rules-apple`, naming the component + constraints.
2. Self-review → "now review what you just built against the HIG" (dual-mode audits its own output).
3. Ship-check → `/code-review` for logic/bugs.

**Existing UI:** point rules-apple at the file/PR in review mode first, fix the flags, done. Running it across your existing components once gives you a punch-list.

## Two habits that matter most

- **Use review mode** — it quietly catches the 44px targets and missing focus restores across a whole codebase.
- **State the context in your prompt** — "mobile web, touch-first" vs. "desktop, keyboard-heavy" changes which rules apply (targets, hover-is-additive, keyboard nav). The platform-adaptation section keys off exactly that.

## Sourcing & maintenance

Rules are drawn from Apple's current HIG (framework updated June 2026 — 7 principles, Delight folded under Craft). The HIG site is a client-rendered SPA: plain fetches return only the page shell. To re-verify a number, fetch the **DocC JSON API** (`https://developer.apple.com/tutorials/data/design/human-interface-guidelines/<slug>.json`) or use an `r.jina.ai` render proxy — not a plain `WebFetch`.
