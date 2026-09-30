---
name: rules-accessibility-mobile
description: "Accessibility rules for React Native + Expo on iOS: VoiceOver semantics (accessible, role, label, hint, state, value, actions), announcements, hiding and modal behavior, grouping, focus order, 44pt touch targets, and the system settings to honor (Bold Text, Reduce Transparency, Increase Contrast). For web, use /better-accessibility. Triggers on: accessibility, a11y, VoiceOver, screen reader, accessibilityLabel, accessibilityRole, accessibilityState, accessibilityHint, accessibilityActions, announceForAccessibility, hitSlop, touch target, 44pt, Increase Contrast, Bold Text, Reduce Transparency, AccessibilityInfo, Accessibility Inspector, aria-label in React Native."
user-invocable: true
---

Accessibility rules for React Native + Expo on iOS: give every control a role, a name and a state that VoiceOver can speak, keep touch targets large, and honor the system settings instead of adding your own.

## MANDATORY PREPARATION

1. Find the shared primitives (button, row, icon button, input, modal wrapper). Fix semantics there once, not per screen.
2. Check for the existing props in use (`accessibilityLabel`, `role`, `aria-*`). Keep one style across the codebase.
3. For text size, contrast and color, go to `/sharqiewicz:rules-typography-mobile` and `/sharqiewicz:rules-color-mobile`. Broader HIG rules live in `/sharqiewicz:rules-apple-mobile`.

---

## Quick Reference

| Need | RN API | Note |
| --- | --- | --- |
| Make a view one focusable element | `accessible` | Touchables and `Pressable` are accessible by default. A parent with `accessible` makes its children part of one element. [RN: Accessibility](https://reactnative.dev/docs/accessibility) |
| What it is | `accessibilityRole` or `role` | `button`, `link`, `header`, `image`, `switch`, `tab`, `adjustable`, `search`, ... `role` also accepts `heading`, `img`, `slider`, `list`, `listitem`. |
| What it is called | `accessibilityLabel` (or `aria-label`) | Short, no role word ("Delete", not "Delete button"). Nested `Text` is concatenated when you omit it. |
| What happens | `accessibilityHint` | Only when the result is not obvious. Users can turn hints off on iOS. |
| Current state | `accessibilityState` `{disabled, selected, checked, busy, expanded}` | `checked` accepts `'mixed'`. |
| Current value | `accessibilityValue` `{min, max, now, text}` | `text` overrides the numbers. Needs `min` and `max` when `now` is set. |
| Extra actions | `accessibilityActions` + `onAccessibilityAction` | Standard names: `activate`, `increment`, `decrement`, `magicTap`, `escape`. |
| Hide from VoiceOver | `accessibilityElementsHidden` (iOS) or `aria-hidden` | Hides the view and its children. |
| Trap focus in a modal | `accessibilityViewIsModal` (iOS) | VoiceOver ignores siblings. |
| Announce a change | `AccessibilityInfo.announceForAccessibility` | Live regions are Android-only. |
| Move focus | `AccessibilityInfo.sendAccessibilityEvent(ref, 'focus')` | Target needs `accessible`. [RN: AccessibilityInfo](https://reactnative.dev/docs/accessibilityinfo) |

## Core Principles

### 1. Every interactive element has role, name and state

**CRITICAL**: An icon-only `Pressable` with no label is read as "button" with no name, or not at all. Set `role="button"` and an `accessibilityLabel`, then express state through `accessibilityState` (`selected`, `checked`, `expanded`, `disabled`, `busy`), never by changing the label text ("Selected, Favorite").

- Use `role="switch"`/`checkbox` with `checked`, `role="tab"` with `selected`, `role="header"` (or `heading`) on section titles so VoiceOver's heading rotor works.
- A slider-like custom control needs `role="adjustable"` (or `slider`), an `accessibilityValue`, and `accessibilityActions` with `increment` and `decrement`. Swipe up and down must change the value.
- Do not stack `accessibilityHint` on every control. A hint describes the result ("Opens your cart"), not the gesture ("Double tap to open").

### 2. Group what belongs together, split what does not

A list row with title, subtitle and a trailing button should read as one row plus one separate action. Put `accessible` on the row container, give it a label that concatenates the facts in reading order, and expose the trailing action through `accessibilityActions` so it is not lost inside the group. Do not wrap two real controls in one `accessible` parent: VoiceOver can no longer reach the inner ones.

### 3. Custom gestures need an action alternative

Swipe-to-delete, long-press menus and drag handles are invisible to VoiceOver. Mirror each one with `accessibilityActions` (`{name: 'delete', label: 'Delete'}`) handled in `onAccessibilityAction` via `event.nativeEvent.actionName`. Apple asks for an alternative to every gesture ([HIG: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)).

### 4. Announce what changed, then manage focus

- Toasts, form errors and async results: call `AccessibilityInfo.announceForAccessibility(message)`. On iOS use `announceForAccessibilityWithOptions(message, {queue: true})` when it must not cut off current speech.
- `accessibilityLiveRegion` (`polite`, `assertive`) and `importantForAccessibility` are **Android-only**. They do nothing on iOS. Do not rely on them for VoiceOver.
- After navigation inside one screen (a step change, an opened panel), send focus to the new heading: `AccessibilityInfo.sendAccessibilityEvent(ref, 'focus')`. `setAccessibilityFocus` is deprecated.
- Default focus order is layout order. To change it, prefer fixing the view order. `experimental_accessibilityOrder` exists but is experimental.

### 5. Modals and hidden content

A custom overlay (not a native-stack modal) leaves the screen behind it reachable. Set `accessibilityViewIsModal` on the overlay container, or `accessibilityElementsHidden` on the content underneath. Use `aria-hidden` on decorative images and duplicated icons. Native-stack modals and `formSheet` handle this for you, which is one more reason to use them.

### 6. Touch targets

The hit region is at least 44x44pt (28pt is the floor), with about 12pt around bezeled controls and about 24pt around unbezeled ones ([HIG: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility), [HIG: Buttons](https://developer.apple.com/design/human-interface-guidelines/buttons)).

- Small icon: keep the visual size and add `hitSlop={{top: 12, bottom: 12, left: 12, right: 12}}` (a number also works). [RN: Pressable](https://reactnative.dev/docs/pressable)
- Slop never extends past the parent bounds, and a sibling's z-order wins on overlap. Close icon buttons in a tight row need real `minWidth`/`minHeight: 44`, not slop.
- `pressRetentionOffset` (default 20 / 20 / 20 / 30pt) only decides how far a finger can drift before the press cancels. It does not enlarge the target.

### 7. Honor system settings; do not add toggles

| Setting | Query | Event |
| --- | --- | --- |
| Reduce Motion | `AccessibilityInfo.isReduceMotionEnabled()` | `reduceMotionChanged` |
| Bold Text (iOS) | `isBoldTextEnabled()` | `boldTextChanged` |
| Reduce Transparency (iOS) | `isReduceTransparencyEnabled()` | `reduceTransparencyChanged` |
| Increase Contrast (iOS) | `isDarkerSystemColorsEnabled()` | none listed |
| Invert Colors (iOS) | `isInvertColorsEnabled()` | `invertColorsChanged` |
| Screen reader | `isScreenReaderEnabled()` | `screenReaderChanged` |

Subscribe with `AccessibilityInfo.addEventListener(name, handler)` and remove the subscription on cleanup. Translucent blur should fall back to an opaque surface under Reduce Transparency. Low-contrast brand colors need a higher-contrast variant under Increase Contrast ([HIG: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)). Prefer `PlatformColor` semantic colors, which adapt on their own. Mark photos that must not invert with `accessibilityIgnoresInvertColors`. Motion: see `/animate-expo` (`ReduceMotion.System`).

Dynamic Type: leave `allowFontScaling` on and test at the largest accessibility sizes. Details in `/sharqiewicz:rules-typography-mobile`.

### 8. Web accessibility idioms that do not exist here

- **No `tabindex`, no focus ring, no `:focus-visible`.** Focus is VoiceOver's cursor. Keyboard focus only matters with an external keyboard.
- **ARIA is not the model.** React Native maps native accessibility (UIAccessibility on iOS). The docs list `aria-label`, `aria-hidden`, `aria-checked`, `aria-disabled`, `aria-busy`, `aria-expanded`, `aria-selected`, `aria-valuemin/max/now/text`, `aria-labelledby` and `role` as aliases for the `accessibility*` props. No other ARIA attribute exists, and `aria-labelledby` and `aria-live` are Android-only. Pick one family per codebase.
- **No semantic landmarks or `<label for>`.** Name a field with `accessibilityLabel` on the `TextInput` itself. A placeholder alone is not a label, since it disappears on typing ([HIG: Text fields](https://developer.apple.com/design/human-interface-guidelines/text-fields)).

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| `TouchableOpacity` around an icon, no label | `Pressable` + `role="button"` + `accessibilityLabel` |
| Label "Close button" | Label "Close"; the role supplies "button" |
| Selected state only a color change | Add `accessibilityState={{selected}}` and a non-color cue |
| Toast shown, nothing announced | `announceForAccessibility` |
| `accessibilityLiveRegion` for VoiceOver | Android only; announce instead |
| `accessible` on a screen-sized container | Children become unreachable; group rows, not screens |
| Text inside a chip clipped at large sizes | Let it grow; `minHeight`, not fixed `height` |

**NEVER:**
- Ship an icon-only control without a label.
- Convey state or errors by color, motion or haptic alone.
- Use `accessibilityHint` to repeat the label.
- Put a swipe or long-press gesture in without an `accessibilityActions` equivalent.
- Wrap independent controls in one `accessible` parent.
- Disable font scaling to keep a layout intact.
- Add an in-app toggle for something the OS already exposes (Bold Text, Reduce Motion, contrast).
- Trust the simulator alone for VoiceOver behavior.

## Verify

- [ ] Turn VoiceOver on, on a real device (Settings > Accessibility > VoiceOver), and swipe through each screen: every stop has a name, a role and the right state. [RN: Accessibility](https://reactnative.dev/docs/accessibility) recommends device testing.
- [ ] Run Xcode's Accessibility Inspector against the simulator or device to read labels, roles and hit areas.
- [ ] Custom gestures work through the VoiceOver actions rotor.
- [ ] Dynamic Type at the largest accessibility size: nothing clipped or overlapping.
- [ ] Increase Contrast, Bold Text, Reduce Transparency, Reduce Motion and Invert Colors each checked once.
- [ ] Every tap target measures 44x44pt, visually or through `hitSlop`.

Remember: if the screen only works when you can see it and use a fingertip precisely, it is not finished.
