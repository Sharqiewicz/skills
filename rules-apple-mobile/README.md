# rules-apple-mobile

Apple's **Human Interface Guidelines for iPhone/iOS**, translated for **React Native + Expo** — a complete, standalone skill for building native iOS apps. The mobile companion to `rules-apple` (which is web/CSS). Every rule works as **build guidance** and as a **review check**, and each carries **Apple's HIG rule + the exact React Native/Expo API + the common RN mistake**.

**Scope:** iPhone (iOS) · React Native. Not iPad/Watch/TV, not SwiftUI, not web, not Android (Android would also need Material Design). Apple values in pt; 1pt ≈ 1 RN density-independent unit.

## What's inside

`SKILL.md` is always loaded (principles + load-bearing rules + mobile ergonomics + routing); reference files load on demand.

| File | Covers |
| --- | --- |
| `SKILL.md` | 7 principles · load-bearing rules (44pt, 4.5:1/3:1, obey-the-system, never one channel) · mobile ergonomics · App Store gotchas · routing |
| `foundations.md` | Ergonomics · safe areas (`react-native-safe-area-context`) · Dynamic Type (`allowFontScaling`, `dynamicTypeRamp`) · dark mode (`useColorScheme`, `PlatformColor`, `DynamicColorIOS`) · materials (`expo-blur`) · SF Symbols (`expo-symbols`) · typography · accessibility · app icons · permissions/privacy · writing |
| `components.md` | Navigation (`@react-navigation/native-stack`, large titles, edge-back) · tab bars · sheets & detents (`formSheet`, `@gorhom/bottom-sheet`) · `Alert`/`ActionSheetIOS` · `Switch`/slider/stepper/`TextInput`/pickers/segmented · lists (`FlatList`/`FlashList`, swipe-to-delete, `RefreshControl`) · context menus · search · progress · buttons |
| `interactions.md` | Gestures (`react-native-gesture-handler`) · keyboard (`TextInput`, `react-native-keyboard-controller`) · haptics (`expo-haptics`) · motion (`react-native-reanimated` — `withSpring`, `withDecay`, Reduce Motion) |
| `patterns.md` | Modality · onboarding · loading · feedback · entering data · permissions · notifications (`expo-notifications`) · launching (`expo-splash-screen`) · settings |
| `technologies.md` | Sign in with Apple (`expo-apple-authentication`) · Apple Pay (`@stripe/stripe-react-native`) · push · ratings (`expo-store-review`) · deep/universal links · App Store Review requirements |

## How to invoke it

- **Automatically** — matches on React Native / Expo / iOS-app triggers (native-stack, safe area, SF Symbols, `Alert.alert`, reanimated, `expo-notifications`, App Store, ATT…).
- **Explicitly** — `/rules-apple-mobile` to force it.

## Build mode

```
/rules-apple-mobile build a settings screen: grouped list, native switches,
an inset "Delete Account" row, and a form sheet with medium/large detents.
```
You get: `SectionList` grouped style, native `Switch` in rows, the App-Store-required account-deletion flow, native-stack `formSheet` with `sheetAllowedDetents`/`sheetGrabberVisible`, safe-area handling, and the Reduce-Motion opt-in.

## Review mode

```
/rules-apple-mobile review src/screens/Checkout.tsx against Apple's HIG for iOS
```
Typical flags: permission requested in a root `useEffect` instead of at point of use · missing `Info.plist` purpose string · destructive button styled as primary · sub-44pt icon target with no `hitSlop` · Reanimated animation with no `ReduceMotion` config · social login present but no Sign in with Apple · `Alert.alert` used for a routine "Saved!" toast.

## Pairs with

- **`rules-apple`** — the web/CSS sibling; same HIG, different platform. Use whichever matches what you're building.
- **`/code-review`** — logic/bugs after the design pass.

## Sourcing & maintenance

Rules are drawn from the current iOS HIG (fetched via the DocC JSON API / render proxy — the HIG site is an SPA that blocks plain fetches) plus current React Native (0.86) / Expo SDK / React Navigation / library docs (July 2026). RN's ecosystem moves fast — re-verify API names (e.g. `headerLargeTitleEnabled`, FlashList v2's New-Architecture requirement, `shouldShowBanner`) against the current docs when updating.
