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

`-mobile` is the only suffix, and it means React Native + Expo on iOS. Every `-mobile` skill names its web sibling, which may be an external skill (e.g. `review-animations-mobile` ↔ `/review-animations`). When the sibling is my own skill, the two cross-reference each other.

Two rules that keep the set honest:

- **The prefix is a promise about side effects.** A `find-` or `review-` skill that edits files is misnamed.
- **One prefix per skill.** If a skill needs two verbs, it's two skills.

---

## My skills

The whole repo is one Claude Code plugin. Install it once and every skill below is invoked as `/sharqiewicz:<skill>`:

```
/plugin marketplace add sharqiewicz/skills
/plugin install sharqiewicz@sharqiewicz
```

Want a single skill instead? `npx skills add sharqiewicz/skills/<skill>` (it gets a bare name, `/<skill>`, and updates with `npx skills update`). **Never do both for the same skill**: an npx copy and the plugin copy both load and compete.

On my own machine the repo is symlinked as `~/.claude/skills/sharqiewicz`, which loads it as the `sharqiewicz@skills-dir` plugin, so every edit here is live without reinstalling. Don't delete that symlink.

### find — search and propose

**`find-animations`** — sweep a **web** UI for moments that don't animate but should, and reject everything that shouldn't. Read-only: it proposes motion with exact curves and durations, it doesn't implement. Built on Emil Kowalski's ["You Don't Need Animations"](https://emilkowal.ski/ui/you-dont-need-animations) — a filter as much as a finder, with a four-question gate (frequency, purpose, speed, function), a required "rejected candidates" section, and a hard cap of 5–7 suggestions.

```
/sharqiewicz:find-animations
```

**`find-animations-mobile`** — the same skill for **React Native + Expo on iOS**. Adds the mobile premise that iOS already animates most of what matters: a system-owned table (native-stack pushes, edge-swipe back, sheet detents, tab switches, `RefreshControl`, native alerts) that is rejected before the gate, a UI-thread test as part of the function question, Reanimated/gesture-handler recipes with exact `dampingRatio` + `duration` configs, `expo-haptics` as a co-channel, and a mandatory Reduce Motion check (Reanimated follows the setting by default, but core `Animated`, `LayoutAnimation` and Lottie don't). Pairs with `rules-apple-mobile`.

```
/sharqiewicz:find-animations-mobile
```

**`find-library`** — a lookup skill for **web**: name a task, get one library. Curated and opinionated, covering UI primitives (base-ui, shadcn/ui, cmdk, Sonner), motion (motion, NumberFlow), data display (TanStack Table, recharts, Tiptap), interaction (dnd kit, Virtuoso), state & styling (zustand, TanStack Query, nuqs, clsx/cva/tailwind-merge), forms (react-hook-form + zod), backend (Drizzle, Better Auth, Resend, Trigger.dev), dates (Temporal over date-fns), and tooling (Vite, Vitest, Playwright, Biome). Includes a `decisions.md` for the contested calls and a "common mismatches" list that catches `useEffect`+`fetch`, filter state outside the URL, and dayjs in greenfield code. UI spine adapted from [Emil Kowalski's pick-ui-library](https://github.com/emilkowalski/skills/blob/main/skills/pick-ui-library/SKILL.md).

```
/sharqiewicz:find-library
```

**`find-library-mobile`** — the same skill for **React Native + Expo on iOS**. Covers foundation (Expo Router, native-stack, safe-area-context), lists (FlashList v2, Legend List), sheets (`formSheet` before a sheet library, `@gorhom/bottom-sheet` when it's earned), styling (Unistyles 3 vs. NativeWind), motion (Reanimated, Moti, gesture-handler, expo-haptics), the four-way storage split (SecureStore / MMKV / expo-sqlite / AsyncStorage), keyboard (`react-native-keyboard-controller`), device capabilities, and EAS/Sentry/Maestro. Carries two extra biases: prefer the Expo SDK module, and prefer native-backed over hand-rolled JS — so several answers are deliberately *"no library"*. Pairs with `rules-apple-mobile`.

```
/sharqiewicz:find-library-mobile
```

**`find-skill`** — ask which installed skill fits a job, e.g. `/sharqiewicz:find-skill animate a bottom sheet on iPhone`. Answers with exactly one skill to use, up to two complements, and the likely wrong picks (namesakes, web vs mobile twins, skills that lost an overlap), each with its exact namespaced command. Reads the curated `find-skill/map.md` plus a live scan of everything installed (`scan.py`), flags unmapped skills, and falls back to Vercel's `/find-skills` when nothing installed fits. Read-only and manual-only.

```
/sharqiewicz:find-skill
```

### fix — diagnose and repair

**`fix-z-index`** — diagnostic decision tree for z-index, stacking context, and overlay bugs. Almost every "z-index doesn't work" issue traces to one of five root causes encoded in the tree.

```
/sharqiewicz:fix-z-index
```

**`fix-animation-mobile`** — diagnose why a **React Native** animation feels off or drops frames, then fix it with the smallest diff. Starts from a release build on a real device, sorts the symptom into JS-thread drops, UI-thread drops, feel, or interaction, and checks the usual causes (core `Animated` without the native driver, animated layout props, per-frame state updates, per-frame hops to JS, the wrong spring). Manual-only. Web sibling: `/debug-animation`.

```
/sharqiewicz:fix-animation-mobile
```

### rules — normative reference

**`rules-apple`** — Apple's Human Interface Guidelines translated for the web (CSS/HTML/JS/React), for frontend and design engineers. Complete standalone skill covering foundations (color, dark mode, materials/translucency, typography, layout, accessibility, RTL, writing), patterns (onboarding, loading/skeletons, feedback, modality, inline validation, delayed sign-in, search, settings), components (buttons, sheets, popovers, alerts, toggles, tab bars, toolbars, sidebars…), inputs (gestures, keyboard, pointer/hover, focus), motion (springs, velocity, interruptibility, reduced-motion), and web-relevant Apple technologies (Sign in with Apple, Apple Pay on the Web). Every rule works as build guidance and as a review check.

```
/sharqiewicz:rules-apple
```

**`rules-apple-mobile`** — Apple's Human Interface Guidelines for iPhone/iOS, translated for React Native + Expo. Complete standalone skill for building native iOS apps: navigation (React Navigation native-stack, large titles, edge-swipe back), tab bars, sheets & detents, alerts/action sheets, forms, lists (FlatList/FlashList, swipe-to-delete, pull-to-refresh), safe areas & Dynamic Island, Dynamic Type, dark mode, SF Symbols, gestures (gesture-handler), motion (reanimated), haptics, permissions, push notifications, and the App Store review requirements that block release (Sign in with Apple, account deletion, ATT). Every rule = Apple HIG rule + the exact RN/Expo API + the common RN mistake.

```
/sharqiewicz:rules-apple-mobile
```

**`rules-layout-mobile`** — layout rules for **React Native + Expo on iOS**: safe areas with `react-native-safe-area-context`, the home indicator and Dynamic Island, keyboard avoidance, RN's flexbox defaults, a point-based spacing scale, large titles with native-stack, and iPad/landscape via `useWindowDimensions` instead of media queries. Web sibling: `/interfaces:better-layout`.

```
/sharqiewicz:rules-layout-mobile
```

**`rules-typography-mobile`** — type rules for **React Native**: Dynamic Type (`allowFontScaling`, `maxFontSizeMultiplier`, `dynamicTypeRamp`), Apple's text-style table, the system font, tabular numbers, `numberOfLines` truncation, and custom fonts via `expo-font`. Web sibling: `/interfaces:better-typography`.

```
/sharqiewicz:rules-typography-mobile
```

**`rules-color-mobile`** — color rules for **React Native**: design in OKLCH but commit hex (RN doesn't document `oklch()`), iOS semantic colors via `PlatformColor`, `DynamicColorIOS` for light/dark and high contrast, Apple's contrast thresholds, and theme tokens. Web siblings: `/interfaces:better-colors`, `/oklch-skill`.

```
/sharqiewicz:rules-color-mobile
```

**`rules-accessibility-mobile`** — VoiceOver rules for **React Native**: roles, labels, hints, state and value, custom actions, announcements, modal focus traps, focus order, 44pt targets with `hitSlop`, and testing with VoiceOver and Accessibility Inspector. Explains why ARIA and `tabindex` habits don't carry over. Web sibling: `/interfaces:better-accessibility`.

```
/sharqiewicz:rules-accessibility-mobile
```

**`rules-polish-mobile`** — the details that make a **React Native** app feel native: `Pressable` press states and scale, continuous corners, concentric radius, `boxShadow` vs `shadow*`, hairline borders, haptics chosen by Apple's guidance, image placeholders, and optimistic UI. Web siblings: `/interfaces:better-ui`, `/make-interfaces-feel-better`.

```
/sharqiewicz:rules-polish-mobile
```

**`rules-design-engineering-mobile`** — craft for **React Native** engineers: respond on press-in, forms that fill themselves (`textContentType`, `autoComplete`, `submitBehavior`, focus chaining), touch instead of hover, interruptible interactions, native-stack presentations, and list choices. Web siblings: `/emil-design-eng`, `/emil-design-engineering`.

```
/sharqiewicz:rules-design-engineering-mobile
```

**`rules-gestures-mobile`** — gesture rules for **React Native**: gesture-handler (hook API first, older builder API mapped), gesture composition and scroll conflicts, `withDecay` with clamp and rubber-banding, velocity hand-off into springs, snap points, native sheets before sheet libraries, and haptics at thresholds. Includes `recipes.md`. Web sibling: `/gesture-ui`.

```
/sharqiewicz:rules-gestures-mobile
```

**`rules-reduced-motion-mobile`** — Reduce Motion in **React Native**: what Reanimated already handles (`ReduceMotion.System` is the default), what it doesn't (core `Animated`, `LayoutAnimation`, Lottie, autoplaying video), what to replace motion with instead of just removing it, and how to test it. Web sibling: `/animation-accessibility`.

```
/sharqiewicz:rules-reduced-motion-mobile
```

**`rules-animation-performance-mobile`** — animation performance for **React Native**: the JS and UI threads, worklets and shared values, cheap vs layout-triggering props, layout animation cost, lists and images during motion, and how to measure with Perf Monitor, Instruments and release builds (`measuring.md`). Web sibling: `/animation-performance`.

```
/sharqiewicz:rules-animation-performance-mobile
```

**`rules-react-state`** — expert guidance for React state management: Zustand, React Query, React Context, and XState. Categorises state as server, global client, injected, or event-driven, then picks the right tool for each.

```
/sharqiewicz:rules-react-state
```

**`rules-git`** — team git workflow: branching strategy, commit discipline, rebase/merge rules, tag management, configuration.

```
/sharqiewicz:rules-git
```

**`rules-web-security`** — frontend and full-stack web security for React, Next.js and TypeScript. Covers XSS sinks, CSP and security headers, CORS, postMessage and WebSocket, CSRF, cookies and sessions, JWT and OAuth/PKCE, and secrets leaked to the browser. Distilled from Securitum's *Bezpieczeństwo aplikacji webowych* (frontend chapters) and checked against current OWASP and MDN guidance. Every rule works as build guidance and as a review check.

```
/sharqiewicz:rules-web-security
```

### review — audit against a standard

**`review-cognitive-load`** — reviews code for extraneous complexity — the kind caused by how code is written, not by the inherent difficulty of the problem — and suggests concrete simplifications.

```
/sharqiewicz:review-cognitive-load
```

**`review-effects`** — detects misused `useEffect` hooks and replaces each with the correct React pattern, based on React's "You Might Not Need an Effect" guidance.

```
/sharqiewicz:review-effects
```

**`review-worst-case`** — tries to break what you just built. Maps where user data enters and where it's displayed, then runs worst-case payloads against the local app: very long names, odd emails, emoji/RTL/Zalgo, 10k rows, zero rows, double submits, Dynamic Type XXL on the smallest iPhone, and case-insensitive duplicates in the DB. Returns a severity-ranked break report with evidence, layer mismatches (UI vs validator vs DB limits) and a cleanup command for seeded data. It never edits source and refuses prod targets unless you confirm them. Pairs with `harden` for the fixes.

```
/sharqiewicz:review-worst-case
```

**`review-interface-mobile`** — audit **React Native** screens, a diff or a path against every `rules-*-mobile` skill plus `rules-apple-mobile`. Greps for the usual problems (hard-coded colors, unlabeled icon buttons, unscaled fonts, module-scope `Dimensions.get`, missing safe areas, web idioms), can take simulator screenshots, and returns P0–P3 findings with file:line, rule, fix and source skill. Read-only, manual-only. Web siblings: `/interfaces:interface-review`, `/web-interface-guidelines`.

```
/sharqiewicz:review-interface-mobile
```

**`review-animations-mobile`** — review the Reanimated and gesture-handler motion in a diff against ten mobile standards drawn from Apple's motion guidance and the Reanimated docs (springs for interactive motion, interruptible, velocity hand-off, UI thread only, Reduce Motion respected, no motion on high-frequency actions, and more). Returns APPROVE or REQUEST CHANGES with file:line findings. Read-only, manual-only. Web sibling: `/review-animations`.

```
/sharqiewicz:review-animations-mobile
```

### make — produce an artifact

**`make-skill`** — scaffolds a new skill from scratch, or audits an existing one against the canonical `SKILL.md` structure and fixes the gaps.

```
/sharqiewicz:make-skill
```

**`make-commit-plan`** — inspects the working tree and proposes how to stage and commit it: logical commit groups, exact `git add` commands (with `-p` hunks when a file spans two commits), and Conventional Commits messages. Runs a risk scan for secrets, build artifacts, and debug leftovers first. Read-only by design — it never runs `git add` or `git commit`; you copy the plan and press the button. Pairs with `rules-git`.

```
/sharqiewicz:make-commit-plan
```

**`make-ticket`** — turns ideas, conversations, and plans into structured, testable work. Three flows: draft a single GitHub Issue in User Story format with Definition of Ready/Done; synthesize the current conversation into a PRD; break a plan or PRD into independently-grabbable tracer-bullet issues.

```
/sharqiewicz:make-ticket
```

**`make-skill-map`** — keeps the skill map current. Finds installed skills the map doesn't mention yet and entries for skills that are gone, proposes a lane and owner for each, shows the diff, and only after approval writes `find-skill/map.md` and regenerates the Skill map section of this README. Depends on `find-skill/scan.py`. Manual-only.

```
/sharqiewicz:make-skill-map
```

**`make-animation-plan-mobile`** — for your most capable model: survey a **React Native** app's motion, audit it against `review-animations-mobile` and `rules-animation-performance-mobile`, and write one self-contained plan file per change (current code, exact Reanimated values, acceptance checks) that a cheaper model can carry out. Manual-only. Web sibling: `/improve-animations`.

```
/sharqiewicz:make-animation-plan-mobile
```

**`make-motion-brief-mobile`** — decide a **React Native** animation before building it, one question at a time with a recommended answer. The first real question is whether iOS already does this, which can end in "don't build". The brief covers trigger, properties, anchor, spring config, gesture hand-off, interruption, haptics, Reduce Motion and frequency. Manual-only. Web sibling: `/motion-brief`.

```
/sharqiewicz:make-motion-brief-mobile
```

**`make-prototype-mobile`** — build several variants of an animation or UI element on a dev-only **Expo Router** screen with a segmented-control switcher. The chosen variant lives in the URL, so a deep link reopens it, and the whole screen is gated on `__DEV__`. Includes cleanup of the losing variants. Manual-only. Web sibling: `/prototype` (Emil).

```
/sharqiewicz:make-prototype-mobile
```

### In progress

Drafts in `in-progress/` (gitignored, not in the plugin). Older versions of two of them are installed on my machine as plain folders: `rules-design-engineering` as `/emil-design-engineering` and `rules-motion-layout` as `/motion-layout-animations`.

- **`rules-design-engineering`** — design engineering principles for polished, accessible, performant web interfaces: animation, forms, touch, color, typography, audio feedback, accessibility, Tailwind state cascading.
- **`rules-motion-layout`** — Motion (Framer Motion successor) layout animations: `layout`, `layoutId`, shared element transitions, `AnimatePresence`, `LayoutGroup`, scale correction.
- **`rules-web-patterns`** — architecture, rendering, and performance patterns from patterns.dev.

<!-- skill-map:start -->
<!-- generated from find-skill/map.md by find-skill/scan.py --readme; edit the map, not this block -->
## Skill map

My curated preferences on top of the live list of installed skills: which **Lane** a skill lives in, which skill is the **Owner** of a job when several overlap, and which names are **Namesakes** or **Exceptions**. Each skill sits in exactly one lane, the one you would look in first. Commands are exact, namespace included. Skills that only run when invoked are marked `manual`. `-mobile` always means React Native + Expo on iOS, and names its web sibling, which may be an external skill.

Maintained by `/sharqiewicz:make-skill-map`, read by `/sharqiewicz:find-skill`. The README section is generated from this file.

### Plan — think before building

| Skill | Job | Notes |
|---|---|---|
| `/mattpocock-skills:grill-me` | Interview me until a plan or design is sharp | manual. Owner of "stress-test my plan". Its auto-invoked twin is `/mattpocock-skills:grilling` |
| `/mattpocock-skills:grilling` | Same interview, model-invoked | Twin of grill-me |
| `/mattpocock-skills:grill-with-docs` | Interview that also writes ADRs and glossary | manual. Owner when the project keeps CONTEXT.md and docs/adr |
| `/mattpocock-skills:to-spec` | Turn the conversation into a spec on the issue tracker | manual. Owner of "write the spec" |
| `/mattpocock-skills:to-tickets` | Break a spec into tracer-bullet tickets | manual. Complements make-ticket flow C |
| `/sharqiewicz:make-ticket` | GitHub Issue, PRD, or tracer-bullet issues | Owner of GitHub Issues and User Stories. |
| `/mattpocock-skills:implement` | Build from a spec or tickets | manual. Runs after to-spec / to-tickets |
| `/mattpocock-skills:wayfinder` | Plan work bigger than one session as a map of decisions | manual |
| `/mattpocock-skills:research` | Investigate a question against primary sources, write findings | Owner of "research this" |
| `/mattpocock-skills:domain-modeling` | Pin down domain terms and model | |
| `/mattpocock-skills:codebase-design` | Vocabulary for designing deep modules | |
| `/mattpocock-skills:prototype` | Throwaway prototype to answer a design question | Namesake of `/prototype` (Emil, in Design UI). Both kept; the namespace tells them apart |
| `/mattpocock-skills:to-questionnaire` | Turn an undecided question into a questionnaire for someone else | manual |
| `/mattpocock-skills:teach` | Teach me a concept or skill | manual |
| `/mattpocock-skills:loop-me` | Grill me about specs for workflows I want to build | manual |
| `/mattpocock-skills:triage` | Move issues and PRs through triage roles | manual |
| `/mattpocock-skills:wait-what` | Re-pitch the last message that did not land | manual |
| `/claude-mem:make-plan` | Phased implementation plan with doc discovery | Plan for execution, not an interview. Runs into `/claude-mem:do` |
| `/claude-mem:do` | Execute a phased plan with subagents | Pair of make-plan. `/mattpocock-skills:implement` owns spec-driven builds |

### Design UI — how it looks and reads

| Skill | Job | Notes |
|---|---|---|
| `/impeccable:impeccable` | Design, critique, audit, polish, typeset, distill any frontend UI (24 commands: `/impeccable:impeccable <command>`) | Owner of "design distinctive UI". Anthropic's frontend-design was removed in its favour |
| `/interfaces:better-ui` | Polish details: radius, optical alignment, shadows, micro-interactions | Owner of "polish small UI details" |
| `/interfaces:better-layout` | Grouping, alignment, reading order, progressive disclosure | |
| `/interfaces:better-typography` | Type scale, spacing, fonts, wrapping | |
| `/interfaces:better-colors` | Color system, OKLCH, contrast | Owner of color. Overlaps `/oklch-skill` |
| `/interfaces:better-accessibility` | Focus, keyboard, ARIA, WCAG | |
| `/interfaces:better-writing` | Interface copy, errors, empty states | |
| `/interfaces:better-interface` | All better-* in one review | Auto-invoked combo of the six above |
| `/interfaces:interface-review` | Multi-category UI review with findings | manual. Owner of "review this UI across categories" |
| `/interfaces:explain-interface` | Figure out how something on the web was built | manual |
| `/interfaces:break` | Render a component in every state and stress it | manual. Code-side stress test: `/sharqiewicz:review-worst-case` (Code quality) |
| `/interfaces:variant` | Build several variants of a component, pick one | manual. Overlaps `/prototype` |
| `/prototype` | Several different versions of a UI piece behind a switcher | manual. Owner of "try several UI variants". Namesake of `/mattpocock-skills:prototype` (Matt, in Plan) |
| `/make-interfaces-feel-better` | Older version of better-ui | Loses to `/interfaces:better-ui` |
| `/oklch-skill` | OKLCH conversions, palettes, Tailwind v4 theming | Loses to `/interfaces:better-colors` |
| `/emil-design-eng` | Emil's philosophy on polish and invisible details | Taste reference; complements better-ui |
| `/emil-design-engineering` | Design engineering rules for forms, touch, performance | Older installed copy of my draft `in-progress/rules-design-engineering`; overlaps emil-design-eng |
| `/sharqiewicz:rules-apple` | Apple HIG translated to web CSS/HTML/React | Web sibling of rules-apple-mobile |
| `/sharqiewicz:rules-apple-mobile` | Apple HIG for React Native + Expo iOS | Mobile sibling of rules-apple |
| `/sharqiewicz:find-library` | Pick one library for a web task (React, Next, Tailwind) | manual. Owner of "which library". Overlaps `/pick-ui-library` |
| `/sharqiewicz:find-library-mobile` | Pick one library for a React Native + Expo task | manual. Mobile sibling of find-library |
| `/sharqiewicz:rules-layout-mobile` | Safe areas, keyboard, flexbox, adaptive layout in React Native | Mobile sibling of `/interfaces:better-layout` |
| `/sharqiewicz:rules-typography-mobile` | Dynamic Type, text styles, system font in React Native | Mobile sibling of `/interfaces:better-typography` |
| `/sharqiewicz:rules-color-mobile` | PlatformColor, DynamicColorIOS, dark mode, contrast in React Native | Mobile sibling of `/interfaces:better-colors` and `/oklch-skill` |
| `/sharqiewicz:rules-accessibility-mobile` | VoiceOver roles, labels, focus, 44pt targets in React Native | Mobile sibling of `/interfaces:better-accessibility` |
| `/sharqiewicz:rules-polish-mobile` | Press feedback, continuous corners, shadows, haptics in React Native | Mobile sibling of `/interfaces:better-ui` and `/make-interfaces-feel-better` |
| `/sharqiewicz:rules-design-engineering-mobile` | Forms, touch, perceived speed, native presentation in React Native | Mobile sibling of `/emil-design-eng` and `/emil-design-engineering` |
| `/sharqiewicz:review-interface-mobile` | Audit React Native screens against every rules-*-mobile skill | manual, read-only. Owner of "review this mobile UI". Mobile sibling of `/interfaces:interface-review` and `/web-interface-guidelines` |
| `/pick-ui-library` | Pick UI and motion tools the animations.dev course trusts | Loses to find-library except for CSS vs WAAPI vs Motion vs GSAP |
| `/shadcn` | Add, search, fix and style shadcn components | |
| `/ask-sonner` | Sonner toast library guide | |
| `/userinterface-wiki` | UI/UX best-practice findings by file:line | Reference; overlaps the better-* set, use as a second opinion |
| `/vocabulary` | Exact design and UI terms for a loose idea | Owner of "what is this design thing called". Motion terms: `/animation-vocabulary` |
| `/web-interface-guidelines` | Review UI code against Vercel's guidelines | Command in ~/.claude/commands |
| `/extract-component` | Extract inline JSX into named components | Command in ~/.claude/commands, Vortex conventions |
| `/write-swift` | Write modern Swift (value types, Swift 6 concurrency) | Native iOS; not React Native |

### Motion — how it moves

| Skill | Job | Notes |
|---|---|---|
| `/animate` | Design and build web animations (Emil / animations.dev) | Owner of "add a web animation". Mobile sibling: `/animate-expo`. Real folder overwrote Emil's npx copy |
| `/animate-expo` | Animations in React Native + Expo | Owner of "motion on mobile". Web sibling: `/animate` |
| `/sharqiewicz:find-animations` | Find places that should animate, reject the rest (web) | Read-only. Owner of "where should I add motion". Overlaps `/find-animation-opportunities` |
| `/sharqiewicz:find-animations-mobile` | Same, for React Native + Expo iOS | Mobile sibling of find-animations |
| `/sharqiewicz:rules-gestures-mobile` | gesture-handler + Reanimated drag, fling, decay, sheets | Mobile sibling of `/gesture-ui` |
| `/sharqiewicz:rules-reduced-motion-mobile` | Reduce Motion in Reanimated, Animated, Lottie, video | Mobile sibling of `/animation-accessibility` |
| `/sharqiewicz:rules-animation-performance-mobile` | JS vs UI thread, worklets, cheap props, profiling | Mobile sibling of `/animation-performance` |
| `/sharqiewicz:fix-animation-mobile` | Find and fix why a React Native animation feels off or drops frames | manual. Owner of "my mobile animation is janky". Mobile sibling of `/debug-animation` |
| `/sharqiewicz:review-animations-mobile` | Approve or reject Reanimated motion in a diff | manual, read-only. Mobile sibling of `/review-animations` |
| `/sharqiewicz:make-animation-plan-mobile` | Audit an app's motion, write plans for cheaper models | manual. Mobile sibling of `/improve-animations` |
| `/sharqiewicz:make-motion-brief-mobile` | Interview me about a mobile animation before building | manual. Mobile sibling of `/motion-brief` |
| `/sharqiewicz:make-prototype-mobile` | Several variants behind a switcher on an Expo dev screen | manual. Mobile sibling of `/prototype` |
| `/find-animation-opportunities` | Emil's version of find-animations | manual. Overlap; loses to find-animations |
| `/review-animations` | Review animation code against the animations.dev bar | manual. Owner of "review my animations" |
| `/improve-animations` | Audit motion and write implementation plans | manual. Plans for other agents; review-animations is the findings report |
| `/debug-animation` | Name the exact cause of an animation that feels off | Owner of "my animation is janky or wrong" |
| `/animation-performance` | Frame budget, composite-only properties | Reference for 60fps |
| `/animation-accessibility` | prefers-reduced-motion variants | Reference for reduced motion |
| `/animation-vocabulary` | Name a motion effect from a vague description | Owner of motion terms. General design terms: `/vocabulary` |
| `/css-animations` | CSS-only transitions, keyframes, transforms | |
| `/motion-react` | Motion for React (motion/react) | |
| `/motion-layout-animations` | layout, layoutId, AnimatePresence, shared elements | Owner of layout animation inside Motion. Older installed copy of my draft `in-progress/rules-motion-layout` |
| `/scroll-animations` | Scroll-triggered reveals and scroll-driven animation | |
| `/gesture-ui` | Drag, swipe, sheets that track the finger | Web. Mobile sibling: `/sharqiewicz:rules-gestures-mobile` |
| `/motion-brief` | Interview me about an animation before building | Plan-like but motion-specific, so it lives here |

### Code quality — how the code holds up

| Skill | Job | Notes |
|---|---|---|
| `/mattpocock-skills:tdd` | Test-first development | Owner of "build test-first" |
| `/mattpocock-skills:diagnosing-bugs` | Diagnosis loop for hard bugs and regressions | Owner of "find the root cause of a bug" |
| `/mattpocock-skills:code-review` | Review changes since a fixed point on two axes | Owner of "review my changes". Namesake of `/code-review` (my Vortex command, below) |
| `/code-review` | Review changed files for React, TypeScript and Vortex conventions | Command in ~/.claude/commands. Namesake of the Matt plugin skill; Vortex repos only |
| `/mattpocock-skills:improve-codebase-architecture` | Find deepening opportunities, render an HTML report | manual |
| `/improve:improve` | Senior-advisor codebase survey; writes plans for other agents | Owner of "what should I improve in this codebase". Read-only on source |
| `/react-doctor` | Diagnose and fix React codebase health | Owner of React health and performance |
| `/sharqiewicz:review-effects` | When to use useEffect and what replaces it | |
| `/sharqiewicz:review-cognitive-load` | Extraneous complexity and simplifications | |
| `/sharqiewicz:review-worst-case` | Break the app with worst-case inputs, report evidence | |
| `/sharqiewicz:rules-react-state` | Zustand, React Query, Context, XState | |
| `/sharqiewicz:rules-web-security` | XSS, CSP, CORS, cookies, JWT, OAuth for React and Next | |
| `/sharqiewicz:fix-z-index` | Fix z-index and stacking-context bugs | |
| `/mattpocock-skills:setup-ts-deep-modules` | dependency-cruiser so each package is a deep module | manual |
| `/mattpocock-skills:migrate-to-shoehorn` | Replace `as` assertions in tests | |
| `/solidity-auditor` | Solidity security audit | Command in ~/.claude/commands |

### Git & handoff — getting work out

| Skill | Job | Notes |
|---|---|---|
| `/sharqiewicz:rules-git` | Branching, commits, rebase, tags | Reference |
| `/sharqiewicz:make-commit-plan` | Propose commit groups and messages; runs no mutating git | Owner of "what should I commit" |
| `/mattpocock-skills:resolving-merge-conflicts` | Resolve an in-progress merge or rebase conflict | |
| `/mattpocock-skills:handoff` | Compact the conversation into a document for another agent | manual. Owner of "hand off this work" |
| `/mattpocock-skills:claude-handoff` | Hand off to a fresh background agent | manual |
| `/mattpocock-skills:setup-pre-commit` | Husky, lint-staged, type checks | |
| `/mattpocock-skills:git-guardrails-claude-code` | Hooks that block dangerous git commands | |

### SEO — search visibility

| Skill | Job | Notes |
|---|---|---|
| `/seo` | Entry point: comprehensive SEO analysis, routes to the rest | Owner when the ask is just "SEO" |
| `/seo-audit`, `/seo-page`, `/seo-technical` | Full site audit, single page, technical audit | Audit family |
| `/seo-content`, `/seo-content-brief`, `/seo-cluster`, `/seo-plan` | Content quality, briefs, topic clusters, strategy | Content and planning family |
| `/seo-schema`, `/seo-sitemap`, `/seo-hreflang`, `/seo-images`, `/seo-image-gen` | Structured data, sitemaps, international, images | On-page assets |
| `/seo-geo`, `/seo-sxo`, `/seo-programmatic`, `/seo-competitor-pages`, `/seo-ecommerce`, `/seo-local`, `/seo-maps` | AI search, SERP fit, scale pages, vs-pages, shops, local | Specialties |
| `/seo-backlinks`, `/seo-drift`, `/seo-flow`, `/seo-unlighthouse`, `/seo-firecrawl` | Links, drift monitoring, FLOW framework, Lighthouse, crawling | Monitoring and tooling |
| `/seo-ahrefs`, `/seo-bing`, `/seo-dataforseo`, `/seo-google`, `/seo-profound`, `/seo-seranking` | Data providers (need API keys or MCP) | Extensions |

### Tools — integrations and meta

| Skill | Job | Notes |
|---|---|---|
| `/sharqiewicz:find-skill` | Which installed skill fits this job | manual, read-only. Owner of "which of my skills" |
| `/sharqiewicz:make-skill-map` | Keep this map current and regenerate the README block | manual. Only writer of map.md |
| `/sharqiewicz:make-skill` | Scaffold or audit a skill | |
| `/find-skills` | Search skills.sh for new skills to install | Vercel, installed via npx. Finds skills I do not have yet |
| `/mattpocock-skills:ask-matt` | Which of Matt's skills fits | manual. Only covers his set; find-skill covers everything |
| `/mattpocock-skills:writing-for-agents` | Write skills, AGENTS.md, agent docs | |
| `/mattpocock-skills:setup-matt-pocock-skills` | Configure a repo for Matt's skills | manual |
| `/mattpocock-skills:wizard` | Interactive bash wizard for human-only steps | |
| `/mattpocock-skills:scaffold-exercises` | Exercise directory structures | |
| `/mattpocock-skills:writing-fragments`, `/mattpocock-skills:writing-beats`, `/mattpocock-skills:writing-shape` | Writing pipeline: fragments, beats, shape | manual |
| `/obsidian-vault` | Search and manage Obsidian notes | Exception: npx, from Matt's repo, not in his plugin |
| `/goals` | Goals, reflection, ONE THING | Personal |
| `/claude-mem:mem-search` | Search past sessions | Owner of "did we solve this before" |
| `/claude-mem:smart-explore` | Token-cheap AST code search | |
| `/claude-mem:knowledge-agent`, `/claude-mem:timeline-report`, `/claude-mem:claude-code-plugin-release` | Knowledge bases, project timeline, plugin release | |
| `/sentry:sentry-workflow` | Fix production issues with Sentry context | Owner of "fix this Sentry error" |
| `/sentry:sentry-fix-issues`, `/sentry:sentry-code-review`, `/sentry:sentry-pr-code-review` | Manual variants: fix issues, resolve Sentry PR comments, Seer PR review | manual |
| `/sentry:sentry-sdk-setup`, `/sentry:sentry-feature-setup` | Set up Sentry in any stack, or a specific feature | Owner of "add Sentry" |
| `/sentry:sentry-instrumentation-guide`, `/sentry:sentry-create-alert`, `/sentry:sentry-setup-ai-monitoring`, `/sentry:sentry-otel-exporter-setup`, `/sentry:sentry-sdk-upgrade`, `/sentry:sentry-sdk-skill-creator` | Signals, alerts, AI monitoring, OTel, upgrades, SDK skill bundles | manual |
| `/sentry:sentry-*-sdk` | Per-platform SDK setup (React, Next, Node, React Native, Python, Go, ...) | manual. Reached through sentry-sdk-setup |
| `/figma:figma-design-to-code`, `/figma:figma-implement-motion`, `/figma:figma-swiftui`, `/figma:figma-code-connect` | Figma to code | Figma plugin; MCP prerequisites load themselves |
| `/figma:figma-use`, `/figma:figma-use-figjam`, `/figma:figma-use-slides`, `/figma:figma-use-motion`, `/figma:figma-create-new-file`, `/figma:figma-generate-design`, `/figma:figma-generate-library`, `/figma:figma-generate-diagram`, `/figma:figma-shaders`, `/figma:figma-generative-plugins` | Code to Figma, writes into files | Figma plugin |
| `/figma:video-interaction-mapper`, `/figma:generate-project-plan` | Screen recording to interaction map, FigJam plan board | Figma plugin |

### Namesakes

- `/prototype` (Emil, several variants behind a switcher) and `/mattpocock-skills:prototype` (Matt, throwaway prototype). Both kept.
- `/code-review` (my Vortex command) and `/mattpocock-skills:code-review` (Matt, general). Both kept.
- Jakub's better-* skills are invoked only as `/interfaces:better-*` (plugin); the map lists no bare copies.

### Exceptions

- `/obsidian-vault` comes through npx because Matt's plugin does not ship it.
- `/sharqiewicz:*` is this repo loaded as a plugin (`sharqiewicz@skills-dir`); never install the same skills with npx.
<!-- skill-map:end -->

---

## External skills

### React

**React Doctor** — diagnoses and fixes React codebase health: performance, correctness, architecture. https://www.react.doctor/

```
npx skills add millionco/react-doctor
```

**Vercel skills** (not installed on my machine; worth a look)

```
npx skills add vercel-labs/agent-skills
```

- [**React view transitions**](https://github.com/vercel-labs/agent-skills/tree/main/skills/react-view-transitions) — smooth, native-feeling animations using React's View Transition API (`<ViewTransition>`, `addTransitionType`, CSS view transition pseudo-elements).
- [**React best practices**](https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices) — React and Next.js performance optimization guidelines from Vercel Engineering.
- [**Composition patterns**](https://github.com/vercel-labs/agent-skills/tree/main/skills/composition-patterns) — React composition patterns that scale; compound components, render props, context providers, component architecture. Includes React 19 API changes.

### Design engineering

**Web interface guidelines** — review UI code for Web Interface Guidelines compliance. I use it as a personal command (`~/.claude/commands/web-interface-guidelines.md`); the skill version ships in Vercel's set:

- [https://github.com/vercel-labs/agent-skills/blob/main/skills/web-design-guidelines](https://github.com/vercel-labs/agent-skills/blob/main/skills/web-design-guidelines)

```
npx skills add vercel-labs/agent-skills
```

**better-** — skills for design engineers (`better-ui`, `better-colors`, `better-layout`, `better-typography`, `better-accessibility`, `better-interface`, `better-writing`), installed as one plugin (invoke as `/interfaces:<skill>`). https://jakub.kr/skills

```
/plugin marketplace add jakubkrehel/skills
/plugin install interfaces@interfaces
```

**OKLCH** — OKLCH color space for web projects. Convert hex/rgb/hsl to oklch, generate palettes, check contrast, handle gamut boundaries, and theme with Tailwind v4:

- [https://github.com/jakubkrehel/oklch-skill/tree/main/skills/oklch-skill](https://github.com/jakubkrehel/oklch-skill/tree/main/skills/oklch-skill)

```
npx skills add jakubkrehel/oklch-skill
```

**Impeccable** — deep design knowledge in one skill with 24 commands (`/impeccable:impeccable polish`, `/impeccable:impeccable audit`, …):

- [https://github.com/pbakaus/impeccable](https://github.com/pbakaus/impeccable)

```
/plugin marketplace add pbakaus/impeccable
/plugin install impeccable@impeccable
```

**vocabulary** — https://index.how/to/articulate

```
npx skills add index-how/vocabulary
```

**shadcn** — https://ui.shadcn.com/docs/skills

```
npx skills add shadcn/ui
```

**userinterface-wiki** — UI/UX best-practice checks reported by file and line; a second opinion next to the better-* set.

```
npx skills add raphaelsalaja/userinterface-wiki
```

### Motion

**Emil Kowalski's skills** — `animate`, `animate-expo` (React Native + Expo), `review-animations`, `improve-animations`, `find-animation-opportunities`, `prototype`, `pick-ui-library`, `animation-vocabulary`, `emil-design-eng`, `ask-sonner`, `write-swift`. https://emilkowal.ski/skill

```
npx skills add emilkowalski/skills
```

**animations.dev skills** — 15 course skills (`animate`, `css-animations`, `motion-react`, `motion-brief`, `gesture-ui`, `scroll-animations`, `debug-animation`, …). Private, for course members only. The installer writes real folders into `~/.claude/skills/` and overwrites same-name skills from Emil's set, so run it **after** `npx skills add emilkowalski/skills`, and never run `npx skills update` on those names afterwards. https://animations.dev/learn/skills

```
npx @animationsdev/install --token=<your token>
```

### SEO

**Comprehensive SEO** — `seo-*` skills and subagents covering technical SEO, on-page analysis, content quality (E-E-A-T), schema markup, image optimization, sitemap architecture, AI search optimization (GEO), local SEO, and more. Installed with the script from https://claude-seo.md, which copies the skills into `~/.claude/skills/` and the subagents into `~/.claude/agents/` (update by rerunning it). A plugin install also exists: `claude-seo@agricidaniel-claude-seo`.

- [https://github.com/AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo)

```
git clone --depth 1 https://github.com/AgriciDaniel/claude-seo.git && bash claude-seo/install.sh
```

### Tooling

**Matt Pocock's skills** — grill-me, grill-with-docs, teach, tdd and more, installed as one plugin (invoke as `/mattpocock-skills:<skill>`). https://github.com/mattpocock/skills

```
/plugin install mattpocock-skills@claude-plugins-official
```

**improve** (shadcn) — a senior codebase audit that writes implementation plans for other agents to execute. https://github.com/shadcn/improve

```
/plugin marketplace add shadcn/improve
/plugin install improve@improve
```

**Obsidian vault** (Matt Pocock) — search, create, and organize notes in Obsidian. It isn't in Matt's plugin, so it's the one skill from his repo installed with npx.

```
npx skills add mattpocock/skills/obsidian-vault
```

**find-skills** (Vercel) — searches skills.sh for skills I don't have yet. `/sharqiewicz:find-skill` hands off to it when nothing installed fits.

```
npx skills add vercel-labs/skills --skill find-skills
```

**Sentry** — fix production issues with Sentry context, set up SDKs, alerts and AI monitoring (invoke as `/sentry:<skill>`).

```
/plugin marketplace add getsentry/plugin-claude
/plugin install sentry@sentry-plugin-marketplace
```

**Figma** — design to code and code to Figma (invoke as `/figma:<skill>`).

```
/plugin install figma@claude-plugins-official
```

**claude-mem** — persistent memory across sessions: search past work, plan and execute phased plans (invoke as `/claude-mem:<skill>`).

```
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem@thedotmack
```

### Keeping external skills up to date

- **Plugins** (Impeccable, Matt Pocock, Jakub, shadcn improve, Sentry, Figma, claude-mem, and this repo for other people): third-party marketplaces don't auto-update by default. Turn it on per marketplace in `/plugin` → Marketplaces, or run `claude plugin update <plugin>`.
- **npx skills** (Emil, OKLCH, vocabulary, shadcn/ui, React Doctor, userinterface-wiki, find-skills, obsidian-vault): `npx skills update`. Skip the names that animations.dev overwrote.
- **Script** (SEO): rerun the claude-seo install script.
- **Folders** (animations.dev): rerun its installer with your token.
- **Never install the same set through two channels.** A plugin copy and an npx copy of one skill both load and compete.
