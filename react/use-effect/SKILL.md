---
name: react-useffect
description: "Guidance on when to use useEffect and how to replace it with correct React patterns. Triggers on: useEffect, side effect, synchronize state, useEffect with useState, useEffect fetch, useEffect cleanup, derived state, useSyncExternalStore, external system, subscription, useEffect dependency array, useEffect infinite loop, useEffect on mount, You Might Not Need an Effect."
user-invocable: true
argument-hint: "[FILE=<path> | AREA=<description>]"
---

Apply this skill to detect and eliminate misused `useEffect` hooks — replacing each with the correct React pattern — based on React's "You Might Not Need an Effect" guidance.

## MANDATORY PREPARATION

1. Read the sub-files for full reference material:
   - `./mental-model.md` — rendering model, lifecycle, cleanup, StrictMode, dependency array rules
   - `./anti-patterns.md` — 12 anti-patterns with ❌/✅ examples
   - `./when-to-use.md` — legitimate uses: DOM, WebSocket, browser APIs, animations, analytics
2. If a file argument is provided, read it and identify every `useEffect` call.
3. If no argument is given, check recently changed files: `git diff --name-only HEAD~1`.
4. Before proposing any replacement, confirm what external system (if any) the effect is syncing with.

---

## Quick Reference

| File | Contents |
|------|----------|
| [mental-model.md](./mental-model.md) | What effects are, rendering model, lifecycle, cleanup, StrictMode, dependency array rules |
| [anti-patterns.md](./anti-patterns.md) | 12 anti-patterns with ❌/✅ examples — derive at render, useMemo, key prop, event handlers, React Query, useSyncExternalStore |
| [when-to-use.md](./when-to-use.md) | When effects ARE correct: DOM, WebSocket, browser APIs, animations, analytics |

---

## Core Principle

**Effects are escape hatches for syncing React with external systems.**

External systems: DOM nodes, WebSocket connections, browser APIs (resize, online/offline), non-React widgets, third-party imperative libraries.

If there is no external system involved, there is almost certainly a better solution:
- Derive at render time (no hook needed)
- Handle in an event handler
- Use `useMemo` for expensive computation
- Pass via props / lift state up
- Use `useSyncExternalStore` for external stores
- Use React Query for data fetching

---

## Decision Flowchart

**CRITICAL**: Run every `useEffect` through this flowchart before accepting it. If no external system is identified, the effect must be replaced — not kept with a comment.

```
Do I need useEffect here?

Is there an external system to sync with?
(DOM node, WebSocket, browser API, non-React widget)
├── Yes → useEffect is likely correct — see when-to-use.md
└── No
    ├── Am I transforming/deriving data from props or state?
    │   └── Compute it directly during render (no effect needed)
    ├── Am I caching an expensive computation?
    │   └── useMemo
    ├── Am I resetting state when a prop changes?
    │   └── key prop on the component
    ├── Am I reacting to a user action (click, submit)?
    │   └── Event handler (not effect)
    ├── Am I subscribing to an external store?
    │   └── useSyncExternalStore
    ├── Am I fetching data?
    │   └── React Query (useQuery)
    └── Am I notifying a parent or sharing logic between handlers?
        └── Call directly / lift state / extract function
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `useEffect` + `setState` to derive/transform data | Compute directly during render |
| `useEffect` + `setState` for expensive calculation | `useMemo` |
| `useEffect` to reset state when prop changes | `key` prop on the component |
| `useEffect` watching state to fire a POST request | Move to the event handler that triggered the state change |
| `useEffect` to notify parent about child state change | Call parent callback directly in event handler |
| `useEffect` + `useState` to subscribe to external store | `useSyncExternalStore` |
| `useEffect` + `fetch` for data fetching | React Query (`useQuery`) |
| `useEffect` with no cleanup for event listeners | Always return cleanup: `() => window.removeEventListener(...)` |
| Missing value in dependency array (lint suppression) | Fix the effect, don't suppress the lint rule |
| `useEffect` for one-time app initialisation | Module-level code outside components |
| Empty deps `[]` meaning "run once" | Understand: `[]` means "sync with nothing"; use it only when the effect genuinely depends on nothing reactive |

**IMPORTANT**: When reviewing existing code, scan all `useEffect` calls before writing any new code — they are the most common source of pattern violations.

---

## Architectural Design Rules

- **Parents own orchestration; children are simple and declarative.** If a child needs an effect to push data back up or react to sibling state, redesign the tree instead.
- **Each component does one job.** If a component needs an effect to juggle multiple concerns, split it.
- **Lift state or redesign the data layer before adding effects.** An effect is rarely the right answer to a data-sharing problem.
- **Propose a cleaner component tree first.** If a feature seems to require heavy effect usage, step back and consider whether the hierarchy itself needs redesigning.

---

## Agent Operational Rules

- **Validate before outputting.** Check every piece of React code against these rules before responding. If a draft uses `useEffect` where a better pattern exists, rewrite it first.
- **Never add an effect "just in case".** Don't use `useEffect` as a safety net or to compensate for a missing abstraction.
- **Proactively migrate legacy effects.** When refactoring existing code, migrate every `useEffect` that violates these rules — don't leave old patterns in place.
- **Explain your pattern choice.** In responses, briefly note which pattern was chosen and why `useEffect` was avoided (e.g. "derives at render time — no effect needed").
- **Ask before guessing.** If a requirement is ambiguous and an effect might seem tempting, ask for clarification rather than reaching for `useEffect`.
- **Write lint-clean code.** Generate code that would pass a strict `no-useEffect` lint rule — no suppressions, no workarounds.

---

## Enforcement & Documentation

- **Suggest the lint rule.** When reviewing a project, always recommend adding a `no-restricted-syntax` or `eslint-plugin-react-hooks`-based rule to forbid or flag `useEffect` outside approved patterns — if the project doesn't already have one.
- **Reference the official guide.** When explaining a decision, cite React's official "You Might Not Need an Effect" documentation.

**NEVER:**
- Use `useEffect` + `setState` to derive or transform data from props or state — compute it during render instead
- Fetch data with `useEffect` + `useState` — use React Query or a framework data-fetching primitive
- Subscribe to an external store with `useEffect` + `useState` — use `useSyncExternalStore`
- Suppress `exhaustive-deps` lint warnings — if adding a dependency feels wrong, redesign the effect
- Write a `useEffect` that registers an event listener or subscription without returning a cleanup function
- Add `useEffect` when the trigger is a user action (click, submit, input) — that belongs in an event handler
- Suggest `useEffect` as a "just in case" safety net or to compensate for a missing abstraction
- Leave `useEffect` anti-patterns in place during a refactor — migrate every violation found

---

## Review Checklist

- [ ] Every `useEffect` has an external system it's syncing with (DOM, API connection, browser API)
- [ ] No `useEffect` + `setState` for derived/computed values — derive at render time instead
- [ ] No `useEffect` + `setState` for expensive calculations — `useMemo` instead
- [ ] No `useEffect` watching state to trigger a POST/mutation — moved to event handler
- [ ] No `useEffect` to notify parent of state changes — event handler or lifted state
- [ ] Data fetching uses React Query, not `useEffect` + `useState`
- [ ] External store subscriptions use `useSyncExternalStore`, not `useEffect` + `useState`
- [ ] Every `useEffect` that sets something up has a cleanup function
- [ ] No suppressed lint warnings on dependency arrays
- [ ] State reset on prop change uses `key` prop, not `useEffect`
- [ ] A no-useEffect lint rule is present in the project (or suggested if missing)
- [ ] Component tree structure was considered before reaching for any effect

## Verify Result

- All `useEffect` calls in scope have been run through the Decision Flowchart
- Every replaced effect has a before/after explanation naming the correct pattern
- Output is lint-clean — no `eslint-disable` comments introduced
- Review Checklist passes for the area reviewed

Effects are escape hatches, not orchestration tools — every `useEffect` must have an external system it is syncing with, or it must not exist.
