---
name: rules-reduced-motion-mobile
description: "Reduce Motion rules for React Native + Expo on iOS: reading the setting (AccessibilityInfo.isReduceMotionEnabled, reduceMotionChanged, Reanimated useReducedMotion), the ReduceMotion config on withTiming/withSpring/withDecay and layout animations, what to replace motion with (crossfade, instant), autoplaying video (expo-video), looping Lottie, parallax, why haptics are not motion, and how to test in the simulator and on device. Every rule = Apple guidance + exact API + the common RN mistake. For web, use /animation-accessibility. Triggers on: reduce motion, reduced motion, ReduceMotion, useReducedMotion, ReducedMotionConfig, isReduceMotionEnabled, reduceMotionChanged, prefersCrossFadeTransitions, vestibular, motion sensitivity, autoplay video, lottie loop, parallax, crossfade, accessibility animation, motion accessibility."
user-invocable: true
---

Rules for making React Native motion respect iOS's Reduce Motion setting: read it correctly, choose the right replacement, and catch the animations that no library handles for you.

## MANDATORY PREPARATION

1. **Grep the motion inventory** before writing anything: `withTiming|withSpring|withDecay|withRepeat|withSequence|entering=|exiting=|layout=|LayoutAnimation|Animated\.(timing|spring|loop)|lottie|LottieView|expo-video|VideoView|autoPlay|parallax|sharedTransitionTag`. Each hit is one of the cases below.
2. **Note the Reanimated version.** `ReduceMotion`, `useReducedMotion` and `ReducedMotionConfig` ship in Reanimated; the legacy `Animated` API, `LayoutAnimation`, Lottie and video have no such integration.
3. For where motion belongs at all see `/sharqiewicz:find-animations-mobile`; to build the replacement see `/animate-expo`; for HIG basics see `/sharqiewicz:rules-apple-mobile`; for gestures see `/sharqiewicz:rules-gestures-mobile`.

---

## Why the web tools do not apply

`prefers-reduced-motion`, `@media` queries, `useReducedMotion` from `motion/react` and `<MotionConfig reducedMotion>` are browser and web-library features. React Native has no CSS and no media queries. The native equivalents are the iOS Reduce Motion setting, read through `AccessibilityInfo` or Reanimated, and you apply it per animation (or globally through `ReducedMotionConfig`). Importing a web hook into a native file fails at build time or silently does nothing.

## What Apple asks for

- **Make motion optional.** Never use motion as the only way to communicate something; add another channel (text, color change, icon, haptic). [HIG: Motion](https://developer.apple.com/design/human-interface-guidelines/motion)
- **When Reduce Motion is on**, reduce automatic and repetitive animation, including zooming, scaling and peripheral motion. Tighten springs to cut bounce, track gestures directly, avoid animating depth changes in z-layers, **replace x/y/z transitions with fades**, and avoid animating into and out of blurs. [HIG: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- **Autoplay:** do not autoplay audio or video without visible controls to start and stop it, and respond to the system's flashing-lights setting for video. [HIG: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- **Let people cancel motion**, and avoid motion on frequent interactions. [HIG: Motion](https://developer.apple.com/design/human-interface-guidelines/motion)

## Core Rules

### 1. Read the setting the right way
- **Imperative, current value:** `AccessibilityInfo.isReduceMotionEnabled()` returns `Promise<boolean>`. **Live updates:** `AccessibilityInfo.addEventListener('reduceMotionChanged', handler)` returns a subscription; call `.remove()` on unmount. [RN: AccessibilityInfo](https://reactnative.dev/docs/accessibilityinfo)
- **Synchronous in render:** Reanimated's `useReducedMotion()` returns a boolean read **when the app started**. Changing the setting does not re-render, so a person who toggles it while your app is open keeps the old value. Use the `AccessibilityInfo` listener (store it in state) for anything that must react live. [Reanimated: useReducedMotion](https://docs.swmansion.com/react-native-reanimated/docs/device/useReducedMotion)
- **iOS-only extra:** `AccessibilityInfo.prefersCrossFadeTransitions()` reports Reduce Motion together with Prefer Cross-Fade Transitions. Use it to choose a crossfade over a slide. [RN: AccessibilityInfo](https://reactnative.dev/docs/accessibilityinfo)
- *Mistake:* reading the value once in a module-level constant, or in a `useEffect` with no `reduceMotionChanged` subscription.

### 2. Reanimated: configure per animation or globally
- The `ReduceMotion` enum has `System`, `Always`, `Never`. `System` disables the animation when the OS setting is on; it is already the default for `withTiming`/`withSpring`/`withDecay`, so plain calls need no extra config. Set `reduceMotion` only to deviate: `Always` to force a skip, or `Never` for essential motion. [Reanimated: Accessibility](https://docs.swmansion.com/react-native-reanimated/docs/guides/accessibility)
- **What "disabled" means:** `withTiming`/`withSpring` jump straight to `toValue`; `withDecay` returns the current value (respecting `clamp`); `withDelay` starts the next animation immediately; `withRepeat` skips infinite/even reversed repeats and otherwise runs once; `withSequence` only starts animations that have reduced motion disabled. A higher-order animation passes its setting to children that were not configured themselves. [Reanimated: Accessibility](https://docs.swmansion.com/react-native-reanimated/docs/guides/accessibility)
- **Layout animations:** `BounceIn.reduceMotion(ReduceMotion.System)`. When on, entering/keyframe/layout animations jump to their end state and **exiting animations and shared transitions are omitted**. [Reanimated: Accessibility](https://docs.swmansion.com/react-native-reanimated/docs/guides/accessibility)
- **Global override:** `<ReducedMotionConfig mode={ReduceMotion.Never} />` applies to the whole app; use it for a deliberate app-wide policy, not as a quick fix. [Reanimated: ReducedMotionConfig](https://docs.swmansion.com/react-native-reanimated/docs/device/ReducedMotionConfig)
- **`ReduceMotion.Never` is for essential motion only** (a progress indicator the person must watch, a gesture-tracked element). Keeping a decorative animation alive with it is a bug.
- *Mistake:* assuming "System" is a finished accessibility story. A spring that snaps to its end value with no other change can make a state change invisible (see rule 3).

### 3. Replace motion, do not just delete it
Snapping to the end state is correct for decoration. When the motion carried meaning (where something went, that something changed), substitute:

| Motion | Reduce Motion replacement |
|---|---|
| Slide/scale/zoom in | Crossfade (`FadeIn`/`FadeOut` with `.reduceMotion(ReduceMotion.Never)`) or instant |
| Bouncy spring | Shorter, critically damped spring, or instant |
| Parallax / tilt / drifting background | Static layout |
| Shared-element flight | Crossfade between screens |
| Looping attention pulse | Static emphasis (color, badge) |
| Progress spinner | Keep it; it is essential feedback |

Fades are the documented alternative to x/y/z transitions. [HIG: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility) The Reanimated docs show the same move: `reduceMotion ? FadeIn.reduceMotion(ReduceMotion.Never) : BounceIn`. [Reanimated: Accessibility](https://docs.swmansion.com/react-native-reanimated/docs/guides/accessibility)

### 4. The things no library handles
- **Legacy `Animated` / `LayoutAnimation` / `Animated.loop`:** no Reduce Motion integration. Gate them with the `AccessibilityInfo` value or migrate to Reanimated.
- **Lottie (`lottie-react-native`):** the library documents `autoPlay`, `loop`, `progress` and `play()/pause()/reset()/resume()` on the ref, and nothing about reduced motion. Set `autoPlay={!reduceMotion}` and `loop={!reduceMotion}`, or render a static frame through `progress={1}` (choose the frame that reads best). [lottie-react-native README](https://github.com/lottie-react-native/lottie-react-native)
- **Video (`expo-video`):** a player only plays when you call `player.play()` (for example inside the `useVideoPlayer` setup callback). Do not call it on mount for decorative or looping video when Reduce Motion is on; show a poster and a play control instead. Autoplay of anything needs visible controls regardless of the setting. `player.loop` makes it repeat forever. [Expo: Video](https://docs.expo.dev/versions/latest/sdk/video/), [HIG: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- **Native-stack transitions, sheets, keyboard, tab switches** are UIKit and adapt to the system setting themselves; system components "might adjust their motion in response to accessibility settings". Do not reimplement them. [HIG: Motion](https://developer.apple.com/design/human-interface-guidelines/motion) Custom `animation` options on native-stack (`slide_from_bottom`, `flip`) are still worth a check on device.
- **Scroll-linked effects** (`useAnimatedScrollHandler` parallax, sticky-header scaling, `interpolate` on `scrollY`): make the mapping constant (`useReducedMotion() ? 0 : factor`) rather than skipping the handler.

### 5. Haptics are not motion
Reduce Motion does not turn haptics off and should not. Haptics are a separate feedback channel that Apple recommends pairing with visual feedback, and they are a good substitute for a removed animation (a selection tick when a card snaps). Keep them purposeful; the system may suppress them in Low Power Mode. [Expo: Haptics](https://docs.expo.dev/versions/latest/sdk/haptics/), [HIG: Playing haptics](https://developer.apple.com/design/human-interface-guidelines/playing-haptics)

### 6. Gestures keep working
Reduce Motion reduces automatic and decorative motion. A finger-tracked drag (see `/sharqiewicz:rules-gestures-mobile`) is direct feedback and stays; what changes is the release: tighter or no bounce, no rubber-band overshoot. `withDecay`/`withSpring` already go to their end value under `ReduceMotion.System`; use `ReduceMotion.Never` on gesture-tracked values only when the element must still follow the finger.

---

**CRITICAL**: State that would be conveyed only by animation must still be visible when the animation is skipped. Check the end frame alone: is the new state obvious?

**IMPORTANT**: Do not add an in-app "reduce animations" toggle. The system setting is the source of truth (see `/sharqiewicz:rules-apple-mobile`).

## How to test
1. **Device:** Settings > Accessibility > Motion > Reduce Motion (and "Prefer Cross-Fade Transitions" beneath it). The app does not need restarting for the listener path; it does for `useReducedMotion`.
2. **Simulator:** open the Settings app inside the simulator and use the same path. <!-- UNVERIFIED: no simctl command for Reduce Motion was found; the Settings-app route is the documented manual path -->
3. Walk every animated screen twice, setting off and on. For each: is meaning lost, is anything still looping or autoplaying, does any transition still slide?
4. Turn the setting on **while the app is open** and check the `reduceMotionChanged` paths update.

## Quick Reference

| Need | API |
|---|---|
| Current value | `AccessibilityInfo.isReduceMotionEnabled()` (Promise) |
| Live changes | `AccessibilityInfo.addEventListener('reduceMotionChanged', cb)` |
| Crossfade preference (iOS) | `AccessibilityInfo.prefersCrossFadeTransitions()` |
| Sync value at startup | `useReducedMotion()` from Reanimated |
| Per animation | `{ reduceMotion: ReduceMotion.System \| Always \| Never }` |
| Layout animation | `Preset.reduceMotion(ReduceMotion.System)` |
| App-wide | `<ReducedMotionConfig mode={...} />` |

**NEVER:**
- Import `motion/react`, `MotionConfig`, `matchMedia('(prefers-reduced-motion)')` or write `@media (prefers-reduced-motion)` in a React Native file.
- Read `useReducedMotion()` and assume it tracks live changes.
- Use `ReduceMotion.Never` on decorative motion to keep it looking good.
- Leave Lottie `autoPlay loop`, looping video, or an `Animated.loop` running when Reduce Motion is on.
- Remove an animation that carried meaning without adding a fade, text or icon change.
- Add your own "reduce animations" switch, or disable haptics because of Reduce Motion.
- Reimplement native-stack, sheet or tab transitions to add a Reduce Motion branch.

## Verify

- [ ] Every explicit `ReduceMotion.Never` (per call, layout preset or `ReducedMotionConfig`) is justified as essential motion
- [ ] Non-Reanimated motion (Animated, Lottie, video, parallax) is gated or migrated
- [ ] A live toggle updates behavior through `reduceMotionChanged`
- [ ] Replacements are crossfades or instant; no slide/zoom/bounce remains
- [ ] No autoplaying video or audio without visible controls
- [ ] End-state-only screenshots still communicate every state change
- [ ] Tested on device with Reduce Motion on, including Prefer Cross-Fade Transitions

Reduce Motion is a request to stop moving things around, not to stop telling people what happened.
