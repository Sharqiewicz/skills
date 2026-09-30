---
name: make-prototype-mobile
description: "Build several variants of an animation or UI element in an Expo app behind an on-screen switcher on a dev-only Expo Router screen, with the chosen variant kept in the URL so it survives reloads and opens as a deep link. Dev-only by construction, then deletes the losing variants once one wins. For web, use /prototype. Triggers on: prototype mobile, compare variants React Native, try animation variants, A/B animation Expo, variant switcher, dev-only screen Expo Router, playground route, which spring feels better, compare two designs on device."
user-invocable: true
disable-model-invocation: true
argument-hint: [what to prototype, and how many variants]
---

Put N candidate versions of one animation or UI element side by side on a real device, switchable with a segmented control, so the choice is made by feel instead of by argument. Then delete every variant that lost.

Feel is judged on a device. The switcher exists so a person can flip between variants in one gesture while holding the phone.

## MANDATORY PREPARATION

1. Confirm the question in one sentence and the variant count (recommend 2 to 4). Each variant must differ in one thing the user can name (config, property animated, structure); variants that differ in three things teach nothing.
2. Read the app's `app/` tree and root `app/_layout.tsx` to learn the router layout, and `app.json` for the `scheme` (needed for deep links). If `scheme` is missing, add it to the plan and tell the user; do not guess one.
3. Check installed packages: `expo-router`, `react-native-reanimated`, `react-native-gesture-handler`, `expo-haptics`. Install anything missing with `npx expo install <pkg>`, and say so.
4. Read `/animate-expo` and `/sharqiewicz:rules-animation-performance-mobile` so each variant is built correctly (UI thread, transform and opacity). A variant that is slow because it is sloppy makes the comparison meaningless.

**CRITICAL**: Nothing here may ship. Every prototype file lives under one dev-only route group, and the group is unreachable in a release build (see *Gate*). Never import prototype code from production screens.

**IMPORTANT**: Variants must be comparable. Same data, same size, same trigger, same haptic (or same absence) in every variant, except for the one thing under test.

---

## Layout

```
app/
  (dev)/
    _layout.tsx            Stack for dev screens
    prototype/
      [name].tsx           the switcher screen; reads ?variant=
src/dev/prototypes/<name>/
  index.tsx                registry: { a: ComponentA, b: ComponentB, ... }
  VariantA.tsx
  VariantB.tsx
```

Route groups in parentheses do not appear in the URL, so `app/(dev)/prototype/[name].tsx` is reached at `/prototype/<name>`; see [Expo Router: Notation](https://docs.expo.dev/router/basics/notation/). Keep the variants outside `app/` so they are not treated as routes.

### Gate with `__DEV__`

In the root layout, wrap the dev group so it does not exist in production, using [`Stack.Protected`](https://docs.expo.dev/router/advanced/protected/):

```tsx
<Stack.Protected guard={__DEV__}>
  <Stack.Screen name="(dev)" />
</Stack.Protected>
```

The docs describe protection as client-side route gating; that is enough for a prototype, which holds no secrets. Also guard inside the screen (`if (!__DEV__) return null;`) so a mistake in the layout fails closed. If the project's Expo Router version lacks `Stack.Protected`, use the guard inside the screen only and record that in the report. <!-- UNVERIFIED: minimum Expo Router version for Stack.Protected -->

Add a dev-only entry point (a link in a settings screen wrapped in `{__DEV__ && ...}`) or rely on the deep link below.

## The Switcher Screen

The screen does four things: read the variant, render it, offer the control, and write the choice back.

1. **Read** with [`useLocalSearchParams`](https://docs.expo.dev/router/reference/url-parameters/): `const { name, variant } = useLocalSearchParams<{ name: string; variant?: string }>()`. Search params arrive as strings. Fall back to the first registry key when `variant` is missing or unknown.
2. **Render** `registry[variant]` inside a fixed stage: a neutral background and a fixed-size container, with an on-screen "replay" button for animations that play once, so every variant can be re-triggered without a reload.
3. **Control**: the native segmented control from [`@react-native-segmented-control/segmented-control`](https://docs.expo.dev/versions/latest/sdk/segmented-control/): `values={['A', 'B', 'C']}`, `selectedIndex`, and `onChange={(e) => setVariant(keys[e.nativeEvent.selectedSegmentIndex])}`. It renders `UISegmentedControl` on iOS. Keep the control outside the animated stage and do not animate it.
4. **Write back** with `router.setParams({ variant })`. It updates the URL without pushing history, so the back gesture still leaves the screen in one swipe.

### Persistence, in this order

1. **URL search param** is the source of truth. It survives Fast Refresh and reloads that keep the route, and it is what a deep link carries.
2. **AsyncStorage fallback** for "reopen the app and see what I last picked": on setting a variant, also `AsyncStorage.setItem('prototype:<name>', variant)`; on mount, if no `variant` param is present, read it and `router.setParams`. Install with `npx expo install @react-native-async-storage/async-storage`. The store is unencrypted and async; the first frame renders the default variant until the read finishes, so do not treat that flash as a bug in the variant. See [Expo: AsyncStorage](https://docs.expo.dev/versions/latest/sdk/async-storage/).

**Do not** hold the choice only in `useState`: a reload resets it and it cannot be shared. **Do not** use `useGlobalSearchParams` here; it re-renders background screens on every URL change ([Expo Router: URL parameters](https://docs.expo.dev/router/reference/url-parameters/)).

## Open a Variant as a Deep Link

With a `scheme` in `app.json`, and a development build installed on the simulator or device:

```sh
# uri-scheme (works for simulator and device)
npx uri-scheme open "myapp://prototype/card-press?variant=b" --ios

# simulator only
xcrun simctl openurl booted "myapp://prototype/card-press?variant=b"
```

In Expo Go the scheme is `exp://`, and the app path follows `/--/`: `npx uri-scheme open "exp://127.0.0.1:8081/--/prototype/card-press?variant=b" --ios`. Expo's docs note that incoming-link support in Expo Go is limited, so prefer a development build. Replace `myapp` with the project's scheme; see [Expo: Testing deep links](https://docs.expo.dev/linking/into-your-app/) and [Expo: Linking](https://docs.expo.dev/guides/linking/). Quote the URL so `?` and `&` survive the shell.

Verify the link once before handing it over: run the command, confirm the right variant is selected, then change the segment and confirm the URL param follows.

## Build the Variants

- One file per variant, each exporting a component with the same props. The registry maps a short key to the component.
- Put the tunable values at the top of each file as named constants (spring `duration`, `dampingRatio`, haptic type) so the diff between variants is readable.
- Leave `reduceMotion` at its default on `with*` calls, and gate any core `Animated`, `LayoutAnimation` or Lottie variant per `/sharqiewicz:rules-reduced-motion-mobile`; a variant that ignores Reduce Motion cannot win.
- Keep haptics identical across variants unless haptics are the thing under test. Fire on the causal event only.
- Run each variant on a release-like build on a real iPhone before deciding; simulator and dev mode hide dropped frames.

## Decide and Clean Up

When the user picks a winner:

1. Move the winning implementation into production code where it belongs (or hand it to `/animate-expo`), keeping its constants.
2. Delete every losing variant file and its registry entry.
3. If this was the last prototype, delete `app/(dev)/`, the `Stack.Protected` block, the dev entry link, and any dev-only dependencies installed for it (for example the segmented control).
4. Remove the `prototype:<name>` AsyncStorage key reference from code.
5. Grep for leftovers: `grep -rn "prototype\|(dev)\|__DEV__" app src`, and check none of the deleted variants is still imported.

**NEVER:**
- Import anything from `app/(dev)/` or `src/dev/` into a production screen
- Gate only by hiding the entry link; the route itself must be guarded by `__DEV__`
- Persist the choice in `useState` alone, or in a module-level variable
- Put the switcher inside the animated element or animate the switcher itself
- Change more than one variable between variants, or use different data per variant
- Judge variants in the simulator, in a debug-only frame rate, or with Reduce Motion accidentally left on
- Leave losing variants in the repo "for later"; version control remembers them
- Invent a URL scheme; read it from `app.json` or ask
- Commit, or push, the prototype as part of this skill without the user's explicit go-ahead

## Verify

- [ ] The dev group is guarded by `__DEV__` at the layout and in the screen
- [ ] The segmented control changes the variant and the URL `variant` param together
- [ ] Reloading the app keeps the variant; the deep link command opens the chosen one
- [ ] Every variant replays on demand and respects Reduce Motion
- [ ] Only one variable differs between variants
- [ ] After a decision: losing variants, the registry entries and (if last) the `(dev)` group are gone, and the grep for leftovers is clean
- [ ] Production bundle has no import path into the prototype code

Remember: a prototype is a question with a deadline. Build just enough to answer it on a real phone, then delete everything that is not the answer.
