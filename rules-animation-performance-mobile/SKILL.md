---
name: rules-animation-performance-mobile
description: "Performance rules for React Native and Expo animation on iOS: the JS/UI thread model, Reanimated worklets and shared values, which style props are cheap and which trigger layout, layout-animation cost, lists during motion, images, Hermes, and how to measure with the Perf Monitor, Xcode Instruments and React DevTools on a release build. Use when writing, reviewing or debugging any animation that must hold its frame rate on a device. For web, use /animation-performance. Triggers on: animation performance, janky animation, dropped frames, JS thread, UI thread, worklet, useSharedValue, useAnimatedStyle, useNativeDriver, layout animation, Perf Monitor, Instruments, hitches, release build, FlatList during animation, FlashList, Hermes, 120 fps, runOnJS, scheduleOnRN, re-render during gesture."
user-invocable: true
---

Performance rules for React Native animation on iOS. Each rule names the principle, the exact API, and the mistake people make in RN. Companion skills: `/animate-expo` builds the animation, `/sharqiewicz:rules-apple-mobile` holds HIG basics, `/sharqiewicz:fix-animation-mobile` applies these rules to a bug.

## MANDATORY PREPARATION

1. Find the motion stack in `package.json`: `react-native-reanimated`, `react-native-gesture-handler`, `react-native-worklets`, legacy `Animated`, `LayoutAnimation`. Note each version, because the gesture and threading APIs differ between major versions (see **Version-sensitive APIs**).
2. Check that the New Architecture status and the Hermes engine are what you think they are. Do not assume either.
3. Read [measuring.md](measuring.md) before making any claim about "slow". A claim about frame rate needs a release build and a number.

---

## Quick Reference

| Area | Rule | API |
|---|---|---|
| Measuring | Only a release build on a real device is evidence. [RN: Performance](https://reactnative.dev/docs/performance) | `npx expo run:ios --configuration Release` ([Expo: local builds](https://docs.expo.dev/guides/local-app-development/)) |
| Threads | Animation state lives on the UI thread, React renders on the JS thread. | shared values, worklets |
| Props | Animate transform, opacity, backgroundColor. Avoid width/height/top/left/margin/padding. [Reanimated: Performance](https://docs.swmansion.com/react-native-reanimated/docs/guides/performance/) | `transform: [{ translateX }]` |
| Reads | Never read `sv.value` on the JS thread. | read inside `useAnimatedStyle` or a gesture callback |
| Bridges | Crossing from UI to JS costs latency. Do it on events, not per frame. | `scheduleOnRN` / `runOnJS` |
| Volume | Roughly 500 animated components on iOS, 100 on low-end Android, then reach for Skia. | [Reanimated: Performance](https://docs.swmansion.com/react-native-reanimated/docs/guides/performance/) |
| Images | Do not animate an `Image`'s width or height. Scale it. [RN: Performance](https://reactnative.dev/docs/performance) | `transform: [{ scale }]` |

---

**CRITICAL**: Per-frame animation state lives in shared values on the UI thread. Never `setState` or read `sv.value` from a per-frame callback or render, and never sign off performance from a dev build or simulator.

## Core Principles

### 1. Know the two frame rates

RN has a JS frame rate (React renders, your handlers, `setState`) and a UI frame rate (native views, native-driven animation, scrolling). The two are independent, so an animation can stay smooth while the JS thread is stalled, but only if nothing on the path needs JS. [RN: Performance](https://reactnative.dev/docs/performance)

In the New Architecture the renderer still does React's render phase on the JS thread and only the UI thread can touch host views, with some high-priority events rendering synchronously on the UI thread. [RN: Threading model](https://reactnative.dev/architecture/threading-model) The practical rule does not change: keep per-frame work off the JS thread.

**Mistake**: concluding "JS is fast enough" because the simulator looked fine. A dev build adds warnings and error checks on the JS thread. [RN: Performance](https://reactnative.dev/docs/performance)

### 2. Drive animation from shared values on the UI thread

A worklet is a short function that can run on the UI thread, marked with the `"worklet"` directive or auto-detected by the Babel plugin. A shared value is the state that both threads can see, read and written through `.value`. [Reanimated: Glossary](https://docs.swmansion.com/react-native-reanimated/docs/fundamentals/glossary/)

- Gesture callbacks are workletized automatically when Reanimated is installed. [RNGH: Callbacks & events](https://docs.swmansion.com/react-native-gesture-handler/docs/fundamentals/callbacks-events)
- Write `x.value = withSpring(target)` inside the callback. Do not `setState` the position and re-render.

**Mistake**: `const [x, setX] = useState(0)` updated from `onUpdate`. That forces a JS render on every touch event.

### 3. Do not read shared values in render or effects

Reading `.value` on the JS thread blocks until the UI thread answers. It is allowed only inside worklets. [Reanimated: Performance](https://docs.swmansion.com/react-native-reanimated/docs/guides/performance/)

```tsx
const style = useAnimatedStyle(() => ({ opacity: sv.value }));   // ok, worklet
useEffect(() => { console.log(sv.value); }, []);                  // blocks the JS thread
```

`useAnimatedStyle` must not mutate shared values or the style object it returns, and its result goes only on `Animated.*` components. Keep static styles in `StyleSheet` and combine them in an array. [Reanimated: useAnimatedStyle](https://docs.swmansion.com/react-native-reanimated/docs/core/useAnimatedStyle/)

### 4. Animate props that do not need layout

`transform`, `opacity` and `backgroundColor` are cheap. `top`/`left`, `width`/`height`, `margin` and `padding` force layout every frame. [Reanimated: Performance](https://docs.swmansion.com/react-native-reanimated/docs/guides/performance/)

- Transforms do not affect layout, so neighbours will not move. Reserve space with padding or margin if overlap matters. [RN: Transforms](https://reactnative.dev/docs/transforms)
- A reveal that really must change size (an accordion) is the one legitimate layout animation. Keep it short, keep the subtree small, and keep it off lists.
- With the legacy `Animated` API, `useNativeDriver: true` covers transform and opacity but not layout props, and one value cannot mix native and JS drivers. [RN: Animations](https://reactnative.dev/docs/animations)
- An animated counter should be a shared value feeding an animated `TextInput`, not a re-rendered `Text`. [Reanimated: Performance](https://docs.swmansion.com/react-native-reanimated/docs/guides/performance/)

**Mistake**: animating `height` from 0 to auto-measured on every row of a list.

### 5. Keep the UI-to-JS bridge off the hot path

`runOnJS` schedules a non-worklet function from the UI thread and is asynchronous. `scheduleOnRN` from `react-native-worklets` is its replacement, and the docs mark `runOnJS` deprecated. Both are for events such as "animation finished" or "crossed a threshold". [Worklets: scheduleOnRN](https://docs.swmansion.com/react-native-worklets/docs/threading/scheduleOnRN) and [Worklets: runOnJS](https://docs.swmansion.com/react-native-worklets/docs/threading/runOnJS)

**Mistake**: calling it in `onUpdate` so a React component can "follow" the finger. Follow with a shared value instead.

### 6. Budget layout animations

Reanimated layout transitions (`LinearTransition`, `FadingTransition` and others) and entering/exiting presets replace layout changes with animation. [Reanimated: Layout transitions](https://docs.swmansion.com/react-native-reanimated/docs/layout-animations/layout-transitions/) They are convenient, and they still cost a layout pass per frame while they run.

- Hoist builders out of the component or wrap them in `useMemo`. [Reanimated: Entering/exiting](https://docs.swmansion.com/react-native-reanimated/docs/layout-animations/entering-exiting-animations/)
- On the New Architecture do not overwrite `nativeID`, which is used to configure entering animations. [Reanimated: Entering/exiting](https://docs.swmansion.com/react-native-reanimated/docs/layout-animations/entering-exiting-animations/)
- Entering animations on every row of a long feed are a cost you pay on every mount.

### 7. Lists and images during motion

- FlatList: give fixed-height items `getItemLayout`, memoize rows and `renderItem`, tune `windowSize`, `maxToRenderPerBatch`, `initialNumToRender`. [RN: Optimizing FlatList](https://reactnative.dev/docs/optimizing-flatlist-configuration)
- FlashList mounted while an animation runs can briefly place items wrongly (a React Native root cause). Mount it before the motion starts. [Reanimated: Performance](https://docs.swmansion.com/react-native-reanimated/docs/guides/performance/)
- With legacy `Animated`, a long or looping native-driven animation can block `VirtualizedList` rendering unless it passes `isInteraction: false`. [RN: Animations](https://reactnative.dev/docs/animations)
- Network and data-URI images need explicit `width` and `height`. [RN: Image](https://reactnative.dev/docs/image) Use thumbnails in lists.
- Defer heavy one-off work with `requestAnimationFrame` or `requestIdleCallback` so it does not land on the frame of a press. [RN: Performance](https://reactnative.dev/docs/performance)

### 8. Engine and build settings

- Hermes is the default engine and precompiles JS to bytecode at build time. [RN: Hermes](https://reactnative.dev/docs/hermes) Confirm with `!!global.HermesInternal`.
- Remove `console.log` from release bundles, including logger middleware. [RN: Performance](https://reactnative.dev/docs/performance)
- 120 fps on iPhone needs `CADisableMinimumFrameDurationOnPhone` in `Info.plist` (already in the template for newer RN). [Reanimated: Performance](https://docs.swmansion.com/react-native-reanimated/docs/guides/performance/)
- New Architecture regressions have documented feature-flag mitigations (scroll jitter, FPS during scroll, many simultaneous animations). Read the flag table there before writing a workaround. Note that the synchronous-update flags affect touch detection on animated transforms, which is why RNGH `Pressable` is suggested. [Reanimated: Performance](https://docs.swmansion.com/react-native-reanimated/docs/guides/performance/)

---

## Version-sensitive APIs

Match the installed version's docs. Do not mix generations in one file.

| Concern | Older form | Newer form |
|---|---|---|
| UI to JS call | `runOnJS(fn)(args)` | `scheduleOnRN(fn, ...args)` from `react-native-worklets` |
| Gesture definition | `Gesture.Pan().onUpdate(...)` | `usePanGesture({ onUpdate, onDeactivate })` |
| Gesture end callbacks | `onEnd` / `onFinalize` | `onDeactivate` (runs only if activated), `onFinalize` (always after `onBegin`) |

[RNGH: Pan gesture](https://docs.swmansion.com/react-native-gesture-handler/docs/gestures/use-pan-gesture) and [RNGH: Callbacks](https://docs.swmansion.com/react-native-gesture-handler/docs/fundamentals/callbacks-events)

---

## Common Mistakes

| Symptom | Likely cause | Fix |
|---|---|---|
| Smooth in dev-client on simulator, choppy on phone | Testing the wrong build or device | Release build, real device |
| Drag lags when a list below re-renders | State set per touch event | Shared value plus `useAnimatedStyle` |
| Jank only at animation start | Mounting a heavy subtree | Mount first, then animate; memoize |
| Image "pumps" while scaling up | Animating `width`/`height` | `transform: [{ scale }]` |
| Flicker on animated header in scroll | Known New Architecture issue | See flag table in Reanimated performance guide |

## Review Checklist

- [ ] Measured on a release build on a real device
- [ ] Every per-frame value is a shared value
- [ ] No `.value` read outside a worklet
- [ ] Only transform, opacity, colour animated (or layout animation justified)
- [ ] No UI-to-JS call inside a per-frame callback
- [ ] Layout-animation builders hoisted or memoized
- [ ] List rows memoized, no entering animation on a primary feed

**NEVER:**
- Benchmark or sign off a dev build
- Read a shared value in render, an effect or a JS event handler
- `setState` from a gesture's per-frame callback
- Animate `width`/`height` of an `Image`
- Invent a flag or `Info.plist` key: copy it from the docs
- Mix `runOnJS` and `scheduleOnRN` generations, or legacy and new gesture APIs, in one gesture

## Verify

- [ ] Build a release configuration and run it on a real device, not the simulator.
- [ ] Watch JS and UI fps in the Perf Monitor while the animation runs: UI stays at the display rate, and JS dips do not change the motion.
- [ ] Scrub the animation in Xcode Instruments (Animation Hitches) and confirm no hitches around start, interruption and end.
- [ ] Use React DevTools Profiler during a drag: the gesture owner does not re-render per touch event.
- [ ] Repeat with a long list mounted and a slow device if one is available.

Remember: smooth motion means the thread that runs it never waits on the thread that does not.
