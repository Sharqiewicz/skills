---
name: fix-animation-mobile
description: "Diagnose why a React Native or Expo animation feels off, janky or unresponsive on iOS, then fix it with the smallest diff and verify on a release build. Separates frame-rate problems (JS thread vs UI thread) from feel problems (spring config, easing, hand-off, interruption, anchor). For web, use /debug-animation. Triggers on: animation janky, animation laggy, dropped frames, stutter, feels off, feels slow, feels floaty, spring too bouncy, gesture not smooth, drag lags, animation cut off, can't interrupt, wrong pivot, transformOrigin, useNativeDriver warning, fix animation mobile, debug reanimated."
user-invocable: true
disable-model-invocation: true
argument-hint: [file, component or description of the problem]
---

Find out why one specific React Native animation is wrong, change as little as possible to fix it, and prove the fix on a release build on a device.

## MANDATORY PREPARATION

1. Read the animation code and its gesture or trigger in full. Do not guess from the component name.
2. Read `/sharqiewicz:rules-animation-performance-mobile` (threading, cheap props, measuring) and skim `/animate-expo` for the project's preferred spring and gesture patterns.
3. Check versions in `package.json` for Reanimated, `react-native-worklets`, and Gesture Handler. The API for UI-to-JS calls and gesture callbacks differs by version, so edit in the style the project already uses.
4. Ask the user only what the code cannot tell you: which device, which screen, what "off" means (stutters, feels slow, feels wrong, cannot be interrupted).

---

## Step 1: Reproduce honestly

**CRITICAL**: Dev mode is slow. Do not diagnose frame drops from a debug build or a simulator. [RN: Performance](https://reactnative.dev/docs/performance)

1. Build release on a real device: `npx expo run:ios --configuration Release --device`. [Expo: Local app development](https://docs.expo.dev/guides/local-app-development/)
2. Reproduce the issue. If it only happens in dev, say so and stop: it is not a product bug.
3. Record the baseline before touching code (see Step 2). Steps for measuring live in `measuring.md` inside `/sharqiewicz:rules-animation-performance-mobile`.

If you cannot run a device, say that the diagnosis below is from reading code and cannot be confirmed.

## Step 2: Classify the problem

Decide which bucket before searching for causes.

| Bucket | What the user says | How to tell |
|---|---|---|
| Frame drops, JS thread | Stutters while something else loads or re-renders | Perf Monitor JS fps falls during the animation |
| Frame drops, UI thread | Stutters even when JS is idle | UI fps falls, Instruments shows layout or commit work |
| Feel | Smooth but wrong: slow, floaty, abrupt, bouncy, snaps back | Frame rate is fine in both monitors |
| Interaction | Cannot be interrupted, jumps under the finger, fights scroll | Reproduce by grabbing it mid-flight |

The Perf Monitor (dev menu, **Show Perf Monitor**) reports JS and UI frame rates separately. [RN: Performance](https://reactnative.dev/docs/performance) Use it to classify, then confirm in Xcode Instruments on the release build. [RN: Profiling](https://reactnative.dev/docs/profiling)

## Step 3: Find the cause

Work the matching list. Every hit needs `file:line` evidence before you change anything.

### Frame-drop causes

| Cause to grep for | Why it hurts | Fix direction |
|---|---|---|
| `Animated.timing` or `Animated.spring` without `useNativeDriver: true` | The animation ticks on the JS thread. [RN: Animations](https://reactnative.dev/docs/animations) | Move to Reanimated shared values, or set the flag if only transform or opacity change |
| Animated `width`, `height`, `top`, `left`, `margin`, `padding` | Layout every frame. [Reanimated: Performance](https://docs.swmansion.com/react-native-reanimated/docs/guides/performance/) | Animate `transform` and `opacity`, or scale a container |
| `setState` inside a gesture callback or `requestAnimationFrame` loop | A React render per frame | Write to a shared value instead |
| Heavy parent re-render while dragging | JS thread busy, handlers delayed | Memoize the subtree, move state away from the gesture owner |
| `runOnJS` or `scheduleOnRN` in `onUpdate` | A thread hop per event. [Worklets: scheduleOnRN](https://docs.swmansion.com/react-native-worklets/docs/threading/scheduleOnRN) | Call on begin, threshold or end only |
| `sv.value` read in render or `useEffect` | Blocks the JS thread on the UI thread. [Reanimated: Performance](https://docs.swmansion.com/react-native-reanimated/docs/guides/performance/) | Read inside `useAnimatedStyle` or a worklet |
| Animated `Image` `width`/`height` | Costly re-crop. [RN: Performance](https://reactnative.dev/docs/performance) | `transform: [{ scale }]` |
| Hundreds of animated views, long lists with layout or entering animations | Volume. [Reanimated: Performance](https://docs.swmansion.com/react-native-reanimated/docs/guides/performance/) | Cut the count, virtualize, or use Skia |
| `console.log` per frame, logger middleware | JS thread cost in a bundled app. [RN: Performance](https://reactnative.dev/docs/performance) | Remove |

### Feel causes

| Symptom | Likely cause | Fix direction |
|---|---|---|
| Slow and heavy | `withTiming` with a long `duration`, or default spring `duration` | Shorten, or use a stiffer spring |
| Mechanical, robotic | `Easing.linear`, or a bezier copied from a web CSS string | Spring for interactive motion, `Easing.out(...)` for exits. Use `Easing.bezier(x1, y1, x2, y2)`, not a CSS string. [Reanimated: withTiming](https://docs.swmansion.com/react-native-reanimated/docs/animations/withTiming/) |
| Bounces when it should not | `dampingRatio` below 1 on a non-gesture change | Critically damped is `dampingRatio: 1`, the default. [Reanimated: withSpring](https://docs.swmansion.com/react-native-reanimated/docs/animations/withSpring/) |
| Release feels dead, or snaps to a fixed speed | Gesture end ignores `event.velocityX` or `velocityY` | Pass velocity into `withSpring({ velocity })` or `withDecay({ velocity })`. [Reanimated: Handling gestures](https://docs.swmansion.com/react-native-reanimated/docs/fundamentals/handling-gestures/) |
| Element jumps to the finger on touch | No captured start offset | Store `x.value` in `onBegin`, then add the translation in `onUpdate` |
| Cannot grab it mid-animation | Gesture disabled while animating, or `withTiming` restarted from a stale value | Keep the gesture enabled. Assigning a new animation to the shared value cancels the old one, and the callback receives `finished: false`. [Reanimated: withSpring](https://docs.swmansion.com/react-native-reanimated/docs/animations/withSpring/) |
| Scales or rotates around the wrong point | Default origin is centre. [RN: Transforms](https://reactnative.dev/docs/transforms) | Set the `transformOrigin` style, such as `'left top'` or `'50% 100%'`. Remove old translate-scale-translate workarounds |
| Spring config ignored | `stiffness` or `damping` mixed with `duration` or `dampingRatio` | Duration-based values override physics values. Pick one set. [Reanimated: withSpring](https://docs.swmansion.com/react-native-reanimated/docs/animations/withSpring/) |
| Fights vertical scroll | Pan activates too early | `activeOffsetX` and `failOffsetY` on the pan. [RNGH: Pan gesture](https://docs.swmansion.com/react-native-gesture-handler/docs/gestures/use-pan-gesture) |
| Haptic fires at the wrong moment | Triggered on tap-down or per frame | Fire once on the causal event. See `/sharqiewicz:rules-apple-mobile` |

Reduce Motion: if the fix changes or adds motion, check it still degrades. The `with*` functions default to `ReduceMotion.System`. [Reanimated: withTiming](https://docs.swmansion.com/react-native-reanimated/docs/animations/withTiming/)

## Step 4: Fix with the smallest diff

1. Pick the single most likely cause. Change only that.
2. Keep the project's existing config vocabulary (spring values, helpers). Do not introduce a parallel set.
3. Do not refactor, rename or restyle unrelated code.
4. Re-measure. If the symptom remains, revert that change and try the next cause. Do not stack speculative fixes.

**IMPORTANT**: If the honest fix is "remove this animation" (frequent interaction, or the system already does it), say so and propose that. See `/sharqiewicz:find-animations-mobile`.

**NEVER:**
- Diagnose or sign off on a dev build or a simulator
- Wrap a JS-thread animation in `setTimeout` or `InteractionManager` and call it fixed
- Change several things in one pass and report the gain as if one caused it
- Raise or lower a duration before confirming the problem is feel, not frame rate
- Copy a web `cubic-bezier(...)` string, `ease-out` keyword or `prefers-reduced-motion` media query into RN
- Add `runOnJS` or `scheduleOnRN` to "fix" a warning inside a per-frame callback
- Commit, push or open a PR. Show the diff and stop

## Verify

- [ ] Reproduced and re-checked on a release build on a real device
- [ ] The cause is backed by `file:line` evidence, not a hunch
- [ ] Before and after numbers (UI fps, JS fps, or a described interaction test) are stated
- [ ] The animation can still be grabbed and interrupted mid-flight
- [ ] Reduce Motion still degrades correctly
- [ ] Diff touches only the files the cause lives in
- [ ] Report lists anything you could not test

Remember: name the cause before you touch the code, and change one thing at a time.
