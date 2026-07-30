# find-library

A **lookup skill**: name a task, get one library. Curated and opinionated — it answers "what should I use for toasts?" with a pick and a sentence of rationale, not a comparison table.

**Scope:** Web. React + Next.js (App Router) + Tailwind. For React Native, use `find-library-mobile`.

## What's inside

| File | Covers |
| --- | --- |
| `SKILL.md` | The full lookup tables (UI primitives · motion · data display · interaction · state & styling · forms · backend · dates & i18n · tooling) + common mismatches |
| `decisions.md` | The contested calls — state routing, headless table vs. grid, forms, auth, ORM, editors, Biome vs. ESLint, why not date-fns, and what's deliberately excluded |

`SKILL.md` holds the whole list on purpose. A lookup skill needs to answer in one glance; `decisions.md` is the one hop away for when the default isn't obviously right.

## How to invoke it

**Explicitly only** — `/find-library`. The frontmatter sets `disable-model-invocation: true`, matching the inspiration: these are taste-driven picks, and they shouldn't silently override a project's existing choices or fire every time someone says "toast."

To make it auto-trigger, delete that line from `SKILL.md` frontmatter.

```
/find-library I need a searchable command palette
/find-library what should I use for auth in this app?
/find-library review package.json — anything we're doing the hard way?
```

That last one is the underrated mode: pointed at an existing `package.json`, it flags `useEffect`+`fetch` where TanStack Query belongs, filter state in `useState` that should be in the URL, and dayjs in a greenfield project.

## The rules it follows

1. Identify the **task**, not the library the user named.
2. Read `package.json` first — respect what's installed, flag but don't churn.
3. Ask whether a library is needed at all. A hover fade is a CSS transition.
4. One recommendation, not a menu.
5. Say so explicitly when the task falls outside the list.

## Pairs with

- **`find-library-mobile`** — the React Native sibling. zustand, TanStack Query, react-hook-form, and zod are deliberately the same picks on both sides.
- **`rules-apple`** — how to build the thing well once the library is chosen.
- **`shadcn`** — for actually wiring up shadcn/ui components.

## Sourcing & maintenance

The UI/motion spine is adapted from Emil Kowalski's [pick-ui-library](https://github.com/emilkowalski/skills/blob/main/skills/pick-ui-library/SKILL.md), with credit in `SKILL.md`. The data, forms, backend, dates, and tooling layers are additions.

Picks verified against current docs as of **July 2026** — notably base-ui at v1.x stable, TanStack Form v1 (composition APIs still moving), Temporal at Stage 4 / ES2026 with Safari still partial, and Auth.js in maintenance. This skill goes stale faster than a design skill; re-verify before trusting a pick in a greenfield decision.
