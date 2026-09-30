---
name: rules-apple-mobile
description: "Apple's Human Interface Guidelines for iPhone/iOS, translated for React Native + Expo. Use when building OR reviewing a native iOS app in React Native: navigation (React Navigation native-stack, large titles, edge-swipe back), tab bars, sheets & detents, alerts & action sheets, forms/TextInput, lists (FlatList/FlashList, swipe-to-delete, pull-to-refresh), pickers, segmented controls, context menus, search bars, safe areas & Dynamic Island, Dynamic Type, dark mode, materials/blur, SF Symbols, accessibility (VoiceOver, 44pt targets), gestures (gesture-handler), motion (reanimated springs), haptics (expo-haptics), keyboard handling, permissions, push notifications, and App Store review requirements (Sign in with Apple, account deletion, ATT, Apple Pay). Every rule = Apple HIG rule + the exact React Native/Expo API + the common RN mistake. Triggers on: React Native, Expo, iOS app, iPhone app, native mobile, React Navigation, native-stack, bottom tabs, safe area, useSafeAreaInsets, Dynamic Type, allowFontScaling, useColorScheme, PlatformColor, DynamicColorIOS, SF Symbols, expo-symbols, expo-blur, BlurView, sheet detents, formSheet, ActionSheetIOS, Alert.alert, TextInput, keyboardType, textContentType, FlatList, FlashList, RefreshControl, swipe to delete, gesture-handler, reanimated, withSpring, withDecay, reduce motion, expo-haptics, KeyboardAvoidingView, expo-notifications, expo-apple-authentication, Sign in with Apple, Apple Pay, App Store review, ATT, App Tracking Transparency, account deletion, expo-splash-screen, deep linking, universal links."
---

# Apple HIG for iPhone (React Native)

Apple's Human Interface Guidelines for **iPhone/iOS**, translated for **React Native + Expo**. Companion to the web-focused `rules-apple` skill — same HIG, but every rule maps to a React Native / Expo API instead of CSS, plus the mobile-only material (ergonomics, edge-swipe back, detents, haptics, App Store rules).

Scope: **iPhone (iOS), React Native.** Not iPad/Watch/TV specifics, not SwiftUI, not web, not Android (adding Android means also consulting Material Design). Apple values in pt; **1pt ≈ 1 RN density-independent unit**. Every rule = **Apple HIG rule + exact RN/Expo API + common RN mistake**, and reads as build guidance *and* as a review check.

## The 7 principles (reasoning vocabulary)

Purpose · Agency · Responsibility · Familiarity · Flexibility · Simplicity · Craft (Delight is a sub-theme of Craft). Build on what people already know about iOS; keep them in control with forgiveness (undo); adapt to every device, input, and ability.

## The load-bearing rules (always true)

1. **Interactive targets ≥ 44×44pt** (28pt floor); ~12pt spacing around bezeled controls, ~24pt around icon-only. → `hitSlop` or `minWidth/minHeight: 44` on `Pressable`.
2. **Contrast 4.5:1** body / **3:1** large-or-bold; aim **7:1** for custom small text; test light *and* dark. `PlatformColor`/`DynamicColorIOS`, not hardcoded hex.
3. **Obey the system, don't rebuild it** — `prefers`-style settings come from the OS: `useColorScheme()`, `AccessibilityInfo.isReduceMotionEnabled()`/`isReduceTransparencyEnabled()`, `allowFontScaling` (leave on). No redundant in-app toggles. **Reduce Motion is only partly automatic in RN**: Reanimated's animation functions default to `ReduceMotion.System`, but core `Animated`, `LayoutAnimation`, Lottie and video don't check it, and "disabled" is not always the right replacement.
4. **Never encode meaning in one channel** (color/motion/haptic alone) — pair with icon + text; announce status via `AccessibilityInfo.announceForAccessibility()`.

## Mobile ergonomics (the iPhone mindset)

- **Reachable wins** — primary actions in the middle/bottom third (bottom tab bars, bottom sheets, bottom-anchored CTAs above the home indicator), not a top toolbar. Don't build phone UIs like scaled-down web pages.
- **Respect the safe area** (Dynamic Island, corners, 34pt home indicator) via `react-native-safe-area-context`; extend backgrounds edge-to-edge, inset only content.
- **Prefer native-backed components over hand-rolled JS** — you inherit gestures, blur, haptics, safe-area, and VoiceOver. Use `@react-navigation/native-stack` (not JS `stack`), `expo-symbols`, native `Alert`/`ActionSheetIOS`, `FlashList`, gesture-handler + reanimated.
- **The #1 RN + App Store mistake:** requesting permissions / onboarding / notification opt-in in a **root-mount `useEffect`**. Do all of it **at point of use** with a stated benefit.
- **App Store gotchas that block release:** Sign in with Apple is effectively mandatory when you offer social login (4.8); in-app account deletion is required if you allow account creation (5.1.1); every permission needs a specific purpose string in `Info.plist` (missing = silent on-device crash); ATT + `NSUserTrackingUsageDescription` required the moment any ad SDK ships.

## Where to look (routing)

| Task | File |
| --- | --- |
| Ergonomics, safe areas, Dynamic Type, dark mode (PlatformColor/DynamicColorIOS), materials/blur, SF Symbols, typography, accessibility, app icons, permissions/privacy copy, writing | [foundations.md](foundations.md) |
| Navigation (native-stack, large titles, edge-back), tab bars, sheets & detents, alerts & action sheets, toggles/sliders/steppers/TextInput/pickers/segmented, lists (FlatList/FlashList/swipe/pull-refresh), context menus, search, progress, buttons | [components.md](components.md) |
| Gestures (gesture-handler), keyboard handling, haptics (expo-haptics), motion (reanimated springs/withDecay/reduce-motion) | [interactions.md](interactions.md) |
| Modality, onboarding, loading, feedback, entering data, permissions, notifications, launching (splash), settings | [patterns.md](patterns.md) |
| Sign in with Apple, Apple Pay, push notifications, ratings, deep/universal links, App Store review requirements | [technologies.md](technologies.md) |
