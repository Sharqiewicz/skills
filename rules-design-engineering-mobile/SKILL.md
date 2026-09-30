---
name: rules-design-engineering-mobile
description: "Craft principles for React Native + Expo engineers building iOS apps: perceived performance, forms and keyboards (TextInput autofill, keyboardType, returnKeyType, submitBehavior, focus chaining, inputAccessoryView), touch instead of mouse, thumb reach, interruptible interactions, sensible defaults, native-stack sheets and modals, FlatList vs FlashList, and what not to build custom. For web, use /emil-design-eng and /emil-design-engineering. Triggers on: design engineering, craft, perceived performance, TextInput, textContentType, autoComplete, keyboardType, returnKeyType, submitBehavior, focus chaining, InputAccessoryView, keyboard handling, thumb reach, bottom sheet, formSheet, native-stack modal, FlatList, FlashList, list performance, native feel."
user-invocable: true
---

Craft principles for React Native + Expo engineers on iOS: make the app respond before it finishes, make forms effortless, design for a thumb instead of a cursor, and use the system's parts rather than rebuilding them.

## MANDATORY PREPARATION

1. Read the screen's real flow: what the person taps first, what waits on the network, where the keyboard appears.
2. Find the form, list and modal components the app already shares. Change defaults there.
3. Do not repeat neighbors. HIG basics: `/sharqiewicz:rules-apple-mobile`. Motion: `/animate-expo` and `/sharqiewicz:find-animations-mobile`. Press states, shadows, haptics, images: `/sharqiewicz:rules-polish-mobile`. VoiceOver and touch targets: `/sharqiewicz:rules-accessibility-mobile`.

---

## Quick Reference

| Topic | Use |
| --- | --- |
| Instant feedback | `Pressable` `onPressIn`, local state first |
| Autofill | `textContentType` (iOS) / `autoComplete` |
| Keyboard | `keyboardType`, `inputMode`, `returnKeyType` / `enterKeyHint` |
| Next field | `submitBehavior="submit"` + `onSubmitEditing` + `ref.focus()` |
| Toolbar above keyboard | `InputAccessoryView` + `inputAccessoryViewID` |
| Scroll + keyboard | `keyboardShouldPersistTaps`, `keyboardDismissMode`, `automaticallyAdjustKeyboardInsets` |
| Sheet / modal | native-stack `presentation` |
| Long lists | `FlatList`, or `FlashList` for large or heterogeneous lists |

**IMPORTANT**: Never lock input while a transition runs. Interactions must be interruptible (tap again, swipe back, change your mind), so drive motion with retargeting springs and keep the UI responsive on the UI thread.

## Core Principles

### 1. Perceived performance beats measured performance

- Respond on touch-down. `onPressIn` fires before `onPress`, so highlight, scale or start a transition there. Navigate on `onPress` so cancelled touches do nothing ([RN: Pressable](https://reactnative.dev/docs/pressable)).
- Update local state first, then sync. Roll back visibly on failure (see `/sharqiewicz:rules-polish-mobile`).
- Prefetch on intent: on press-in of a row, when it becomes visible, or at screen mount for the obvious next step. Images: `Image.prefetch` in `expo-image` ([Expo: Image](https://docs.expo.dev/versions/latest/sdk/image/)).
- Show something immediately and fill in the rest. HIG: if people wait before anything appears, they assume a problem ([HIG: Loading](https://developer.apple.com/design/human-interface-guidelines/loading)).
- Keep heavy work off the JS thread during a transition: see `/sharqiewicz:rules-animation-performance-mobile` for the thread model.

### 2. Forms: remove work from the person

Every `TextInput` states what it is, so the keyboard and iOS AutoFill can help ([RN: TextInput](https://reactnative.dev/docs/textinput)).

| Field | Props |
| --- | --- |
| Email | `keyboardType="email-address"`, `autoCapitalize="none"`, `autoCorrect={false}`, `textContentType="emailAddress"`, `autoComplete="email"` |
| Existing password | `secureTextEntry`, `textContentType="password"`, `autoComplete="password"` |
| New password | `secureTextEntry`, `textContentType="newPassword"`, `autoComplete="new-password"`, optional `passwordRules` |
| One-time code | `textContentType="oneTimeCode"`, `autoComplete="one-time-code"`, `keyboardType="number-pad"` |
| Phone | `keyboardType="phone-pad"`, `textContentType="telephoneNumber"` |
| Amount | `keyboardType="decimal-pad"` (or `inputMode="decimal"`) |
| Search | `returnKeyType="search"`, `clearButtonMode="while-editing"` |

- `autoComplete` wins over `textContentType` when both are set, and `inputMode` wins over `keyboardType`. Set one family or keep them consistent.
- **Known pitfall:** `onSubmitEditing` does not fire on iOS with `keyboardType="phone-pad"` (the keyboard has no return key). Use a visible Continue button or an `InputAccessoryView`.
- Placeholder is a hint, not a label: keep a visible label above the field, because the placeholder vanishes when typing ([HIG: Text fields](https://developer.apple.com/design/human-interface-guidelines/text-fields)). Use the keyboard type that matches the content, and validate on blur for email, before leaving the field for usernames and passwords (same page).
- Match field width to the expected text, stack fields vertically, keep consistent widths.

**Focus chaining.** Return key "Next" moves to the next field; the last field says "Done" or "Go" and submits.

- Non-last fields: `returnKeyType="next"`, `submitBehavior="submit"` so the keyboard does not dismiss between fields, and `onSubmitEditing={() => nextRef.current?.focus()}`.
- Last field: `returnKeyType="done"`, the default single-line `submitBehavior` (`blurAndSubmit`) dismisses the keyboard, then run the submit handler.
- `blurOnSubmit` is deprecated; use `submitBehavior`.
- `enterKeyHint` is the web-style alternative to `returnKeyType`.

**Accessory toolbar.** `InputAccessoryView` (iOS only) adds a bar above the keyboard (Next/Previous/Done): give it a `nativeID` and pass the same value to `inputAccessoryViewID`. Limits from the docs: no multiline `TextInput`, and it cannot be used with a bottom tab bar ([RN: InputAccessoryView](https://reactnative.dev/docs/inputaccessoryview)).

**Keyboard and scroll.** Put forms in a `ScrollView`. `keyboardShouldPersistTaps="handled"` lets buttons inside receive taps while the keyboard is up (the default `never` swallows the first tap). `keyboardDismissMode="interactive"` (iOS) lets a drag dismiss the keyboard. `automaticallyAdjustKeyboardInsets` (iOS) moves content above the keyboard ([RN: ScrollView](https://reactnative.dev/docs/scrollview)). For everything else see keyboard handling in `/sharqiewicz:rules-apple-mobile`.

### 3. Design for touch, not a cursor

- No hover, no right-click, no precise pointer. Every state must be reachable by tap, long-press or swipe, and each needs a visible affordance. `onHoverIn` is for iPad pointers only.
- Fingers are fat and cover what they touch: targets at least 44x44pt with spacing ([HIG: Buttons](https://developer.apple.com/design/human-interface-guidelines/buttons)); show feedback outside the touch point.
- Thumb reach: the bottom third of a phone is easy, the top corners are hard. Put the primary action near the bottom, inside the safe area (see `/sharqiewicz:rules-layout-mobile`). Destructive or rare actions go out of the thumb's natural sweep.
<!-- UNVERIFIED: thumb-zone guidance is ergonomic convention; no primary doc fetched for it -->
- Gestures are not discoverable. Every gesture-only action also needs a button or menu path (`/sharqiewicz:rules-accessibility-mobile`).
- Keyboard covers half the screen: design forms so the focused field, its error and the primary button are visible while typing.

### 4. Interruptible interactions

People tap again, swipe back and change their mind mid-animation. Do not lock input while a transition runs.

- Drive motion with springs (`withSpring`) that retarget from current position and velocity, rather than fixed-duration sequences that must finish ([Reanimated: withSpring](https://docs.swmansion.com/react-native-reanimated/docs/animations/withSpring/)). Details: `/animate-expo`.
- Make cancellable presses: `Pressable` cancels `onPress` when the finger drifts past `pressRetentionOffset`.
- Gestures should follow the finger 1:1 and hand off velocity on release (gesture-handler + Reanimated).
- Async work needs cancellation: ignore or abort stale responses when the person navigates away or types again.

### 5. Defaults that feel right

- Keyboard type, capitalization, autofill, return key: set per field, never leave `default`.
- Dismiss sheets by swipe, tap outside and a visible button. Focus the first field only when typing is the point (`autoFocus`).
- Keep `allowFontScaling` on; choose sensible `maxFontSizeMultiplier` only for tight UI chrome.
- Restore scroll position and form input when returning. Preserve drafts.
- Destructive actions confirm with `Alert.alert` (destructive style) or offer undo, not a silent delete.

### 6. Sheets and modals: presentation, not custom views

Use `@react-navigation/native-stack` (real `UINavigationController`) and set `presentation` per screen ([React Navigation: Native Stack](https://reactnavigation.org/docs/native-stack-navigator)).

| Need | Option |
| --- | --- |
| Standard modal with nested stack | `presentation: 'modal'` |
| Bottom sheet with detents | `presentation: 'formSheet'` + `sheetAllowedDetents` (`'fitToContents'` or fractions like `[0.5, 1]`) |
| Grabber, corner radius | `sheetGrabberVisible`, `sheetCornerRadius` |
| Keep content behind interactive | `sheetLargestUndimmedDetentIndex` |
| Scroll expands the sheet | `sheetExpandsWhenScrolledToEdge` (iOS, default true) |
| Must not be swiped away | `fullScreenModal`, or `gestureEnabled: false` |
| Overlay that shows previous screen | `transparentModal` |

You get native gestures, dimming, VoiceOver focus, safe area and swipe-to-dismiss for free. A JS-drawn bottom sheet reimplements all of it, usually badly. Sheet HIG: [Sheets](https://developer.apple.com/design/human-interface-guidelines/sheets); more in `/sharqiewicz:rules-apple-mobile`.

### 7. Lists

- `FlatList` fits most screens. Follow its tuning rules: stable `keyExtractor`, `React.memo` items, a memoized `renderItem` (`useCallback`), `getItemLayout` when rows have one fixed height, sensible `initialNumToRender`/`windowSize` ([RN: Optimizing FlatList](https://reactnative.dev/docs/optimizing-flatlist-configuration)).
- `FlashList` (`@shopify/flash-list`) recycles cells to avoid blank areas on big feeds. Rules: `keyExtractor`, `getItemType` for mixed row kinds, no `key` props inside rows, state in rows can go stale under recycling (use `useRecyclingState`), memoize props ([FlashList docs](https://shopify.github.io/flash-list/docs/usage)). Set `recyclingKey` on `expo-image` inside rows.
- Never nest a vertical `FlatList` in a vertical `ScrollView` (it loses virtualization). Use `ListHeaderComponent`/`ListFooterComponent`.
- Pull-to-refresh with `RefreshControl`; swipe actions and row patterns in `/sharqiewicz:rules-apple-mobile`.

### 8. What not to build custom

Native stack and headers, tab bar, sheets, alerts, pickers, switches, segmented control, context menus, pull-to-refresh, keyboard avoiding, date pickers, share sheet, SF Symbols. If a design asks for a custom version, first ask which native one is closest and what is lost. Only go custom when you will also own gestures, haptics, VoiceOver, Dynamic Type and dark mode.

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| Navigation on `onPressIn` | Feedback on press-in, navigate on `onPress` |
| `blurOnSubmit` | `submitBehavior` |
| Every field `returnKeyType="done"` | `next` until the last field |
| Form in a plain `View` | `ScrollView` + keyboard props |
| Tapping a button while keyboard is open needs two taps | `keyboardShouldPersistTaps="handled"` |
| Custom `Modal` with hand-drawn sheet | native-stack `formSheet` |
| `FlashList` row with `useState` | `useRecyclingState` or lift state |

**NEVER:**
- Leave `keyboardType`, `textContentType`/`autoComplete` and `autoCapitalize` unset on credential, email, phone or code fields.
- Rely on `onSubmitEditing` with `phone-pad`.
- Lock input during an animation or transition.
- Require hover, right-click or a gesture with no button alternative.
- Put the main action in the top corner of a tall phone layout.
- Nest same-direction virtualized lists in a `ScrollView`.
- Hand-build a bottom sheet, tab bar or alert when a native one exists.

## Verify

- [ ] Fill each form with only the keyboard and AutoFill on a device: correct keyboard, Next moves on, Done submits.
- [ ] Mash taps and swipe back mid-transition: no stuck or double state.
- [ ] Offline or slow network: instant local response, visible rollback.
- [ ] Primary actions reachable with one thumb; keyboard never hides the focused field or submit.
- [ ] Sheets dismiss by swipe, scrim tap and button; VoiceOver reads them correctly.
- [ ] Scroll a 1000-row list fast on a release build: no blank flashes.

Remember: craft is deciding, field by field and moment by moment, that the person should never wait, re-type or hunt.
