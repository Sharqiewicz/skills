---
name: find-library-mobile
description: "Pick the right library for a React Native + Expo task from a curated, opinionated list — routing, lists, bottom sheets, icons, styling, animation, gestures, haptics, storage, state, forms, keyboard, camera/media, notifications, Sign in with Apple, Apple Pay, builds/OTA, monitoring, and E2E testing. One pick per task, not a menu. Only runs when explicitly invoked; it does not trigger on its own."
disable-model-invocation: true
---

# Finding The Right Library (React Native)

A lookup skill. When invoked with a task ("I need a bottom sheet", "how do I store the auth token?", "what should I use for lists?"), match the task to the curated list below and recommend **one** library. These are deliberate, taste-driven picks — don't substitute alternatives outside this list unless the user asks for one or the task genuinely isn't covered.

**Stack assumption:** React Native + **Expo** (managed workflow, `expo prebuild` when native config is needed), iOS-first. For web, use `find-library` instead. For *how* to build the screen to Apple's standards once the library is chosen, that's `rules-apple-mobile`.

## How to use this

1. **Identify the task**, not the library the user named.
2. **Check what's already installed.** Read `package.json` first. If the project already uses a listed library, use it. If it uses a competitor (FlatList instead of FlashList, NativeWind instead of Unistyles), flag the recommendation but **don't churn the dependency without being asked**.
3. **Prefer the Expo SDK module over a third-party one** when both exist. `expo-*` packages are versioned against the SDK, config-plugin-ready, and don't break on upgrade. Reach outside Expo only when the list below says to.
4. **Prefer native-backed over hand-rolled JS.** Native components inherit gestures, blur, haptics, safe-area behaviour, and VoiceOver for free. A JS reimplementation inherits none of it and will feel wrong on iOS.
5. **Check whether a library is needed at all.** A `formSheet` screen is cheaper than a bottom-sheet library. A 20-item list is a `ScrollView`. Native `Alert` beats a custom modal.
6. **Recommend one library**, state what it's for in one sentence, and install/wire it up if that's part of the request.
7. **If the call is genuinely contested** (styling, lists, navigation, storage, local-first) → read [decisions.md](decisions.md).
8. If the task isn't covered, say so explicitly and recommend from your own knowledge — but be clear you've left the curated list.

## Foundation

| Task | Library |
| --- | --- |
| The framework itself | [Expo](https://expo.dev) — not bare React Native CLI |
| Routing & navigation | [Expo Router](https://docs.expo.dev/router/introduction/) (file-based, built on React Navigation) |
| Screen-level native behaviour (large titles, edge-back, sheet detents) | [`@react-navigation/native-stack`](https://reactnavigation.org/docs/native-stack-navigator) — configured *through* Expo Router |
| Safe areas (Dynamic Island, home indicator) | [react-native-safe-area-context](https://github.com/th3rdwave/react-native-safe-area-context) |

Expo Router is React Navigation with file-based routing on top — you aren't choosing between them, you're choosing whether to write the navigator tree by hand. Adopting Expo Router gets you automatic deep linking and typed routes; you still reach for native-stack options (`headerLargeTitle`, `presentation: 'formSheet'`, `sheetAllowedDetents`) via screen options.

**Always use `native-stack`, never the JS `stack` navigator.** The JS one reimplements the iOS push transition and edge-swipe-back in JavaScript, and it shows.

## Lists & layout

| Task | Library |
| --- | --- |
| Long or performance-sensitive lists | [FlashList v2](https://shopify.github.io/flash-list/) |
| Lists with rich, interactive, wildly variable rows | [Legend List](https://www.legendapp.com/open-source/list/) |
| Images (caching, transitions, blurhash) | [expo-image](https://docs.expo.dev/versions/latest/sdk/image/) |
| SVG rendering | [react-native-svg](https://github.com/software-mansion/react-native-svg) |
| Custom drawing, canvas, shaders, complex visual effects | [React Native Skia](https://shopify.github.io/react-native-skia/) |

FlashList v2 is the default — it measures items and computes positions before first paint, so there are no size estimates to tune and no blank cells while scrolling. It requires the New Architecture. Legend List is faster on very complex rows but is younger and less battle-tested; see [decisions.md](decisions.md).

Use plain `ScrollView` under ~50 static items. Virtualization has real overhead and isn't free.

## Sheets, overlays & feedback

| Task | Library |
| --- | --- |
| A modal sheet that's just another screen | native-stack `presentation: 'formSheet'` — **no library** |
| Sheets with custom snap points, drag interaction, scrollable content | [@gorhom/bottom-sheet](https://ui.gorhom.dev/components/bottom-sheet) |
| Confirmations, destructive choices | native `Alert` / `ActionSheetIOS` — **no library** |
| Toasts / transient status | [burnt](https://github.com/nandorojo/burnt) (native iOS toast/haptic feedback) |
| Blur & system materials | [expo-blur](https://docs.expo.dev/versions/latest/sdk/blur-view/) |

The sheet split matters and is routinely got wrong: if the sheet is a *destination* (a detail view, a form you push into), it's a native-stack screen with `presentation: 'formSheet'` and `sheetAllowedDetents` — free, native, correct edge cases. Reach for `@gorhom/bottom-sheet` only when you need snap points, drag-driven UI that responds continuously, or a sheet that isn't a route. Never hand-roll one with `PanResponder`.

## Icons & typography

| Task | Library |
| --- | --- |
| iOS system icons (SF Symbols) | [expo-symbols](https://docs.expo.dev/versions/latest/sdk/symbols/) |
| Cross-platform icon set | [lucide-react-native](https://lucide.dev/guide/packages/lucide-react-native) |
| Custom fonts | [expo-font](https://docs.expo.dev/versions/latest/sdk/font/) |

On iOS, SF Symbols via `expo-symbols` are the right answer: they scale with Dynamic Type, match system weight, and animate. `react-native-vector-icons` shipping a bundled icon font is the usual thing to replace.

## Styling

| Task | Library |
| --- | --- |
| Styling (default) | [Unistyles 3](https://www.unistyl.es) |
| Styling when the team already writes Tailwind and shares code with web | [NativeWind](https://www.nativewind.dev) |

Unistyles 3 is a superset of `StyleSheet` implemented in C++ over Nitro modules — themes, variants, and breakpoints update styles natively without re-rendering the React tree, and it benchmarks roughly 3× faster than NativeWind on both platforms. It's the default here because it stays out of the way and costs nothing at runtime.

NativeWind is the reasonable deviation, not a mistake — pick it when the team's muscle memory is Tailwind or when components are genuinely shared with a web codebase. See [decisions.md](decisions.md) for the honest version of this tradeoff.

## Motion, gestures & haptics

| Task | Library |
| --- | --- |
| Animation engine (springs, worklets, shared values) | [react-native-reanimated](https://docs.swmansion.com/react-native-reanimated/) |
| Declarative enter/exit and simple animated components | [Moti](https://moti.fyi) (wraps Reanimated) |
| Gestures (pan, pinch, long-press, swipeable rows) | [react-native-gesture-handler](https://docs.swmansion.com/react-native-gesture-handler/) |
| Haptic feedback | [expo-haptics](https://docs.expo.dev/versions/latest/sdk/haptics/) |

Reanimated is the engine; Moti is the ergonomic layer for the common cases (fade in, slide up, presence). Use Moti when you'd otherwise write ten lines of `useSharedValue` + `withTiming` for a fade.

**Never use the built-in `Animated` API for anything gesture-driven** — it runs on the JS thread and drops frames under load. And Reduce Motion is not automatic in Reanimated the way it is in CSS: pass `reduceMotion: ReduceMotion.System` per animation.

## State, data & storage

| Task | Library |
| --- | --- |
| Client state management | [zustand](https://zustand.docs.pmnd.rs) |
| Server state (fetching, caching, offline-aware refetch) | [TanStack Query](https://tanstack.com/query) |
| Fast key-value storage (preferences, flags, store persistence) | [react-native-mmkv](https://github.com/mrousavy/react-native-mmkv) |
| Tokens, secrets, anything sensitive | [expo-secure-store](https://docs.expo.dev/versions/latest/sdk/securestore/) |
| Relational / offline data with queries and relations | [expo-sqlite](https://docs.expo.dev/versions/latest/sdk/sqlite/) + [Drizzle](https://orm.drizzle.team) |

The storage split, in order of how often it's got wrong:

1. **Auth tokens go in `expo-secure-store`** (Keychain), never MMKV, never AsyncStorage. This is a security bug, not a preference.
2. **Preferences, flags, small caches, zustand persistence → MMKV.** Synchronous C++, no promises, ~30× faster than AsyncStorage.
3. **Anything with queries, relations, or hundreds of rows → expo-sqlite.** Don't hide a database inside a serialized JSON blob in a KV store.
4. **AsyncStorage** only for Expo Go compatibility or a low-risk migration path in an older app.

Same rule as web: server state belongs to TanStack Query, not zustand. On mobile it matters more — Query's focus/reconnect refetch handles backgrounded apps and flaky networks that a hand-rolled store won't.

## Forms & keyboard

| Task | Library |
| --- | --- |
| Forms | [react-hook-form](https://react-hook-form.com) |
| Schema validation | [zod](https://zod.dev) |
| Keyboard avoidance, sticky footers, keyboard-aware scrolling | [react-native-keyboard-controller](https://kirillzyusko.github.io/react-native-keyboard-controller/) |

React Native's built-in `KeyboardAvoidingView` uses `keyboardDidShow`, which fires *after* the keyboard finishes animating — too late to move in sync with it, and it behaves differently per platform. `react-native-keyboard-controller` exports a drop-in `KeyboardAvoidingView` with the same props plus `KeyboardAwareScrollView` and `KeyboardStickyView`. Swapping the import is usually the entire fix.

## Device & platform capabilities

| Task | Library |
| --- | --- |
| Push notifications | [expo-notifications](https://docs.expo.dev/versions/latest/sdk/notifications/) |
| Sign in with Apple (App Store requirement 4.8) | [expo-apple-authentication](https://docs.expo.dev/versions/latest/sdk/apple-authentication/) |
| Apple Pay & card payments | [@stripe/stripe-react-native](https://github.com/stripe/stripe-react-native) |
| In-app purchases & subscriptions | [RevenueCat](https://www.revenuecat.com/docs/getting-started/installation/reactnative) |
| Camera | [expo-camera](https://docs.expo.dev/versions/latest/sdk/camera/) |
| Photo library picking | [expo-image-picker](https://docs.expo.dev/versions/latest/sdk/imagepicker/) |
| Location | [expo-location](https://docs.expo.dev/versions/latest/sdk/location/) |
| Biometric unlock | [expo-local-authentication](https://docs.expo.dev/versions/latest/sdk/local-authentication/) |
| App Store rating prompt | [expo-store-review](https://docs.expo.dev/versions/latest/sdk/store-review/) |
| Splash screen | [expo-splash-screen](https://docs.expo.dev/versions/latest/sdk/splash-screen/) |
| App Tracking Transparency | [expo-tracking-transparency](https://docs.expo.dev/versions/latest/sdk/tracking-transparency/) |

Digital goods consumed inside the app must go through StoreKit, not Stripe — RevenueCat wraps that. Apple Pay via Stripe is for physical goods and real-world services only. Getting this wrong is a rejection, not a bug.

Every permission module above needs a purpose string in `Info.plist` via its config plugin. A missing purpose string is a silent crash on device that won't reproduce in the simulator.

## Build, release & monitoring

| Task | Library |
| --- | --- |
| Cloud builds & store submission | [EAS Build / Submit](https://docs.expo.dev/eas/) |
| Over-the-air JS updates | [expo-updates](https://docs.expo.dev/versions/latest/sdk/updates/) / EAS Update |
| Crash & performance monitoring | [@sentry/react-native](https://docs.sentry.io/platforms/react-native/) |
| Product analytics & feature flags | [posthog-react-native](https://posthog.com/docs/libraries/react-native) |
| End-to-end tests | [Maestro](https://www.maestro.dev) |

Maestro over Detox: YAML flows, no build instrumentation, and it doesn't fall over on every RN upgrade.

OTA updates ship JS and assets only. Anything touching native code — a new Expo module, a config plugin change, an SDK bump — needs a real build. Reaching for EAS Update to fix a native crash won't work.

## Common mismatches to catch

- **`FlatList` rendering hundreds of rows with visible blanking** → FlashList v2.
- **A bottom sheet hand-rolled with `PanResponder` and `Animated`** → native-stack `formSheet`, or `@gorhom/bottom-sheet` if it truly needs snap points.
- **Auth tokens in AsyncStorage or MMKV** → `expo-secure-store`. Flag this as a security issue, not a style note.
- **AsyncStorage used as the app's entire data layer** → MMKV for KV, expo-sqlite for anything relational.
- **`KeyboardAvoidingView` from `react-native` with per-platform offset hacks** → `react-native-keyboard-controller`.
- **`Animated` from `react-native` driving a gesture** → Reanimated + gesture-handler.
- **A Reanimated animation with no `ReduceMotion` config** → accessibility bug; Reduce Motion is opt-in here.
- **`react-native-vector-icons` for iOS system-looking icons** → `expo-symbols`.
- **The JS `stack` navigator** → `native-stack`.
- **`useEffect` + `fetch` + `setLoading`** → TanStack Query, especially with backgrounding and flaky networks in play.
- **A custom modal used for a destructive confirmation** → native `Alert` / `ActionSheetIOS`.
- **`moment` or `dayjs` bundled into the app** → `Intl` + `temporal-polyfill`; bundle size is a user-facing cost here.
- **Bare RN CLI chosen "because we need native modules"** → Expo with `prebuild` and config plugins does this now.
- **Subscriptions billed through Stripe inside the app** → RevenueCat/StoreKit, or the build gets rejected.

## Pairs with

- **`rules-apple-mobile`** — once the library is chosen, that skill covers how to use it to Apple's standards (44pt targets, detents, Dynamic Type, App Store requirements).
- **`find-library`** — the web sibling. zustand, TanStack Query, react-hook-form, and zod are deliberately the same picks on both sides.

## Contested calls

Read [decisions.md](decisions.md) for the real tradeoffs behind Unistyles vs. NativeWind, FlashList vs. Legend List, Expo Router vs. hand-written navigators, Expo vs. bare RN, storage layering, and what deliberately isn't on this list.

## Provenance

Structure and format adapted from Emil Kowalski's [pick-ui-library](https://github.com/emilkowalski/skills/blob/main/skills/pick-ui-library/SKILL.md); the React Native picks are original. Verified against current Expo SDK, React Native, and library docs as of July 2026.
