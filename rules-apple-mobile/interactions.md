# Interactions (iOS · React Native)

Gestures, keyboard, haptics, and motion for a native iPhone feel. Format: Apple rule → RN/Expo API → common mistake. Core rule: **`react-native-gesture-handler` (RNGH) + `react-native-reanimated` for anything beyond a tap** — they run on the UI thread and compose with scroll/nav gestures; `Pressable`/`PanResponder` (JS thread) can't drive 1:1 interruptible motion.

## Gestures

- **Standard vocabulary:** tap = activate, swipe = reveal/dismiss/scroll, drag = move, touch-and-hold = reveal more, double-tap/pinch = zoom, edge-swipe = back. **Don't remap standard gestures**; custom gestures only for specialized, frequent tasks, and **never the sole path** to something important.
- **Always give more than one way to act** — a swipe-to-delete-only row breaks VoiceOver/Switch Control; provide a visible edit-mode/button fallback.
- **Indicate when a gesture is unavailable** — a disabled control needs a distinct style, or it reads as frozen.
- → simple tap = `Pressable`. Beyond that = RNGH:
  ```js
  const pan = Gesture.Pan().onUpdate(e => { x.value = startX.value + e.translationX })
                           .onEnd(e => { x.value = withDecay({ velocity: e.velocityX }) });
  <GestureDetector gesture={Gesture.Simultaneous(pinch, rotation)}>…</GestureDetector>
  ```
  Compose with `Gesture.Simultaneous` (both — pinch+rotate), `Gesture.Exclusive` (a, else b — double-tap vs single-tap), `Gesture.Race` (first wins).
- **44×44pt targets** → `hitSlop` (note: it never extends past the parent bounds and can't steal touches from a cramped neighbor — real spacing does).
- **Edge-swipe-back is system-owned** — use native-stack `gestureEnabled`/`fullScreenGestureEnabled`/`gestureResponseDistance`, don't hand-build it. *Mistake:* a custom left-edge `Pan` (drawer/carousel) fighting the navigator's back-swipe — constrain `activeOffsetX`/`failOffsetY` or disable `gestureEnabled` on that screen + give a back button.

## Keyboard

- **Match keyboard to content**, customize the Return key, keep the focused field + action above the keyboard, input accessory only when it adds function.

| Apple concept | `TextInput` prop | Note |
| --- | --- | --- |
| Keyboard type | `keyboardType` | `email-address`/`number-pad`/`decimal-pad`/`url`/`phone-pad` |
| Autofill hint | `textContentType` (iOS) | `oneTimeCode` (SMS strip), `newPassword`/`password` (Keychain), `emailAddress`, `username` |
| Capitalization | `autoCapitalize` | default `sentences` on an email field is a common bug |
| Return semantics | `returnKeyType` + `onSubmitEditing` | set `search` but wire the handler |
| Field advance | `blurOnSubmit` + ref `.focus()` | Return moves focus, not dismiss |
| Accessory bar | `inputAccessoryViewID` + `<InputAccessoryView>` | iOS-only; needs Android fallback |

- **Keyboard avoidance:** core `KeyboardAvoidingView` is flaky (ignores translucent headers, breaks with nested scrolls). Prefer **`react-native-keyboard-controller`** (`KeyboardAwareScrollView` auto-scrolls to the focused field; `KeyboardToolbar`; native-synced avoidance) — needs a dev build.
- `keyboardDismissMode="interactive"` (iOS) = keyboard tracks the drag 1:1 (interruptible motion applied to the keyboard).
- *Mistake:* `keyboardShouldPersistTaps` defaults to `'never'`, so a tap on a button while the keyboard is up just dismisses it (two taps needed) — set `'handled'`.

## Haptics — `expo-haptics`

- **Causality** (fire on the real event — the snap, the toggle flip — not tap-down), **consistency** (never reuse one pattern for opposite outcomes), **harmony** (match the animation + sound), **utility** (short, discrete; "unnoticed but missed when off"). The OS mute setting is enforced beneath `expo-haptics` — no in-app toggle needed.

| Pattern | Call | When |
| --- | --- | --- |
| Selection | `selectionAsync()` | picker tick, segment drag-over |
| Impact (Light/Medium/Heavy/Rigid/Soft) | `impactAsync(ImpactFeedbackStyle.X)` | Medium = button confirm, Heavy = sheet snap, Rigid = boundary/rubber-band max |
| Notification (Success/Warning/Error) | `notificationAsync(NotificationFeedbackType.X)` | submit success, validation warning, failed submit |

- *Mistakes:* firing haptics every frame inside `onUpdate` (fire only at discrete events / gesture end — Apple violation + perf); `impactAsync` for a completion/error (use `notificationAsync`).

## Motion — `react-native-reanimated`

Apple: purposeful only; never the sole channel; motion matches gesture direction (reveal-down → dismiss-down); brief; interruptible — never make people wait through it twice.

- **Interruptibility & direct manipulation:** mutate `useSharedValue` inside `Gesture.Pan()` on the UI thread — inherently grabbable from the current value. **Capture the grab offset:** `onBegin(() => startX.value = x.value)` then `onUpdate(e => x.value = startX.value + e.translationX)` — setting `x = e.translationX` directly snaps to the finger. *Mistake:* legacy `Animated.timing/spring` for gesture UI (bridge-hops, restarts from a stale snapshot on interrupt → visible jump).
- **Velocity handoff / momentum:** `withDecay({ velocity: e.velocityY, deceleration: 0.998, clamp: [0,H], rubberBandEffect: true })` — the built-in projection primitive. *Mistake:* `withSpring`/`withTiming` with a fixed duration for swipe-to-dismiss (ignores release speed).
- **Springs — use the duration-based `withSpring`, which maps to Apple's damping+response almost verbatim:** `dampingRatio` (1.0 critical, <1.0 bouncy) + `duration` (ms). `withSpring(t, { duration: 400, dampingRatio: 1.0 })` for move/reposition; `{ duration: 300, dampingRatio: 0.8 }` for a drawer after a flick. `overshootClamping: true` forces no bounce. *Mistake:* mixing physics params (`stiffness`) with duration params in one config.
- **Reduce Motion — only partly automatic in RN.** `withSpring`/`withTiming`/`withDecay` default to `ReduceMotion.System`, which disables the animation when the setting is on [Reanimated: withTiming](https://docs.swmansion.com/react-native-reanimated/docs/animations/withTiming). Never pass `ReduceMotion.Never` for decorative motion. Core `Animated`, `LayoutAnimation`, Lottie and autoplaying video ignore the setting: branch on `useReducedMotion()` / `AccessibilityInfo.isReduceMotionEnabled()`. When "disabled" is wrong (a slide that explains where content went), swap in a crossfade instead.
- Prefer Reanimated `entering`/`exiting` presets (`FadeIn`, `Layout.springify()`) over core `LayoutAnimation` (no Reduce-Motion integration, manual Android opt-in). Animate `transform`/`opacity` only; don't hop to JS inside `onUpdate` (`runOnJS` in Reanimated 3, `scheduleOnRN` in Reanimated 4), since it brings the latency back.
