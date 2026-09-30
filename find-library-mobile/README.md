# find-library-mobile

A **lookup skill**: name a task, get one library. Curated and opinionated — it answers "what should I use for a bottom sheet?" with a pick and a sentence of rationale, not a comparison table.

**Scope:** React Native + **Expo**, iOS-first. For web, use `find-library`.

## What's inside

| File | Covers |
| --- | --- |
| `SKILL.md` | The full lookup tables (foundation · lists & layout · sheets & overlays · icons · styling · motion/gestures/haptics · state & storage · forms & keyboard · device capabilities · build & monitoring) + common mismatches |
| `decisions.md` | The contested calls — Unistyles vs. NativeWind, FlashList vs. Legend List, Expo Router vs. hand-written navigators, Expo vs. bare RN, the four-way storage split, and what's deliberately excluded |

## How to invoke it

**Explicitly only** — `/find-library-mobile`. The frontmatter sets `disable-model-invocation: true`: these are taste-driven picks and shouldn't silently override a project's existing choices.

To make it auto-trigger, delete that line from `SKILL.md` frontmatter.

```
/find-library-mobile I need a bottom sheet with snap points
/find-library-mobile where should the auth token live?
/find-library-mobile review package.json — anything we're doing the hard way?
```

## Its house rules

Beyond "one pick per task," this skill carries two biases the web version doesn't:

1. **Prefer the Expo SDK module over a third-party one** when both exist — versioned with the SDK, config-plugin-ready, doesn't break on upgrade.
2. **Prefer native-backed over hand-rolled JS** — you inherit gestures, blur, haptics, safe-area behaviour, and VoiceOver for free. A JS reimplementation inherits none of it and feels wrong on iOS.

That's why several answers are *"no library"*: a `formSheet` screen instead of a sheet library, native `Alert` instead of a custom modal, `ScrollView` instead of virtualization under 50 items.

## What it catches

Typical flags on an existing codebase: auth tokens in AsyncStorage (a security bug, not a style note) · `FlatList` blanking on long lists · a `PanResponder` bottom sheet · `KeyboardAvoidingView` with per-platform offset hacks · the JS `stack` navigator · `Animated` driving a gesture · a Lottie loop that ignores Reduce Motion · subscriptions billed through Stripe instead of StoreKit.

## Pairs with

- **`rules-apple-mobile`** — once the library is chosen, that skill covers how to use it to Apple's standards (44pt targets, detents, Dynamic Type, App Store requirements). This skill picks the tool; that one governs how you hold it.
- **`find-library`** — the web sibling. zustand, TanStack Query, react-hook-form, and zod are deliberately the same picks on both sides.

## Sourcing & maintenance

Structure and format adapted from Emil Kowalski's [pick-ui-library](https://github.com/emilkowalski/skills/blob/main/skills/pick-ui-library/SKILL.md); the React Native picks are original.

Verified against current Expo SDK, React Native, and library docs as of **July 2026**. RN's ecosystem moves faster than the web's — FlashList v2's New Architecture requirement, Unistyles 3's Nitro modules, and Reanimated's major version are all recent enough that re-verifying before a greenfield decision is worth the two minutes.
