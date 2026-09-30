---
name: rules-polish-mobile
description: "The small details that make a React Native + Expo app feel native on iOS: Pressable press states and spring scale, concentric corner radius, borderCurve continuous, boxShadow vs shadow props, hairline borders, haptics, image placeholders and transitions, skeletons vs spinners, optimistic UI, no layout shift, native components over look-alikes. For web, use /better-ui and /make-interfaces-feel-better. Triggers on: polish, feels native, feels cheap, press state, Pressable, TouchableOpacity, scale on press, corner radius, borderCurve, continuous corners, boxShadow, shadow, hairlineWidth, expo-haptics, expo-image, placeholder, skeleton, spinner, optimistic update, layout shift, native feel, UI details."
user-invocable: true
---

The small details that make a React Native + Expo app feel native on iOS: every touch answers instantly, shapes and shadows match the system, and nothing jumps while content loads.

## MANDATORY PREPARATION

1. Find the shared `Button`/`Card`/`Avatar`/`Image` primitives. Polish lives there, not on each screen.
2. Check the React Native architecture and version in `package.json`: `boxShadow` needs the New Architecture.
3. For HIG component choice (tab bars, sheets, pickers, alerts) read `/sharqiewicz:rules-apple-mobile`. For building the animations below use `/animate-expo`. To find more motion opportunities use `/sharqiewicz:find-animations-mobile`.

---

## Quick Reference

| Detail | RN / Expo API | Rule of thumb |
| --- | --- | --- |
| Press feedback | `Pressable` `style={({pressed}) => ...}`, `onPressIn` | Change something visible on press-in, within one frame |
| Spring scale | Reanimated `withSpring` on `transform: [{scale}]` | Subtle (about 0.96-0.98), spring back on release |
| Corner shape | `borderCurve: 'continuous'` | iOS smooth corner; combine with `borderRadius` |
| Nested radius | inner = outer - padding | Never the same radius for parent and child |
| Shadow | `boxShadow` (New Arch) or `shadow*` props | One system per codebase |
| Divider | `StyleSheet.hairlineWidth` | Thin, pixel-aligned |
| Haptic | `expo-haptics` | One short haptic per discrete event |
| Remote image | `expo-image` `placeholder`, `transition` | Reserve the size; fade in |
| Loading | skeleton for layout, spinner for unknown waits | Show something right away |

**CRITICAL**: Every custom touchable answers on touch-down. Drive a visible press state from `Pressable`'s `pressed` or `onPressIn`, not from `onPress`, because a control with no press state feels broken.

## Core Principles

### 1. Answer the touch at once

HIG: "Always include a press state for a custom button", since without one it feels unresponsive ([HIG: Buttons](https://developer.apple.com/design/human-interface-guidelines/buttons)).

- `Pressable` exposes `pressed` in `style` and in `children` functions, and fires `onPressIn` on touch-down, before `onPress` on release ([RN: Pressable](https://reactnative.dev/docs/pressable)). Drive visuals from `pressed` or `onPressIn`, not from `onPress`.
- Opacity-only dimming (the `TouchableOpacity` default) is fine for text links and toolbar items. On cards and filled buttons it looks web-like and unfinished. Use a slight scale-down plus a background shade instead.
- Scale on press with Reanimated: a shared value, `withSpring` in `onPressIn`, back to 1 in `onPressOut`. Keep it on the UI thread with `useAnimatedStyle`. `withSpring` already follows Reduce Motion by default; see `/sharqiewicz:rules-reduced-motion-mobile` for where that default does not reach. Full recipe: `/animate-expo`.
<!-- UNVERIFIED: the 0.96-0.98 scale range is a house convention, not from a primary doc -->
- **There is no hover on iPhone.** `onHoverIn`/`onHoverOut` only matter with a pointer (iPad). Never gate feedback on hover.
- `android_ripple` is Android only. Do not expect it on iOS.
- Set `delayLongPress` (default 500ms) only when you have a real long-press action. `unstable_pressDelay` delays `onPressIn`, which is the opposite of what you want for feedback.

### 2. Shapes: concentric radius and continuous corners

- A card with padding `p` and outer radius `R` holds children with radius `R - p` (never below 0). Equal radii on nested shapes look pinched. Apple builds this into the system design language ([WWDC25: Get to know the new design system](https://developer.apple.com/videos/play/wwdc2025/356/)). Compute it from tokens, do not hand-tune per view.
- `borderCurve: 'continuous'` gives iOS's smooth corner (iOS 13+); the default is `'circular'` ([RN: View Style Props](https://reactnative.dev/docs/view-style-props)). Set it inside the shared `Card`/`Button`/`Avatar`, not one-off.
- `borderRadius` needs `overflow: 'hidden'` for children (images) to be clipped. But `overflow: 'hidden'` also clips shadows: put the shadow on an outer view and the clip on an inner one.
- Capsule buttons: radius at least half the height.

### 3. Shadows, borders and surfaces

- React Native has three shadow systems: `boxShadow` (spec-like, supports `inset` and spread, iOS and Android, New Architecture only), the native `shadowColor`/`shadowOffset`/`shadowOpacity`/`shadowRadius` (iOS), and Android `elevation` ([RN: Shadow props](https://reactnative.dev/docs/shadow-props)). Web `box-shadow` strings work only in `boxShadow`. Pick one family and wrap it in a token.
- Keep shadows soft and low-opacity. iOS uses depth sparingly; prefer a hairline border and a surface color step in dark mode, where shadows disappear.
- Dividers and card outlines: `borderWidth: StyleSheet.hairlineWidth`, which rounds to a whole pixel for a crisp line ([RN: StyleSheet](https://reactnative.dev/docs/stylesheet)). A `1` px border renders heavy on 3x screens. Check on a real device, since a downscaled simulator may hide it.
- Semantic colors via `PlatformColor` so borders and surfaces adapt to dark mode and Increase Contrast. See `/sharqiewicz:rules-color-mobile`.

### 4. Haptics as feedback, not decoration

Per [HIG: Playing haptics](https://developer.apple.com/design/human-interface-guidelines/playing-haptics): use them for cause and effect, complement what the screen shows, keep them short, do not overuse them, and let people turn them off.

| Situation | expo-haptics call |
| --- | --- |
| Value changing while scrubbing or picking (picker tick, segment change) | `Haptics.selectionAsync()` |
| A view snaps into place, a light object bumps | `Haptics.impactAsync(ImpactFeedbackStyle.Light / Medium / Heavy / Rigid / Soft)` matched to weight |
| Outcome of a task: saved, payment done | `Haptics.notificationAsync(NotificationFeedbackType.Success)` |
| Recoverable problem | `NotificationFeedbackType.Warning` |
| Failure | `NotificationFeedbackType.Error` |

- Standard controls (`Switch`, pickers, native tabs) already play system haptics. Adding another doubles it.
- Do not reuse a pattern for a different meaning: success on a failure path confuses people.
- Calls are silent when Low Power Mode or the system setting is off, or during camera/dictation ([Expo: Haptics](https://docs.expo.dev/versions/latest/sdk/haptics/)). Nothing may depend on them. Store an in-app "haptics" preference only if you add custom haptics.

### 5. Images, placeholders, skeletons, spinners

- Use `expo-image` (`Image`) rather than the core `Image` for remote content: it has `placeholder` (BlurHash or ThumbHash), `transition` (ms number, cross-dissolve), `cachePolicy` (default `disk`), `priority`, and `Image.prefetch(urls)` ([Expo: Image](https://docs.expo.dev/versions/latest/sdk/image/)).
- Set `placeholderContentFit` equal to `contentFit` to avoid a flicker when the real image arrives. Inside `FlashList` set `recyclingKey` so a recycled cell does not show the previous picture.
- Reserve space: give the image a fixed `width`/`height` or `aspectRatio` so the list does not jump when it loads.
- HIG on loading: show something as soon as possible, use placeholders that get replaced by content, and let people do other things while they wait ([HIG: Loading](https://developer.apple.com/design/human-interface-guidelines/loading)). Skeleton when the final layout is known (lists, cards, profile). Native `ActivityIndicator` for short, shapeless waits (button submit, pull-to-refresh via `RefreshControl`). A determinate progress bar when you know the duration.
- Skeleton shimmer is motion: slow it down or make it static under Reduce Motion.

### 6. Optimistic UI and no layout shift

- Apply the result of a tap (like, toggle, send, reorder) locally in the same frame, then reconcile with the server. On failure roll back and say so (toast plus `announceForAccessibility`). React's `useOptimistic` reverts to real state when the action ends ([React: useOptimistic](https://react.dev/reference/react/useOptimistic)); its React Native support is not stated in those docs, so a TanStack Query or store-level optimistic update is the safer path.
- Prefetch the next screen's data on press-in or when a row becomes visible.
- Layout shift sources on mobile: images without size, text that swaps between loading and loaded heights, buttons that change width when a spinner replaces the label, content inserted above the scroll position, and late safe-area values. Give each a fixed box or `minHeight`.

### 7. Native beats custom look-alikes

Reach for the platform control first (HIG covers each in `/sharqiewicz:rules-apple-mobile`): native-stack header and large title, native tabs, `Alert.alert`/`ActionSheetIOS`, `Switch`, system pickers, `formSheet` presentation, SF Symbols through `expo-symbols`. A custom version needs to reproduce gestures, haptics, Dynamic Type, VoiceOver and dark mode, and usually does not.

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| Web `box-shadow` string in `shadowColor` style | Use `boxShadow`, or the `shadow*` props |
| Shadow vanishes with `overflow: 'hidden'` | Split into outer shadow view and inner clip view |
| Same radius on card and inner image | Inner radius = outer minus padding |
| `activeOpacity` 0.2 on a filled button | Scale + shade feedback |
| Haptic on every scroll tick or tap | Only on meaningful discrete events |
| Spinner over a blank screen | Skeleton or cached content |
| `1` px divider | `StyleSheet.hairlineWidth` |

**NEVER:**
- Leave a custom `Pressable` without a visible pressed state.
- Fire feedback from `onPress` when `onPressIn` is available and appropriate.
- Hard-code hover styles or rely on `onHoverIn` on iPhone.
- Stack a custom haptic on a control that already plays one.
- Let remote images load with no reserved size.
- Animate press scale without honoring Reduce Motion.
- Rebuild a native control for looks alone.

## Verify

- [ ] Tap every custom control on a device: a visible change arrives on touch-down.
- [ ] Nested rounded shapes share a center; corners use `continuous` curve.
- [ ] Shadows and hairlines look right in light and dark, on a 3x device.
- [ ] Throttle the network: placeholders show, images fade in, nothing shifts.
- [ ] Haptics fire once per event, match the HIG meaning, and the app works with them off.
- [ ] Failed optimistic action rolls back and is announced.

Remember: polish is the sum of a hundred moments where the app answered faster and more quietly than people expected.
