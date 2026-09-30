---
name: rules-gestures-mobile
description: "Gesture-driven interaction rules for React Native + Expo on iOS: react-native-gesture-handler (pan, tap, long press, fling, pinch, composition, scroll conflicts), Reanimated physics (withDecay, withSpring with velocity hand-off, rubber-banding), snap points, velocity-based dismissal, bottom sheets (native formSheet detents first), swipe-to-dismiss, interruptibility, haptics at thresholds, edge-swipe-back conflicts, shared element transitions. Every rule = principle + exact API + the common RN mistake. For web, use /gesture-ui. Triggers on: gesture handler, GestureDetector, usePanGesture, Gesture.Pan, swipe to dismiss, bottom sheet, formSheet, sheetAllowedDetents, snap points, withDecay, rubber band, velocity, drag, pinch, long press, fling, simultaneousWith, activeOffsetX, failOffsetY, edge swipe, swipe back, sharedTransitionTag, shared element, interruptible, draggable."
user-invocable: true
---

Rules for building gesture-driven UI in React Native (iOS first) that tracks the finger 1:1, carries the finger's velocity into the release, and never fights the system's own gestures.

## MANDATORY PREPARATION

1. **Read `package.json` for the installed `react-native-gesture-handler` and `react-native-reanimated` versions.** Match the installed version. Gesture Handler 3 uses hooks (`usePanGesture`, `useTapGesture`, ...); Gesture Handler 2 uses the `Gesture.Pan()` builder. They use different callback names and **relations cannot be mixed between the two APIs**. Write in the style the project already uses; mapping table in [recipes.md](recipes.md). [RNGH: Upgrading to 3](https://docs.swmansion.com/react-native-gesture-handler/docs/guides/upgrading-to-3)
2. **Confirm `GestureHandlerRootView` wraps the app** (as close to the root as possible). Gestures are not recognized outside it, and relations only work between gestures under the same root. Gestures inside a React Native `Modal` need their own root view. [RNGH: Getting started](https://docs.swmansion.com/react-native-gesture-handler/docs/fundamentals/getting-started)
3. **Find the navigator.** Native-stack owns edge-swipe-back and the swipe-to-dismiss of modal and sheet presentations. Anything you add must coexist with it. [React Navigation: Native Stack](https://reactnavigation.org/docs/native-stack-navigator/)
4. For HIG basics (gesture vocabulary, haptics, sheets) see `/sharqiewicz:rules-apple-mobile`. For reduced-motion behavior see `/sharqiewicz:rules-reduced-motion-mobile`. To build the animation itself see `/animate-expo`.

---

## Core Principles

### 1. Use the platform gesture before building one
- Screen dismissal, sheets, edge-swipe back, pull-to-refresh and list swipe rows exist natively. Reach for `presentation: 'formSheet'`, native-stack `gestureEnabled`, `RefreshControl`, and `ReanimatedSwipeable` (`react-native-gesture-handler/ReanimatedSwipeable`) first. [RNGH: Reanimated Swipeable](https://docs.swmansion.com/react-native-gesture-handler/docs/components/reanimated_swipeable)
- Custom gestures only for frequent, specialized tasks, and never as the only path to an action: pair a swipe-to-dismiss with a visible close button. [HIG: Gestures](https://developer.apple.com/design/human-interface-guidelines/gestures), [HIG: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- *Mistake:* a hand-built bottom sheet or drawer for something `formSheet` already does.

### 2. Direct manipulation runs on the UI thread
- Drive position from a `useSharedValue` written inside gesture callbacks. Callbacks that are worklets run on the UI thread with no JS round trip. [RNGH: Reanimated integration](https://docs.swmansion.com/react-native-gesture-handler/docs/fundamentals/reanimated-interactions)
- **Capture the grab offset.** Accumulate `e.changeX` / `e.changeY` into the shared value (or save the start value in `onBegin`). Assigning `translationX` directly snaps the element to the finger's origin on the second touch.
- Callbacks that are wrapped in `useCallback`/`useMemo` or declared outside the config are not auto-workletized; add `'worklet'` yourself. Do not call JS functions from `onUpdate`. [Worklets: scheduleOnRN](https://docs.swmansion.com/react-native-worklets/docs/threading/scheduleOnRN/) (Reanimated 3 name: `runOnJS`).
- *Mistake:* `PanResponder` or legacy `Animated` for a draggable. It runs on the JS thread and restarts from a stale value when interrupted.

### 3. Hand the finger's velocity to the release
- On pan release (`onDeactivate`, not `onFinalize`, so cancelled gestures do not fling) pass `e.velocityX` / `e.velocityY` (points per second) into the release animation. [RNGH: Pan](https://docs.swmansion.com/react-native-gesture-handler/docs/gestures/use-pan-gesture)
- **Free-scrolling content:** `withDecay({ velocity, clamp: [min, max] })`. Add `rubberBandEffect: true` to overshoot the clamp and bounce back (requires `clamp`; strength via `rubberBandFactor`). `deceleration` tunes friction. Decay returns the current value at once when Reduce Motion is on. [Reanimated: withDecay](https://docs.swmansion.com/react-native-reanimated/docs/animations/withDecay)
- **Snapping / settling:** `withSpring(target, { velocity })` so the spring continues the finger's motion instead of restarting from rest. Choose either physics (`stiffness` + `damping`) or duration (`duration` + `dampingRatio`); the two groups cannot be mixed. `clamp` is only available in the duration-based form. [Reanimated: withSpring](https://docs.swmansion.com/react-native-reanimated/docs/animations/withSpring)
- *Mistake:* `withTiming` on release. A fixed-duration ease ignores how hard the person flicked, so a fast flick and a slow drag feel identical.

### 4. Edges resist, they do not stop
- Past a boundary, apply diminishing movement (for example `offset * 0.3`, or a square-root falloff) instead of clamping. A hard stop reads as a frozen UI. For momentum after release use `withDecay`'s rubber band; for drag, scale the translation yourself. `Math.max/min` clamping is for values that must never leave range (opacity, progress).
- Release past the edge springs back with `withSpring` and the release velocity.

### 5. Decide dismiss and snap on distance plus velocity
- Dismiss when `|translation| > ~1/3 of the extent` **or** `|velocity|` exceeds a threshold tuned on device (a heuristic, not a documented value; start near 500-800 pt/s). Distance alone makes quick flicks fail; velocity alone makes twitches dismiss.
- For several snap points, project where the motion would end (`position + velocity * k`, small `k` such as 0.1-0.2) and snap to the nearest point to the projection, not to the release position.
- Fade or scale a backdrop with progress (`interpolate(offset, [0, height], [1, 0])`), so the gesture visibly changes the thing it controls.

### 6. Gestures must be interruptible
- Grabbing a moving element must stop the running animation and continue from its current value. In `onBegin` call `cancelAnimation(x)` ([Reanimated: cancelAnimation](https://docs.swmansion.com/react-native-reanimated/docs/core/cancelAnimation/)) and then track from `x.value`. Never gate input with `isAnimating`.
- *Mistake:* disabling the gesture (`enabled: false`) until an animation finishes, or starting a `withTiming` from a captured `useState` value.

### 7. Resolve conflicts explicitly
- **Horizontal pan inside a vertical scroller (or the reverse):** give the pan `activeOffsetX: [-15, 15]` so it only activates after clear horizontal travel, and `failOffsetY: [-10, 10]` so it gives up when the person scrolls. Vertical dismiss over a `ScrollView` needs the opposite, plus the scroll position check (only dismiss when `scrollY <= 0`). [RNGH: Pan config](https://docs.swmansion.com/react-native-gesture-handler/docs/gestures/use-pan-gesture)
- **Same component:** compose with `useSimultaneousGestures`, `useExclusiveGestures` (priority by argument order, e.g. double tap before single tap), or `useCompetingGestures` (first to activate wins). **Different components:** `simultaneousWith`, `requireToFail`, `block` config props. RNGH 2 names: `Gesture.Simultaneous/Exclusive/Race`, `simultaneousWithExternalGesture`, `requireExternalGestureToFail`, `blocksExternalGesture`. [RNGH: Composition](https://docs.swmansion.com/react-native-gesture-handler/docs/composition/overview)
- **Edge-swipe back:** owned by the native-stack. A left-edge pan (drawer, carousel, image pager) loses or fights it. Options: start your pan away from the edge, set `gestureEnabled: false` on that screen and provide a back button, or `fullScreenGestureEnabled` if a full-width back swipe is acceptable. [React Navigation: Native Stack](https://reactnavigation.org/docs/native-stack-navigator/)
- Never attach a pan to the whole screen without `activeOffset*`/`failOffset*`; it will steal scroll and back gestures.

### 8. Sheets: native first
- `presentation: 'formSheet'` with `sheetAllowedDetents: [0.4, 1]` (or `'fitToContents'`), `sheetGrabberVisible`, `sheetInitialDetentIndex`, `sheetLargestUndimmedDetentIndex` (non-modal feel), `sheetExpandsWhenScrolledToEdge`. You inherit the detent physics, dismiss gesture, dimming, keyboard and VoiceOver behavior. [React Navigation: Native Stack](https://reactnavigation.org/docs/native-stack-navigator/), [HIG: Sheets](https://developer.apple.com/design/human-interface-guidelines/sheets)
- Only when native cannot do it (sheet over a non-navigation screen, custom snap behavior, persistent sheet with a map behind) use `@gorhom/bottom-sheet`, which builds on Reanimated and Gesture Handler. <!-- UNVERIFIED: @gorhom/bottom-sheet API and current version compatibility not checked against its docs -->
- Show one sheet at a time, always offer Close/Done. [HIG: Sheets](https://developer.apple.com/design/human-interface-guidelines/sheets)

### 9. Haptics at thresholds, never per frame
- Fire `Haptics.selectionAsync()` when a drag crosses a snap point or threshold, `impactAsync(ImpactFeedbackStyle.Light|Medium)` on a snap or landing, `notificationAsync` for success/warning/error outcomes. Fire once on crossing (track the crossed state in a shared value and call via `scheduleOnRN`/`runOnJS`), not on every `onUpdate`. [Expo: Haptics](https://docs.expo.dev/versions/latest/sdk/haptics/), [HIG: Playing haptics](https://developer.apple.com/design/human-interface-guidelines/playing-haptics)
- Haptics do not play in Low Power Mode or while the camera or dictation is active; never make them the only signal.

### 10. Shared element transitions are experimental
- `sharedTransitionTag` (the same tag on an `Animated.View` on two screens) is documented as experimental, behind a feature flag, and not recommended for production. Known limits: native-stack only, no tab navigator, issues with `transparentModal`, `backgroundColor` not animated in swipe-driven transitions. Default to native-stack's built-in transition, or a cross-fade, until this leaves experimental. [Reanimated: Shared Element Transitions](https://docs.swmansion.com/react-native-reanimated/docs/shared-element-transitions/overview)
- Under Reduce Motion, shared transitions are omitted. [Reanimated: Accessibility](https://docs.swmansion.com/react-native-reanimated/docs/guides/accessibility)

---

**CRITICAL**: A gesture that cannot be done by another route (button, menu, accessibility action) is a defect. Provide a tap alternative for every custom swipe or drag. [HIG: Gestures](https://developer.apple.com/design/human-interface-guidelines/gestures)

**IMPORTANT**: Indicate unavailable gestures. A drag that does nothing with no visual change reads as a frozen app.

## Quick Reference

| Need | API |
|------|-----|
| Drag | `usePanGesture({ onBegin, onUpdate, onDeactivate })` (RNGH 2: `Gesture.Pan().onBegin/onUpdate/onEnd`), `e.changeX/translationX/velocityX` |
| Tap / double tap | `useTapGesture({ numberOfTaps })` |
| Long press | `useLongPressGesture`, or Pan's `activateAfterLongPress` (ms) |
| Flick | `useFlingGesture({ direction: Directions.RIGHT })` |
| Zoom | `usePinchGesture` (`e.scale`, `e.velocity`) |
| Coast after release | `withDecay({ velocity, clamp, rubberBandEffect })` |
| Settle | `withSpring(to, { velocity, stiffness, damping })` |
| Native sheet | native-stack `presentation: 'formSheet'` + `sheetAllowedDetents` |
| Swipe row | `ReanimatedSwipeable` |
| Edge-back conflict | `gestureEnabled`, `fullScreenGestureEnabled`, or move the pan inward |

More code: [recipes.md](recipes.md).

**NEVER:**
- Clamp a drag at an edge with `Math.min/max` when the element is a scroller or sheet; use resistance and a spring back.
- Release with `withTiming` or a fixed-duration ease after a drag; pass the gesture velocity.
- Decide dismissal from distance only, or read `translationX` in `onFinalize` of a cancelled gesture.
- Fire haptics every `onUpdate` frame, or use `impactAsync` for errors (use `notificationAsync`).
- Mix hook-API gestures with `Gesture.*` builder gestures in one relation, or forget `GestureHandlerRootView`.
- Put an unconstrained full-screen pan over a scroll view or over the left edge of a native-stack screen.
- Use web ideas: no `touch-action`, `pointer` events, `cursor: grab`, `:active` styling or CSS `transition` for drag feedback.
- Ship `sharedTransitionTag` to production without the user accepting its experimental status.

## Verify

- [ ] Dragging is on the UI thread (worklet callbacks, shared values); no `runOnJS`/`scheduleOnRN` inside `onUpdate` except at thresholds
- [ ] The grab offset is captured; a second touch does not jump
- [ ] Release uses `withDecay`/`withSpring` with the gesture velocity; edges rubber-band
- [ ] Dismiss and snap use distance plus velocity; threshold tuned on a real device
- [ ] Grabbing mid-animation catches the element without a jump
- [ ] Pans inside scrollers set `activeOffset*`/`failOffset*`; edge-back still works (test on device)
- [ ] Every custom gesture has a button/menu alternative; VoiceOver can reach it
- [ ] Sheets use `formSheet` detents unless a stated reason prevents it
- [ ] Reduce Motion behavior checked (see `/sharqiewicz:rules-reduced-motion-mobile`)

A gesture is finished when it feels like the object is in the person's hand, and the system's own gestures still work around it.
