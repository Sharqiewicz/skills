# Skill map

My curated preferences on top of the live list of installed skills: which **Lane** a skill lives in, which skill is the **Owner** of a job when several overlap, and which names are **Namesakes** or **Exceptions**. Each skill sits in exactly one lane, the one you would look in first. Commands are exact, namespace included. Skills that only run when invoked are marked `manual`. `-mobile` always means React Native + Expo on iOS, and names its web sibling, which may be an external skill.

Maintained by `/sharqiewicz:make-skill-map`, read by `/sharqiewicz:find-skill`. The README section is generated from this file.

## Plan — think before building

| Skill | Job | Notes |
|---|---|---|
| `/mattpocock-skills:grill-me` | Interview me until a plan or design is sharp | manual. Owner of "stress-test my plan". Its auto-invoked twin is `/mattpocock-skills:grilling` <!-- grill-me is the explicit command, grilling the same job for model invocation; kept both, grill-me as owner --> |
| `/mattpocock-skills:grilling` | Same interview, model-invoked | Twin of grill-me |
| `/mattpocock-skills:grill-with-docs` | Interview that also writes ADRs and glossary | manual. Owner when the project keeps CONTEXT.md and docs/adr |
| `/mattpocock-skills:to-spec` | Turn the conversation into a spec on the issue tracker | manual. Owner of "write the spec" <!-- to-spec matches the .scratch/ tracker convention in my repos; make-ticket flow B (PRD) covers GitHub Issues --> |
| `/mattpocock-skills:to-tickets` | Break a spec into tracer-bullet tickets | manual. Complements make-ticket flow C <!-- to-tickets for .scratch trackers, make-ticket for GitHub Issues --> |
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
| `/claude-mem:do` | Execute a phased plan with subagents | Pair of make-plan. `/mattpocock-skills:implement` owns spec-driven builds <!-- two executors; implement for specs and tickets, claude-mem:do for make-plan output --> |

## Design UI — how it looks and reads

| Skill | Job | Notes |
|---|---|---|
| `/impeccable:impeccable` | Design, critique, audit, polish, typeset, distill any frontend UI (24 commands: `/impeccable:impeccable <command>`) | Owner of "design distinctive UI", **only in projects with no defined design team**. When a design team owns the look, don't invent a visual direction: polish within their design with `/interfaces:better-*` and `/emil-design-eng` |
| `/interfaces:better-ui` | Polish details: radius, optical alignment, shadows, micro-interactions | Owner of "polish small UI details" <!-- emil-design-eng covers the same ground as taste reference --> |
| `/interfaces:better-layout` | Grouping, alignment, reading order, progressive disclosure | |
| `/interfaces:better-typography` | Type scale, spacing, fonts, wrapping | |
| `/interfaces:better-colors` | Color system, OKLCH, contrast | Owner of color and OKLCH |
| `/interfaces:better-accessibility` | Focus, keyboard, ARIA, WCAG | |
| `/interfaces:better-writing` | Interface copy, errors, empty states | |
| `/interfaces:better-interface` | All better-* in one review | Auto-invoked combo of the six above |
| `/interfaces:interface-review` | Multi-category UI review with findings | manual. Owner of "review this UI across categories" <!-- explicit report form; impeccable audit is the alternative when the goal is fixing, not reporting --> |
| `/interfaces:explain-interface` | Figure out how something on the web was built | manual |
| `/interfaces:break` | Render a component in every state and stress it | manual. Code-side stress test: `/sharqiewicz:review-worst-case` (Code quality) |
| `/interfaces:variant` | Build several variants of a component, pick one | manual. Overlaps `/prototype` <!-- Emil's prototype is built for this and kept; variant is the plugin alternative --> |
| `/prototype` | Several different versions of a UI piece behind a switcher | manual. Owner of "try several UI variants". Namesake of `/mattpocock-skills:prototype` (Matt, in Plan) |
| `/emil-design-eng` | Emil's philosophy on polish and invisible details | Taste reference; the one I use most for polish. Complements better-ui |
| `/sharqiewicz:rules-apple` | Apple HIG translated to web CSS/HTML/React | Web sibling of rules-apple-mobile |
| `/sharqiewicz:rules-apple-mobile` | Apple HIG for React Native + Expo iOS | Mobile sibling of rules-apple |
| `/sharqiewicz:find-library` | Pick one library for a web task (React, Next, Tailwind) | manual. Owner of "which library". On my machine also owns CSS vs WAAPI vs motion via the private `animation-tools.local.md` |
| `/sharqiewicz:find-library-mobile` | Pick one library for a React Native + Expo task | manual. Mobile sibling of find-library |
| `/sharqiewicz:rules-layout-mobile` | Safe areas, keyboard, flexbox, adaptive layout in React Native | Mobile sibling of `/interfaces:better-layout` |
| `/sharqiewicz:rules-typography-mobile` | Dynamic Type, text styles, system font in React Native | Mobile sibling of `/interfaces:better-typography` |
| `/sharqiewicz:rules-color-mobile` | PlatformColor, DynamicColorIOS, dark mode, contrast in React Native | Mobile sibling of `/interfaces:better-colors` |
| `/sharqiewicz:rules-accessibility-mobile` | VoiceOver roles, labels, focus, 44pt targets in React Native | Mobile sibling of `/interfaces:better-accessibility` |
| `/sharqiewicz:rules-polish-mobile` | Press feedback, continuous corners, shadows, haptics in React Native | Mobile sibling of `/interfaces:better-ui` |
| `/sharqiewicz:rules-design-engineering-mobile` | Forms, touch, perceived speed, native presentation in React Native | Mobile sibling of `/emil-design-eng` |
| `/sharqiewicz:review-interface-mobile` | Audit React Native screens against every rules-*-mobile skill | manual, read-only. Owner of "review this mobile UI". Mobile sibling of `/interfaces:interface-review` and `/web-interface-guidelines` |
| `/shadcn` | Add, search, fix and style shadcn components | |
| `/vocabulary` | Exact design and UI terms for a loose idea | Owner of "what is this design thing called". Motion terms: `/animation-vocabulary` |
| `/web-interface-guidelines` | Review UI code against Vercel's guidelines | Command in ~/.claude/commands |

## Motion — how it moves

| Skill | Job | Notes |
|---|---|---|
| `/animate` | Design and build web animations (Emil / animations.dev) | Owner of "add a web animation". Mobile sibling: `/animate-expo`. Real folder overwrote Emil's npx copy |
| `/animate-expo` | Animations in React Native + Expo | Owner of "motion on mobile". Web sibling: `/animate` |
| `/sharqiewicz:find-animations-mobile` | Find places that should animate in React Native + Expo iOS, reject the rest | Read-only. Owner of "where should I add motion" on mobile. Web sibling: `/find-animation-opportunities` |
| `/sharqiewicz:rules-gestures-mobile` | gesture-handler + Reanimated drag, fling, decay, sheets | Mobile sibling of `/gesture-ui` |
| `/sharqiewicz:rules-reduced-motion-mobile` | Reduce Motion in Reanimated, Animated, Lottie, video | Mobile sibling of `/animation-accessibility` |
| `/sharqiewicz:rules-animation-performance-mobile` | JS vs UI thread, worklets, cheap props, profiling | Mobile sibling of `/animation-performance` |
| `/sharqiewicz:fix-animation-mobile` | Find and fix why a React Native animation feels off or drops frames | manual. Owner of "my mobile animation is janky". Mobile sibling of `/debug-animation` |
| `/sharqiewicz:review-animations-mobile` | Approve or reject Reanimated motion in a diff | manual, read-only. Mobile sibling of `/review-animations` |
| `/sharqiewicz:make-animation-plan-mobile` | Audit an app's motion, write plans for cheaper models | manual. Mobile sibling of `/improve-animations` |
| `/sharqiewicz:make-motion-brief-mobile` | Interview me about a mobile animation before building | manual. Mobile sibling of `/motion-brief` |
| `/sharqiewicz:make-prototype-mobile` | Several variants behind a switcher on an Expo dev screen | manual. Mobile sibling of `/prototype` |
| `/find-animation-opportunities` | Find places that should animate on the web, reject the rest (Emil) | manual. Owner of "where should I add motion" on the web. Mobile sibling: `/sharqiewicz:find-animations-mobile` |
| `/review-animations` | Review animation code against the animations.dev bar | manual. Owner of "review my animations" |
| `/improve-animations` | Audit motion and write implementation plans | manual. Plans for other agents; review-animations is the findings report |
| `/debug-animation` | Name the exact cause of an animation that feels off | Owner of "my animation is janky or wrong" <!-- starts from a symptom; animation-performance is the reference for frame budget --> |
| `/animation-performance` | Frame budget, composite-only properties | Reference for 60fps |
| `/animation-accessibility` | prefers-reduced-motion variants | Reference for reduced motion |
| `/animation-vocabulary` | Name a motion effect from a vague description | Owner of motion terms. General design terms: `/vocabulary` |
| `/css-animations` | CSS-only transitions, keyframes, transforms | |
| `/motion-react` | Motion for React (motion/react) | |
| `/scroll-animations` | Scroll-triggered reveals and scroll-driven animation | |
| `/gesture-ui` | Drag, swipe, sheets that track the finger | Web. Mobile sibling: `/sharqiewicz:rules-gestures-mobile` |
| `/motion-brief` | Interview me about an animation before building | Plan-like but motion-specific, so it lives here |

## Code quality — how the code holds up

| Skill | Job | Notes |
|---|---|---|
| `/mattpocock-skills:tdd` | Test-first development | Owner of "build test-first" |
| `/mattpocock-skills:diagnosing-bugs` | Diagnosis loop for hard bugs and regressions | Owner of "find the root cause of a bug" |
| `/mattpocock-skills:code-review` | Review changes since a fixed point on two axes | Owner of "review my changes". Namesake of `/code-review` (my Vortex command, below) <!-- general-purpose review owns the bare intent; bare /code-review stays as the Vortex-specific exception --> |
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

## Git & handoff — getting work out

| Skill | Job | Notes |
|---|---|---|
| `/sharqiewicz:rules-git` | Branching, commits, rebase, tags | Reference |
| `/sharqiewicz:make-commit-plan` | Propose commit groups and messages; runs no mutating git | Owner of "what should I commit" |
| `/mattpocock-skills:resolving-merge-conflicts` | Resolve an in-progress merge or rebase conflict | |
| `/mattpocock-skills:handoff` | Compact the conversation into a document for another agent | manual. Owner of "hand off this work" |
| `/mattpocock-skills:claude-handoff` | Hand off to a fresh background agent | manual |
| `/mattpocock-skills:setup-pre-commit` | Husky, lint-staged, type checks | |
| `/mattpocock-skills:git-guardrails-claude-code` | Hooks that block dangerous git commands | |

## Tools — integrations and meta

| Skill | Job | Notes |
|---|---|---|
| `/sharqiewicz:find-skill` | Which installed skill fits this job | manual, read-only. Owner of "which of my skills" |
| `/sharqiewicz:make-skill-map` | Keep this map current and regenerate the README block | manual. Only writer of map.md |
| `/sharqiewicz:make-skill` | Scaffold or audit a skill | |
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
| `/figma:figma-design-to-code`, `/figma:figma-implement-motion`, `/figma:figma-swiftui`, `/figma:figma-code-connect` | Figma to code | Figma plugin; MCP prerequisites load themselves |
| `/figma:figma-use`, `/figma:figma-use-figjam`, `/figma:figma-use-slides`, `/figma:figma-use-motion`, `/figma:figma-create-new-file`, `/figma:figma-generate-design`, `/figma:figma-generate-library`, `/figma:figma-generate-diagram`, `/figma:figma-shaders`, `/figma:figma-generative-plugins` | Code to Figma, writes into files | Figma plugin |
| `/figma:video-interaction-mapper`, `/figma:generate-project-plan` | Screen recording to interaction map, FigJam plan board | Figma plugin |

## Namesakes

- `/prototype` (Emil, several variants behind a switcher) and `/mattpocock-skills:prototype` (Matt, throwaway prototype). Both kept.
- `/code-review` (my Vortex command) and `/mattpocock-skills:code-review` (Matt, general). Both kept.
- Jakub's better-* skills are invoked only as `/interfaces:better-*` (plugin); the map lists no bare copies.

## Exceptions

- `/obsidian-vault` comes through npx because Matt's plugin does not ship it.
- `/sharqiewicz:*` is this repo loaded as a plugin (`sharqiewicz@skills-dir`); never install the same skills with npx.
