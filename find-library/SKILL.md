---
name: find-library
description: "Pick the right library for a web task from a curated, opinionated list — UI primitives, toasts, command menus, charts, tables, drag and drop, virtualization, rich text, motion, state, styling, forms, data fetching, auth, ORM, email, payments, dates, i18n, and tooling. React + Next.js + Tailwind. One pick per task, not a menu. Only runs when explicitly invoked; it does not trigger on its own."
disable-model-invocation: true
---

# Finding The Right Library (Web)

A lookup skill. When invoked with a task ("I need toasts", "what should I use for drag and drop?", "how do I do auth?"), match the task to the curated list below and recommend **one** library. These are deliberate, taste-driven picks — don't substitute alternatives outside this list unless the user asks for one or the task genuinely isn't covered.

**Stack assumption:** React + Next.js (App Router) + Tailwind. A few picks are Next-specific and marked as such. For React Native, use `find-library-mobile` instead.

## How to use this

1. **Identify the task**, not the library the user named. "I need to show a dropdown" is a UI-primitives task (base-ui), even if they asked about something else.
2. **Check what's already installed.** Read `package.json` first. If the project already uses a listed library, use it. If it uses a competitor (e.g. react-window instead of Virtuoso, Prisma instead of Drizzle), flag the recommendation but **don't churn the dependency without being asked**.
3. **Check whether a library is needed at all.** A hover fade is a CSS transition, not motion. A single boolean is `useState`, not zustand. Three rows are a `<table>`, not TanStack Table. The best pick is often none.
4. **Recommend one library**, state what it's for in one sentence, and install/wire it up if that's part of the request. Don't present a menu when the list has a clear answer.
5. **If the call is genuinely contested** (state, styling, forms, auth, database, editors, dates) → read [decisions.md](decisions.md) for the real tradeoff and when to deviate.
6. If the task isn't covered, say so explicitly and recommend from your own knowledge — but be clear you've left the curated list.
7. **If `animation-tools.local.md` exists next to this file, read it** for animation-tool choices (CSS vs WAAPI vs motion) and the extra picks it lists. It is a private local addition, so never quote it into anything published.

## UI components & primitives

| Task | Library |
| --- | --- |
| Unstyled, accessible primitives (dialogs, popovers, menus, selects…) | [base-ui](https://base-ui.com) |
| Styled components you own the source of, on top of those primitives | [shadcn/ui](https://ui.shadcn.com) |
| Command menus (⌘K palettes) | [cmdk](https://cmdk.paco.me) |
| Toasts / notifications | [Sonner](https://sonner.emilkowal.ski) |
| One-time password / verification code inputs | [input-otp](https://input-otp.rodz.dev) |
| Icons | [lucide-react](https://lucide.dev) |
| Customizable GUIs / control panels / debug tweakers | [Leva](https://github.com/pmndrs/leva) |

base-ui is the behaviour layer, shadcn/ui is a styled layer on top — they aren't competitors. Reach for shadcn when you want a working button today and are happy owning the file; reach for base-ui directly when the design system is yours and you only need the accessibility, focus trapping, and dismissal logic.

## Motion & visuals

| Task | Library |
| --- | --- |
| General-purpose animation (springs, layout animations, enter/exit) | [motion](https://motion.dev) |
| Animating numbers (counters, prices, stats) | [NumberFlow](https://number-flow.barvian.me) |
| Animated text components | [torph](https://torph.lochie.me/) |
| 3D globes | [Cobe](https://cobe.vercel.app) |
| Dynamic OG images (HTML/CSS → SVG/PNG) | [Satori](https://github.com/vercel/satori) (Next: `next/og` wraps it) |
| Syntax highlighting | [shiki](https://shiki.style) |

Reach for motion when you need springs, layout animations, exit animations, or gesture-driven values. A simple hover or fade doesn't need it — plain CSS transitions are the right tool there.

## Data display

| Task | Library |
| --- | --- |
| Tables (sorting, filtering, grouping, pagination) | [TanStack Table](https://tanstack.com/table) |
| Real-time / streaming charts | [Liveline](https://github.com/benjitaylor/liveline) |
| General charts (static or interactive dashboards) | [recharts](https://recharts.org) |
| Rich text editing | [Tiptap](https://tiptap.dev) — [Plate](https://platejs.org) if the project is shadcn-based |

The chart split: if data points arrive live and the chart scrolls with time, use Liveline. Everything else is recharts.

TanStack Table is headless — it gives you the logic, you render the markup. That's the point: it fits your design system instead of fighting it. If you need pivoting, Excel export, and 100 built-in features more than you need control, you want a grid, not a table — see [decisions.md](decisions.md).

## Interaction & performance

| Task | Library |
| --- | --- |
| Drag and drop | [dnd kit](https://dndkit.com) |
| Virtualization (long lists, large tables) | [Virtuoso](https://virtuoso.dev) |
| File drop zones | [react-dropzone](https://react-dropzone.js.org) |
| Full upload pipeline (client + server + storage), Next | [UploadThing](https://uploadthing.com) |

## State & styling

| Task | Library |
| --- | --- |
| Client state management | [zustand](https://zustand.docs.pmnd.rs) |
| Server state (fetching, caching, invalidation, optimistic updates) | [TanStack Query](https://tanstack.com/query) |
| State that lives in the URL (filters, tabs, pagination) | [nuqs](https://nuqs.dev) |
| Constructing `className` strings conditionally | [clsx](https://github.com/lukeed/clsx) |
| Type-safe, variant-driven styling for Tailwind | [cva](https://cva.style) |
| Resolving conflicting Tailwind classes when merging props | [tailwind-merge](https://github.com/dcastil/tailwind-merge) |
| Theme switching / dark mode (no flash on load) | [next-themes](https://github.com/pacocoursey/next-themes) |

The state split is the one people get wrong: **server state is not client state.** Anything that came from an API and can go stale belongs to TanStack Query, not zustand. zustand is for genuinely client-owned state — a wizard step, an editor selection, a sidebar toggle shared across a tree. Filters and pagination belong in the URL (nuqs) so they survive refresh and are shareable.

The styling split: clsx for ad-hoc conditional classes; cva when a component has real variants (size, intent, state) that deserve a typed API; tailwind-merge when a component accepts a `className` prop that must be able to override its own defaults. They compose — cva uses clsx-style inputs internally, and `cn()` in shadcn projects is clsx + tailwind-merge.

## Forms & validation

| Task | Library |
| --- | --- |
| Forms | [react-hook-form](https://react-hook-form.com) |
| Schema validation (input, env vars, API boundaries) | [zod](https://zod.dev) |

One schema, both jobs: define it in zod once, use it for the form resolver and for server-side validation. Never validate the same shape twice in two places.

## Backend & platform

| Task | Library |
| --- | --- |
| Database access / ORM | [Drizzle](https://orm.drizzle.team) |
| Authentication (self-hosted, own your user table) | [Better Auth](https://better-auth.com) |
| Authentication (managed, fastest to ship) | [Clerk](https://clerk.com) |
| Transactional email | [Resend](https://resend.com) + [React Email](https://react.email) |
| Payments & subscriptions | [Stripe](https://stripe.com) |
| Background jobs / durable workflows | [Trigger.dev](https://trigger.dev) |
| Product analytics, feature flags, session replay | [PostHog](https://posthog.com) |
| Error & performance monitoring | [Sentry](https://sentry.io) |
| Rate limiting, edge KV, queues | [Upstash](https://upstash.com) |

The auth split: Better Auth by default — users live in your database, sessions revoke instantly, and there's no per-MAU bill that scales against you. Clerk when someone is paying you to ship this week and the managed UI plus B2B org features are worth the pricing curve. Don't start a new project on Auth.js/NextAuth; even its maintainers point new projects elsewhere.

## Dates, i18n, and language-level gaps

| Task | Library |
| --- | --- |
| Date & time arithmetic, time zones | **Temporal** (ES2026) via [temporal-polyfill](https://www.npmjs.com/package/temporal-polyfill) |
| Date & time formatting | `Intl.DateTimeFormat` — no library |
| Internationalization (Next) | [next-intl](https://next-intl.dev) |
| Internationalization (other frameworks) | [i18next](https://www.i18next.com) |

Temporal reached Stage 4 and shipped in ES2026 — it's native in Chrome 144+, Firefox 139+, and Edge 144+, with Safari still partial as of mid-2026. Ship `temporal-polyfill` (~30kB gzip, drops out once Safari lands) and write against the standard. **Do not add moment, dayjs, or date-fns to new code** — they exist to patch holes the language has now filled.

## Tooling

| Task | Library |
| --- | --- |
| Build tool / dev server (non-Next) | [Vite](https://vite.dev) |
| Unit & component tests | [Vitest](https://vitest.dev) + [Testing Library](https://testing-library.com) |
| End-to-end tests | [Playwright](https://playwright.dev) |
| Lint + format | [Biome](https://biomejs.dev) |
| Package manager | [pnpm](https://pnpm.io) |
| Monorepo task runner | [Turborepo](https://turborepo.com) |

Biome replaces ESLint + Prettier with one fast binary and one config. Keep ESLint only where you depend on rules Biome hasn't ported — Next's own lint rules are the usual reason, and the two can run side by side.

## Common mismatches to catch

- **Toasts built by hand or with a modal library** → Sonner exists for exactly this.
- **A `<div>`-based dropdown/dialog with manual focus handling** → base-ui, which handles accessibility, focus trapping, and dismissal.
- **Animating a number by re-rendering text** → NumberFlow handles digit transitions properly.
- **Rendering a 1,000+ row list directly** → Virtuoso before reaching for pagination hacks.
- **A `useState`-per-component web of props for shared state** → zustand.
- **`useEffect` + `fetch` + `setLoading` + `setError`** → TanStack Query. This one is nearly always worth flagging.
- **Filter and pagination state in `useState`, lost on refresh** → nuqs.
- **Template-literal className ternaries three conditions deep** → clsx (or cva if it's variant-shaped).
- **A component with a `className` prop whose defaults can't be overridden** → tailwind-merge.
- **Hand-rolled sortable table with `useState` for sort direction** → TanStack Table.
- **Zod schema on the client, hand-written `if` checks on the server** → one schema, both sides.
- **`dayjs`/`moment` added to a greenfield project** → Temporal + `Intl.DateTimeFormat`.
- **Rolling your own session cookies and password hashing** → Better Auth.
- **A cron endpoint doing long work inside a serverless request** → Trigger.dev.

## Contested calls

Read [decisions.md](decisions.md) when the pick above isn't obviously right for the situation — it covers the real tradeoffs behind state management, headless vs. batteries-included tables, editors, auth, ORM, Biome vs. ESLint, and what deliberately isn't on this list yet.

## Provenance

The spine of this list — base-ui, cmdk, Sonner, input-otp, Leva, motion, NumberFlow, torph, Cobe, Satori, shiki, Liveline, recharts, dnd kit, Virtuoso, zustand, clsx, cva, next-themes — is adapted from Emil Kowalski's [pick-ui-library](https://github.com/emilkowalski/skills/blob/main/skills/pick-ui-library/SKILL.md). The data, forms, backend, dates, and tooling layers are additions.
