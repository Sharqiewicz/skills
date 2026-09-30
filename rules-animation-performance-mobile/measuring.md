# Measuring animation performance on iOS

## Get an honest build

1. Turn development mode off before profiling. [RN: Profiling](https://reactnative.dev/docs/profiling)
2. Build a release configuration locally and install it on a connected device:
   `npx expo run:ios --configuration Release --device`. The build is unsigned, so it is for local testing only. [Expo: Local app development](https://docs.expo.dev/guides/local-app-development/) and [Expo CLI](https://docs.expo.dev/more/expo-cli/)
3. Use the same device model your users hold. A flagship hides problems. An older iPhone exposes them.

## Perf Monitor (quick, dev build)

The dev menu's **Show Perf Monitor** shows the JS and UI frame rates. [RN: Performance](https://reactnative.dev/docs/performance)

- UI fps drops: native work (layout, too many views, blur, big images). Suspect animated layout props and view count.
- JS fps drops but UI stays high: expected if the animation is on the UI thread. It becomes a problem when the animation depends on JS (state per frame, `runOnJS`, JS-driven `Animated`).
- Both drop: look for layout-triggering animation plus heavy re-renders.
- <!-- UNVERIFIED: whether the dev menu and Perf Monitor are reachable in a Release configuration. Treat it as a dev-build tool and confirm release behaviour with Instruments. -->

## Xcode Instruments (release build, the real verdict)

Instruments is the primary iOS profiling tool. [RN: Profiling](https://reactnative.dev/docs/profiling)

- Hitches: a hitch is a frame that arrives late during scrolling, dragging or animation. Apple's Organizer metric treats at most 10 ms/s of pause as good, up to 25 as a warning, up to 50 as critical, and beyond that as needing immediate attention. [Apple: Understanding hitches](https://developer.apple.com/documentation/xcode/understanding-hitches-in-your-app)
- Commit hitches come from main-thread delay before the frame is handed to the render server, render hitches from the render phase. [Apple: Understanding hitches](https://developer.apple.com/documentation/xcode/understanding-hitches-in-your-app)
- <!-- UNVERIFIED: exact Instruments template names ("Animation Hitches", "Time Profiler", "Core Animation"). Check the template chooser in the installed Xcode. -->
- Use Time Profiler to find what the main thread does in the slow frames, and look for layout and commit work during the animation.

## React DevTools Profiler (JS side)

React Native DevTools includes the React Profiler (flame graph of commits) and a Performance panel that records JS execution. "Highlight updates when components render" exposes re-renders. [RN: React Native DevTools](https://reactnative.dev/docs/react-devtools) Use it to catch re-renders during a gesture. It measures the JS thread, not native frame pacing.

## Report format

State: device model, build configuration, what was measured (UI fps, JS fps, hitch ms/s), before and after. "Feels smoother" is not a result.
