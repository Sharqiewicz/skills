# Contested calls

The picks in `SKILL.md` are defaults, not laws. These are the ones where the runner-up is genuinely defensible — the tradeoff, and the condition under which you should deviate. If a section here doesn't apply, the default in `SKILL.md` stands and you shouldn't relitigate it.

---

## State: zustand vs. TanStack Query vs. nuqs vs. `useState`

Not a competition — a routing decision. Ask **who owns this value.**

| Owner | Tool |
| --- | --- |
| One component, dies with it | `useState` |
| The server; can go stale | TanStack Query |
| The URL; must survive refresh & be shareable | nuqs |
| The client, shared across a tree, no URL meaning | zustand |

The common failure is reaching for a global store to hold API data, then hand-writing cache invalidation, refetch-on-focus, and request dedup that TanStack Query already ships. If you find yourself writing `isLoading` booleans in a zustand store, you routed wrong.

**Deviate when:** you have deeply nested, high-frequency updates where re-render scope matters (a canvas editor, a spreadsheet) — Jotai's atom model fits that shape better than zustand's single store. Redux Toolkit only if the team already runs it; don't introduce it.

---

## Tables: TanStack Table vs. a real grid

TanStack Table is headless — ~15kB, MIT, no UI. You render the markup, which is exactly why it disappears into your design system. It covers sorting, filtering, grouping, pagination, and column sizing for what is realistically 90% of application tables.

**Deviate when** the requirement list reads like a spreadsheet product: pivoting, row grouping with aggregation, Excel export, master/detail, integrated charts, clipboard range selection. Rebuilding that on a headless core is months of work. AG Grid ships it — but the features that matter are Enterprise, roughly $999/developer/year, and the community bundle is ~330kB gzip against TanStack's ~15kB. Make the license and bundle cost explicit before recommending it, and never recommend it for a table with a dozen columns and sorting.

Pair TanStack Table with Virtuoso for virtualization — it doesn't include one.

---

## Forms: react-hook-form vs. TanStack Form

react-hook-form is the default. It's uncontrolled and ref-based, so typing doesn't re-render the tree, and it stays fast at hundreds of inputs with no architectural effort. The ecosystem, resolver support, and available answers are much larger.

**Deviate when:** you need the same form logic across React *and* Vue/Solid/Angular, or you want end-to-end type inference strict enough that field paths are checked at compile time. TanStack Form's store-based reactivity keeps re-render scope automatic as forms grow, and it's stable at v1 — but its composition APIs (`createFormHook`, `AppField`) are still moving, so pin and expect churn.

Either way, zod owns the schema. Don't let the form library define your validation types.

---

## Auth: Better Auth vs. Clerk

The axis is **who owns the user table**, not which SDK is nicer.

**Better Auth** — users in your database, sessions revocable immediately, organizations/passkeys/RBAC as first-party plugins, no per-MAU cost. You own migrations, email deliverability, and the sign-in UI. Right for anything expected to grow a real user count or that has data-residency constraints.

**Clerk** — production sign-in screens, user management, and B2B org UI on day one. Right when time-to-market is the actual constraint. Say the pricing curve out loud when recommending it: per-MAU billing that is cheap at launch and a line item at scale, and migrating off it later means moving identities.

**Auth.js / NextAuth** — maintenance-only. Don't start new projects on it; its own maintainers now direct new projects toward Better Auth. If a project already runs it and works, leave it alone.

Supabase Auth is fine and effectively free if the project is *already* on Supabase Postgres. It isn't a reason to adopt Supabase.

---

## Database: Drizzle vs. Prisma

Drizzle is SQL-shaped: the query builder maps to SQL you can read, it's thin at runtime, and it works in edge runtimes without a separate engine. That's why it's the default here.

**Deviate when:** the team wants a schema DSL and generated client over writing SQL-like queries, or already runs Prisma in production. Prisma's tooling (Studio, migrations) is more polished and its docs are broader. Migrating an existing Prisma app to Drizzle to satisfy this list is not a good use of anyone's week — flag the preference and move on.

Either way, run migrations as versioned files in the repo. Don't push schema changes straight to production databases.

---

## Editors: Tiptap vs. Plate vs. Lexical

**Tiptap** (ProseMirror) is the default: best docs, largest extension ecosystem, and collaboration/CRDT support that actually works. Right for CMS, docs, knowledge bases, comment boxes.

**Plate** (Slate) when the project is already shadcn/ui — the plugin system and copy-the-component-into-your-repo model line up exactly, and you get styled editor components rather than assembling them.

**Lexical** (Meta) when the editor *is* the product and performance is the constraint — ~22kB core, minimal DOM work. The cost is a steeper, lower-level plugin model and much more code to reach parity with Tiptap's defaults.

Rich text is heavy no matter which you pick. If the requirement is really "bold, italic, links," a markdown textarea plus a renderer is smaller and less to maintain.

---

## Lint: Biome vs. ESLint + Prettier

Biome is one Rust binary doing both jobs, roughly an order of magnitude faster, one config file, no plugin resolution problems. Default for new projects.

**Deviate when** you depend on rules Biome hasn't ported — `eslint-config-next`, `eslint-plugin-testing-library`, custom in-house rules, or an import-boundary plugin enforcing architecture. Running both is normal and supported: Biome formats and handles the common rules, ESLint runs the narrow plugin set.

---

## Dates: why not date-fns

Temporal is ES2026 and native in Chrome 144+, Firefox 139+, Edge 144+. Safari is still partial as of mid-2026, so `temporal-polyfill` is the shipping path — but you're writing standard code that gets *smaller* over time as the polyfill drops out, instead of code coupled to a library's API.

date-fns and dayjs exist because `Date` was broken. It isn't anymore. Keep them in codebases that already use them heavily; don't add them to new ones. moment is deprecated by its own maintainers and should be treated as a migration target.

`Intl.DateTimeFormat` handles formatting and locales natively, including relative times via `Intl.RelativeTimeFormat`. It has needed no library for years.

---

## Deliberately not on the list

Not omissions — judgment calls, revisit as they mature.

- **Local-first sync engines** (TanStack DB, Zero, ElectricSQL, PowerSync). Genuinely exciting, and the right shape for collaborative and offline apps. Still moving fast enough that adopting one is a bet on the vendor, not just the library. Recommend only when offline or realtime multiplayer is a stated requirement, and say plainly that it's an early call.
- **Component libraries with baked-in visual design** (MUI, Mantine, Chakra). They ship faster on day one and then fight your designer for the rest of the project. base-ui + Tailwind, or shadcn/ui, gets you there without the fight.
- **CSS-in-JS runtimes** (styled-components, Emotion). Runtime cost, poor RSC story, and both are effectively in maintenance mode. Tailwind or CSS Modules.
- **tRPC.** Still good, and correct if you own both ends and want end-to-end types without codegen. Left off because Server Actions and Server Components cover most of what it was reached for in a Next App Router codebase.
- **A GraphQL client.** If the API is GraphQL, use one (urql or Apollo). Adopting GraphQL to get a client is backwards.
