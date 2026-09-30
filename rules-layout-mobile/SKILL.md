---
name: rules-layout-mobile
description: "Layout rules for React Native + Expo screens on iPhone and iPad: safe areas, keyboard avoidance, RN flexbox defaults, a point-based spacing scale, grouping and density on small screens, scroll content with large titles, and adapting to rotation and iPad. Every rule = principle + the exact RN/Expo API + the common RN mistake. For web, use /better-layout. Triggers on: layout, spacing, padding, margin, gap, safe area, SafeAreaView, useSafeAreaInsets, SafeAreaProvider, notch, Dynamic Island, home indicator, KeyboardAvoidingView, keyboard covers input, automaticallyAdjustKeyboardInsets, keyboardVerticalOffset, flexbox, flexDirection, contentInsetAdjustmentBehavior, large title, headerLargeTitleEnabled, useWindowDimensions, landscape, iPad, split view, rotation, small screen, screen layout, responsive."
user-invocable: true
---

Layout rules for React Native + Expo screens: where content may sit, how it moves with the keyboard, and how it adapts to the window. Units are points (1 RN unit = 1pt on iOS).

## MANDATORY PREPARATION

1. Read the screen and its navigator setup first (native-stack vs custom header, tab bar, modal or sheet). The navigator decides which insets you must add yourself.
2. Check `package.json` for `react-native-safe-area-context`, `react-native-keyboard-controller` and the Expo SDK. Use what is installed.
3. Find the root: is there a `SafeAreaProvider` (Expo Router and React Navigation already include one)? [Expo: Safe areas](https://docs.expo.dev/develop/user-interface/safe-areas/)
4. For HIG basics (44pt targets, reachability, Dynamic Island) see `/sharqiewicz:rules-apple-mobile`. For text sizing see `/sharqiewicz:rules-typography-mobile`.

---

## Quick Reference

| Situation | Use | Not |
|---|---|---|
| Content must avoid notch, home indicator | `SafeAreaView` or `useSafeAreaInsets` from `react-native-safe-area-context` | RN core `SafeAreaView` (deprecated), hardcoded `paddingTop: 47` |
| Screen inside native-stack with a header | Nothing extra at the top; the header handles it | Adding `insets.top` under a visible header |
| Form with inputs | `KeyboardAvoidingView` with explicit `behavior`, or `ScrollView` + `automaticallyAdjustKeyboardInsets` | `behavior` left unset |
| Scroll view under a large title | `contentInsetAdjustmentBehavior="automatic"` | Manual `paddingTop` for the header height |
| Gaps between siblings | `gap`, `rowGap`, `columnGap` | Margin on every child |
| Wide window, rotation, iPad | `useWindowDimensions()` | `@media`, a one-time `Dimensions.get` |

---

**CRITICAL**: Let the background fill the screen and pad only the content with the safe-area insets (`SafeAreaView` or `useSafeAreaInsets`). Never hardcode status-bar, notch or home-indicator numbers, and never pad the keyboard as if it were a safe area.

## Core Principles

### 1. Insets belong to content, backgrounds go edge to edge

Let the background colour fill the screen and pad only the content. Consume insets with `react-native-safe-area-context`: the library calls `SafeAreaView` the preferred way (native, no flicker) and warns the hook "can cause some layout flicker in certain cases". [safe-area-context: Usage](https://appandflow.github.io/react-native-safe-area-context/usage) The hook suits cases where you need a number, such as a bottom bar that sits `insets.bottom` above the edge. RN's own `SafeAreaView` is deprecated, iOS-only, and ignores custom padding. [RN: SafeAreaView](https://reactnative.dev/docs/safeareaview)

- `<SafeAreaView edges={['bottom']}>` when a navigator header already covers the top. Only pad the edges nothing else covers.
- Insets are relative to the nearest `SafeAreaProvider`, so one provider at the root is enough, not one per screen.
- Read the numbers from `useSafeAreaInsets()`. They change with device, orientation and status bar. Never hardcode a Dynamic Island or home-indicator height.
- **Common mistake:** wrapping a screen that already sits under a native-stack header in `SafeAreaView` with all edges, which doubles the top gap.

### 2. The keyboard is not part of the safe area

Insets exclude the software keyboard. [safe-area-context: Usage](https://appandflow.github.io/react-native-safe-area-context/usage) Handle it separately:

- `KeyboardAvoidingView`: set `behavior` on both platforms, the docs recommend it because iOS and Android react differently. Expo's guidance: `'padding'` on iOS, `undefined` on Android. [RN: KeyboardAvoidingView](https://reactnative.dev/docs/keyboardavoidingview), [Expo: Keyboard handling](https://docs.expo.dev/guides/keyboard-handling/)
- Under a header or inside a modal, set `keyboardVerticalOffset` to the distance between the screen top and the view (for example the header height). Default is 0.
- In a `ScrollView`, iOS has `automaticallyAdjustKeyboardInsets` (default `false`) to grow `contentInset` with the keyboard. [RN: ScrollView](https://reactnative.dev/docs/scrollview)
- Pair forms with `keyboardDismissMode="interactive"` (iOS) and `keyboardShouldPersistTaps="handled"`, otherwise the first tap on a button only closes the keyboard.
- Long forms with many inputs: Expo points to `react-native-keyboard-controller` (`KeyboardAwareScrollView`, `KeyboardToolbar`); it needs a development build, not Expo Go.
- **Common mistake:** `KeyboardAvoidingView` without `behavior`, or a sticky bottom button that ignores the keyboard so it floats above the keys or hides behind them.

### 3. RN flexbox is CSS flexbox with different defaults

`flexDirection` defaults to `column`, `alignContent` to `flex-start`, `flexShrink` to `0`, and `flex` takes one number only. [RN: Flexbox](https://reactnative.dev/docs/flexbox)

- Overflowing row children do not shrink: add `flexShrink: 1` (or `flex: 1`) on the text container, or long strings push siblings off screen.
- Sizes are points or `'%'`. No `rem`, `em`, `vh`, `calc()`, `grid`. `display` only accepts `flex`, `none`, `contents`. [RN: Layout props](https://reactnative.dev/docs/layout-props)
- `boxSizing` defaults to `border-box`. `gap`, `rowGap`, `columnGap` work, in points only.
- Use `start`/`end`, `marginStart`/`paddingEnd` so the layout mirrors in RTL locales (`direction` defaults to inherit from the locale).
- Text must sit in `<Text>`; a bare string in `<View>` throws.

### 4. Spacing: a small point scale, applied by relationship

Pick one scale and keep to it. A common choice is 4, 8, 12, 16, 24, 32. <!-- house recommendation, not a quoted HIG value -->

- Closer means related: 4 to 8 inside a label/value pair, 12 to 16 between rows in a group, 24 to 32 between groups.
- Standard screen side margin of 16; read it from one constant, not from each screen.
- Snapping to pixel is automatic: RN rounds to the pixel grid relative to the root. Use `PixelRatio.roundToNearestPixel` only for hairlines you compute yourself. [RN: PixelRatio](https://reactnative.dev/docs/pixelratio)
- Interactive targets: see `/sharqiewicz:rules-accessibility-mobile` for the 44pt minimum and `hitSlop`.

### 5. Density on small screens

- One primary task per screen. Move secondary actions into a menu, sheet or a second screen rather than shrinking type and spacing.
- Group with whitespace and grouped-list backgrounds before you reach for borders. Use `StyleSheet.hairlineWidth` for separators.
- Keep the primary action in the bottom third, above the home indicator (`insets.bottom`).
- Test the smallest supported iPhone at the largest text size (see `/sharqiewicz:rules-typography-mobile`); if a row breaks, stack it vertically instead of clipping.

### 6. Scroll content under native headers

With native-stack, set `headerLargeTitleEnabled: true`, wrap the screen in a scrollable (`ScrollView`, `FlatList`) and add `contentInsetAdjustmentBehavior="automatic"` so the title collapses and content starts below the bar. `headerSearchBarOptions` needs the same prop. With `headerTransparent: true` the header floats and you must offset content yourself. [React Navigation: Native Stack](https://reactnavigation.org/docs/native-stack-navigator) The RN default for the prop is `'never'`. [RN: ScrollView](https://reactnative.dev/docs/scrollview)

- **Common mistake:** the tutorial-era option name `headerLargeTitle`; the current option is `headerLargeTitleEnabled`. Check the installed version's types.
- **Common mistake:** a screen whose content is not a scrollable at all; the docs require a `ScrollView` or `FlatList` for the title to collapse.

### 7. Adapt to the window, not the device

`useWindowDimensions()` returns `width`, `height`, `scale`, `fontScale` and re-renders on rotation, split view and font-scale changes. [RN: useWindowDimensions](https://reactnative.dev/docs/usewindowdimensions)

- Switch layout on width breakpoints (for example two columns from about 700pt), because iPad split view and Stage Manager change width without rotating.
- Do not read `Dimensions.get('window')` once at module scope; it goes stale.
- `flexWrap` plus `gap` and a computed column count beats media-query thinking. There is no `@media`.
- Lock orientation only when the product needs it (`orientation` in the Expo config) [Expo: App config](https://docs.expo.dev/versions/latest/config/app/). `ios.requireFullScreen: true` opts out of Slide Over and Split View on iPad, which also removes the width changes below.; otherwise test landscape, where vertical insets shrink and left/right insets appear.

---

## Decision Flowchart

**Which inset tool?**
- Whole screen container, need padding on chosen edges → `SafeAreaView` with `edges`.
- Need the number (floating button, custom bar, animation) → `useSafeAreaInsets()`.
- Inside native-stack or tabs with visible bars → usually nothing for those edges.
- Scrolling content that should pass behind a bar → `contentInsetAdjustmentBehavior="automatic"`, not padding.

**Input hidden by keyboard?**
- Fixed layout, one or two inputs → `KeyboardAvoidingView`.
- Scrolling form → `ScrollView` + `automaticallyAdjustKeyboardInsets`.
- Many inputs, toolbar, animated sync → `react-native-keyboard-controller` (dev build).

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| `paddingTop: 44` for the notch | `useSafeAreaInsets().top` |
| Row text pushes icon off screen | `flexShrink: 1` on the text wrapper |
| `width: '100vw'`, `@media (min-width)` | `useWindowDimensions`, `width: '100%'` |
| Keyboard covers the submit button | `behavior` + offset, or keyboard-controller |
| Margin on every child | `gap` on the parent |
| Safe-area padding only on top | Check bottom and, in landscape, left/right |

---

## Review Checklist

- [ ] No hardcoded notch, status bar or home-indicator numbers
- [ ] Insets from `react-native-safe-area-context`, not RN core `SafeAreaView`
- [ ] No doubled inset under a native header
- [ ] Every screen with a `TextInput` handles the keyboard, with `behavior` set explicitly
- [ ] Large-title screens use `contentInsetAdjustmentBehavior="automatic"`
- [ ] Layout breakpoints use `useWindowDimensions`; landscape and iPad split view checked
- [ ] Spacing values come from one scale; side margins from one constant
- [ ] Row layouts survive a long string and the largest text size

**NEVER:**
- Use `SafeAreaView` from `react-native` in new code.
- Put padding styles on RN's core `SafeAreaView` and expect them to apply.
- Leave `KeyboardAvoidingView` without `behavior`.
- Use web units or queries (`rem`, `vh`, `calc`, `@media`, `env(safe-area-inset-*)`).
- Wrap every screen in one extra full-edge `SafeAreaView` inside a native-stack.
- Shrink touch targets below 44pt to fit more on the screen.

## Verify

- Run on the smallest and the largest iPhone simulator, in landscape, and on an iPad at half-width.
- Focus the lowest input with the keyboard open: it and its submit button stay visible.
- Scroll a large-title screen: the title collapses, nothing sits under the bar.

Layout on mobile is inset-aware, keyboard-aware and window-aware; let the platform measure, and keep your own numbers to one scale.
