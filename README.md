# skills

A collection of agent skills that extend capabilities across planning, development, and tooling.

---

## Naming convention

Every skill in this repo is named `<verb>-<object>[-<platform>]`. The prefix is a closed set of five verbs, and it answers one question: **what does this skill do to you?**

| prefix | mode | read-only? |
|---|---|---|
| `find-` | sweeps for candidates, returns a ranked list | yes |
| `fix-` | diagnoses one class of bug and repairs it | no |
| `rules-` | normative reference; model-invoked background knowledge | n/a |
| `review-` | audits existing code against a standard, returns findings | yes |
| `make-` | produces an artifact | no |

`-mobile` is the only suffix, and it means React Native + Expo on iOS. Every `-mobile` skill has a web sibling with the same stem, and the two cross-reference each other.

Two rules that keep the set honest:

- **The prefix is a promise about side effects.** A `find-` or `review-` skill that edits files is misnamed.
- **One prefix per skill.** If a skill needs two verbs, it's two skills.

---

## My skills

### find — search and propose

**`find-animations`** — sweep a **web** UI for moments that don't animate but should, and reject everything that shouldn't. Read-only: it proposes motion with exact curves and durations, it doesn't implement. Built on Emil Kowalski's ["You Don't Need Animations"](https://emilkowal.ski/ui/you-dont-need-animations) — a filter as much as a finder, with a four-question gate (frequency, purpose, speed, function), a required "rejected candidates" section, and a hard cap of 5–7 suggestions.

```
/find-animations
```

**`find-animations-mobile`** — the same skill for **React Native + Expo on iOS**. Adds the mobile premise that iOS already animates most of what matters: a system-owned table (native-stack pushes, edge-swipe back, sheet detents, tab switches, `RefreshControl`, native alerts) that is rejected before the gate, a UI-thread test as part of the function question, Reanimated/gesture-handler recipes with exact `dampingRatio` + `duration` configs, `expo-haptics` as a co-channel, and a mandatory Reduce Motion check (RN doesn't suppress motion automatically). Pairs with `rules-apple-mobile`.

```
/find-animations-mobile
```

**`find-library`** — a lookup skill for **web**: name a task, get one library. Curated and opinionated, covering UI primitives (base-ui, shadcn/ui, cmdk, Sonner), motion (motion, NumberFlow), data display (TanStack Table, recharts, Tiptap), interaction (dnd kit, Virtuoso), state & styling (zustand, TanStack Query, nuqs, clsx/cva/tailwind-merge), forms (react-hook-form + zod), backend (Drizzle, Better Auth, Resend, Trigger.dev), dates (Temporal over date-fns), and tooling (Vite, Vitest, Playwright, Biome). Includes a `decisions.md` for the contested calls and a "common mismatches" list that catches `useEffect`+`fetch`, filter state outside the URL, and dayjs in greenfield code. UI spine adapted from [Emil Kowalski's pick-ui-library](https://github.com/emilkowalski/skills/blob/main/skills/pick-ui-library/SKILL.md).

```
/find-library
```

**`find-library-mobile`** — the same skill for **React Native + Expo on iOS**. Covers foundation (Expo Router, native-stack, safe-area-context), lists (FlashList v2, Legend List), sheets (`formSheet` before a sheet library, `@gorhom/bottom-sheet` when it's earned), styling (Unistyles 3 vs. NativeWind), motion (Reanimated, Moti, gesture-handler, expo-haptics), the four-way storage split (SecureStore / MMKV / expo-sqlite / AsyncStorage), keyboard (`react-native-keyboard-controller`), device capabilities, and EAS/Sentry/Maestro. Carries two extra biases: prefer the Expo SDK module, and prefer native-backed over hand-rolled JS — so several answers are deliberately *"no library"*. Pairs with `rules-apple-mobile`.

```
/find-library-mobile
```

### fix — diagnose and repair

**`fix-z-index`** — diagnostic decision tree for z-index, stacking context, and overlay bugs. Almost every "z-index doesn't work" issue traces to one of five root causes encoded in the tree.

```
/fix-z-index
```

### rules — normative reference

**`rules-apple`** — Apple's Human Interface Guidelines translated for the web (CSS/HTML/JS/React), for frontend and design engineers. Complete standalone skill covering foundations (color, dark mode, materials/translucency, typography, layout, accessibility, RTL, writing), patterns (onboarding, loading/skeletons, feedback, modality, inline validation, delayed sign-in, search, settings), components (buttons, sheets, popovers, alerts, toggles, tab bars, toolbars, sidebars…), inputs (gestures, keyboard, pointer/hover, focus), motion (springs, velocity, interruptibility, reduced-motion), and web-relevant Apple technologies (Sign in with Apple, Apple Pay on the Web). Every rule works as build guidance and as a review check.

```
/rules-apple
```

**`rules-apple-mobile`** — Apple's Human Interface Guidelines for iPhone/iOS, translated for React Native + Expo. Complete standalone skill for building native iOS apps: navigation (React Navigation native-stack, large titles, edge-swipe back), tab bars, sheets & detents, alerts/action sheets, forms, lists (FlatList/FlashList, swipe-to-delete, pull-to-refresh), safe areas & Dynamic Island, Dynamic Type, dark mode, SF Symbols, gestures (gesture-handler), motion (reanimated), haptics, permissions, push notifications, and the App Store review requirements that block release (Sign in with Apple, account deletion, ATT). Every rule = Apple HIG rule + the exact RN/Expo API + the common RN mistake.

```
/rules-apple-mobile
```

**`rules-react-state`** — expert guidance for React state management: Zustand, React Query, React Context, and XState. Categorises state as server, global client, injected, or event-driven, then picks the right tool for each.

```
npx skills add sharqiewicz/skills/rules-react-state
```

**`rules-git`** — team git workflow: branching strategy, commit discipline, rebase/merge rules, tag management, configuration.

```
npx skills add sharqiewicz/skills/rules-git
```

### review — audit against a standard

**`review-cognitive-load`** — reviews code for extraneous complexity — the kind caused by how code is written, not by the inherent difficulty of the problem — and suggests concrete simplifications.

```
npx skills add sharqiewicz/skills/review-cognitive-load
```

**`review-effects`** — detects misused `useEffect` hooks and replaces each with the correct React pattern, based on React's "You Might Not Need an Effect" guidance.

```
npx skills add sharqiewicz/skills/review-effects
```

### make — produce an artifact

**`make-skill`** — scaffolds a new skill from scratch, or audits an existing one against the canonical `SKILL.md` structure and fixes the gaps.

```
npx skills add sharqiewicz/skills/make-skill
```

**`make-ticket`** — turns ideas, conversations, and plans into structured, testable work. Three flows: draft a single GitHub Issue in User Story format with Definition of Ready/Done; synthesize the current conversation into a PRD; break a plan or PRD into independently-grabbable tracer-bullet issues.

```
npx skills add sharqiewicz/skills/make-ticket
```

### In progress

Not yet installed — see `in-progress/`.

- **`rules-design-engineering`** — design engineering principles for polished, accessible, performant web interfaces: animation, forms, touch, color, typography, audio feedback, accessibility, Tailwind state cascading.
- **`rules-motion-layout`** — Motion (Framer Motion successor) layout animations: `layout`, `layoutId`, shared element transitions, `AnimatePresence`, `LayoutGroup`, scale correction.
- **`rules-web-patterns`** — architecture, rendering, and performance patterns from patterns.dev.

---

## External skills

### React

**React Doctor** — https://www.react.doctor/

```
npx react-doctor@latest
```

**Vercel skills**

```
npx skills add vercel-labs/agent-skills
```

- [**React view transitions**](https://github.com/vercel-labs/agent-skills/tree/main/skills/react-view-transitions) — smooth, native-feeling animations using React's View Transition API (`<ViewTransition>`, `addTransitionType`, CSS view transition pseudo-elements).
- [**React best practices**](https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices) — React and Next.js performance optimization guidelines from Vercel Engineering.
- [**Composition patterns**](https://github.com/vercel-labs/agent-skills/tree/main/skills/composition-patterns) — React composition patterns that scale; compound components, render props, context providers, component architecture. Includes React 19 API changes.

### Design engineering

**Web interface guidelines** — review UI code for Web Interface Guidelines compliance:

- [https://github.com/vercel-labs/agent-skills/blob/main/skills/web-design-guidelines](https://github.com/vercel-labs/agent-skills/blob/main/skills/web-design-guidelines)

```
npx skills add vercel-labs/agent-skills
```

**OKLCH** — OKLCH color space for web projects. Convert hex/rgb/hsl to oklch, generate palettes, check contrast, handle gamut boundaries, and theme with Tailwind v4:

- [https://github.com/jakubkrehel/oklch-skill/tree/main/skills/oklch-skill](https://github.com/jakubkrehel/oklch-skill/tree/main/skills/oklch-skill)

```
npx skills add jakubkrehel/oklch-skill
```

**Impeccable** — deep design knowledge with 18 commands to steer the result:

- [https://github.com/pbakaus/impeccable](https://github.com/pbakaus/impeccable)

```
npx skills add pbakaus/impeccable
```

**review-animations** — https://emilkowal.ski/skill

```
npx skills add emilkowalski/skill
```

**vocabulary** — https://index.how/to/articulate

```
npx skills add index-how/vocabulary
```

**shadcn** — https://ui.shadcn.com/docs/skills

```
npx skills add shadcn/ui
```

### SEO

**Comprehensive SEO** — 20 core sub-skills covering technical SEO, on-page analysis, content quality (E-E-A-T), schema markup, image optimization, sitemap architecture, AI search optimization (GEO), local SEO, and more:

- [https://github.com/AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo)

### Tooling

**Grill me** — interview the user relentlessly about a plan or design until reaching shared understanding. Use when stress-testing a plan or design:

```
npx skills add mattpocock/skills/grill-me
```

**Teach** — https://github.com/mattpocock/skills/tree/main/skills/productivity/teach

```
npx skills add mattpocock/skills/teach
```
