# Patterns (iOS · React Native)

Interaction flows mapped to React Native / Expo. Format: Apple rule → RN/Expo API → common mistake.

> **Cross-cutting anti-pattern (the #1 RN + App Store mistake):** requesting permissions / firing onboarding / asking for notifications in a **root-mount `useEffect`** at cold start. Apple wants all of these **at the point of use**, with a stated benefit. This recurs in Onboarding, Permissions, and Notifications below — fix it once, everywhere.

## Modality

- **Modal only for a clear benefit** — critical info, confirm/modify the last action, a narrow focused task. Keep it short; **no "app within an app"** (no nested navigator inside a modal). **Never stack modals or show two alerts.** Obvious, consistent dismiss; confirm before dismissing if data would be lost.
- → native-stack `presentation: 'modal' | 'formSheet' | 'fullScreenModal' | 'transparentModal'` (`formSheet` gives native detents — see components.md); `fullScreenModal` can't be gesture-dismissed (good for confirm-before-dismiss flows). `Alert.alert()` queues natively; custom `Modal`s don't — guard with a single `activeModal` state.
- *Mistakes:* independent boolean state per modal (two can be true → visual stacking); a full `Stack.Navigator` nested inside a modal screen.

## Onboarding

- **Teach through interactivity**, not a slideshow; **skippable and don't force again** (keep findable in help/settings); ship good defaults, postpone nonessential setup; tie any permission request to a stated benefit *or* defer to point-of-use.
- → brief intro (`react-native-app-intro-slider`) if any; real teaching via contextual coach-marks (`react-native-copilot`) during use; persist a "seen" flag in `expo-secure-store`/AsyncStorage, checked once at boot.
- *Mistake:* a root `useEffect` firing camera/location/notification prompts back-to-back at cold start.

## Loading

- **Show placeholder structure immediately** (skeletons shaped like the final content), replace progressively; keep other regions interactive; **determinate** progress when duration is knowable, indeterminate only when not; prefetch ahead of need.
- → `moti/skeleton` or `react-native-skeleton-placeholder`; `ActivityIndicator` (native) for indeterminate; `react-native-progress` `Bar`/`Circle` (0–1) for determinate; React Query/SWR (`isLoading` vs background `isFetching`) for non-blocking loads; `RefreshControl` for pull-to-refresh.
- *Mistakes:* a full-screen `ActivityIndicator` gating the whole screen when one section is slow; an indeterminate spinner for a knowable-duration upload.

## Feedback

- **Multi-channel** (color + text/icon + haptic); **inline near the control**, not pulled into a modal; alerts reserved for critical/actionable; **warn before irreversible loss, not routine actions**; explain *why* on failure.
- → inline `<Text>` by the field; `Alert.alert()` only for destructive-confirm/unrecoverable errors; non-blocking toasts via `burnt` (wraps the native iOS toast + haptic) or `react-native-toast-message`; pair with `expo-haptics` `notificationAsync`; **`AccessibilityInfo.announceForAccessibility()`** = the `aria-live` equivalent for VoiceOver.
- *Mistakes:* `Alert.alert()` for routine "Saved!" (a fully blocking native alert — worse than a web toast); color-only error with nothing announced to VoiceOver.

## Entering data

- **Pull from the system over typing** where possible; secure field for sensitive input, **never prepopulate a password**; **choices over free text**; support paste; **validate as they type**; disable Continue until valid.
- → `textContentType` (`oneTimeCode` for SMS autofill, `newPassword` for Keychain suggestion, `emailAddress`, `creditCardNumber`) + cross-platform `autoComplete` (iOS uses `textContentType` when both set); `secureTextEntry` with no initial `value`; `@react-native-picker/picker`/action sheet for enumerable choices; `expo-clipboard` to auto-detect a copied OTP; `react-hook-form` `mode: 'onChange'` with per-field inline errors + `formState.isValid` gating submit.
- *Mistakes:* unset `textContentType` on an OTP/signup field (silently loses SMS autofill / strong-password suggestion — no JS symptom); validating only in the submit handler.

## Permissions & privacy

- **Request only what's needed, at point of use** (not launch); **purpose strings = active, specific, complete sentences.**
- → two-part contract every time: (1) JS request in the feature handler — `useCameraPermissions()`, `requestForegroundPermissionsAsync()` (location), `requestPermissionsAsync()` (media/contacts), `requestTrackingPermissionsAsync()` (ATT), `expo-local-authentication` `authenticateAsync()` (Face ID — check `hasHardwareAsync()`/`isEnrolledAsync()` first); (2) the native purpose string via a **config plugin** (preferred) or `app.json` `ios.infoPlist` (`NSCameraUsageDescription`, `NSFaceIDUsageDescription`, `NSUserTrackingUsageDescription`…).
- *Mistakes:* root-effect requesting; **forgetting the Info.plist string → the app crashes silently on-device** the instant the OS tries to show the prompt (no JS error); vague passive copy that fails review; expecting an OTA update to change purpose strings (needs a native rebuild).

## Managing notifications

- **Explicit opt-in before sending, never at launch;** separate opt-in for marketing vs. transactional with in-app controls; never misuse **Time Sensitive** for marketing; **suppress/redirect when the app is foregrounded**; no sensitive content in the banner.
- → `expo-notifications`: `requestPermissionsAsync({ ios: { allowAlert, allowBadge, allowSound, allowProvisional } })` contextually; `setNotificationHandler` returning `{ shouldShowBanner, shouldShowList, shouldPlaySound, shouldSetBadge }` (current field names — `shouldShowBanner`, not the old `shouldShowAlert`); set `shouldShowBanner: false` when the relevant screen is focused and update in-app UI instead; `setNotificationCategoryAsync(...)` for actions (`options.previewPlaceholder` hides sensitive lock-screen content).
- *Mistakes:* launch-time permission request; no `setNotificationHandler` (a foregrounded app shows a redundant banner); `interruptionLevel: 'timeSensitive'` for promos.

## Launching

- **Launch screen ≠ splash ≠ onboarding** — its only job is instant-feel, "nearly identical to the first screen," **no text, no branding/ads**. Restore state granularly (scroll, tab, form, route) on relaunch.
- → native launch screen via `expo-splash-screen`; `SplashScreen.preventAutoHideAsync()` at module scope + `hideAsync()` gated on an `isReady` flag (fonts/auth/critical data), **not a timer**; `setOptions({ fade })` for the cross-fade. State restoration: `NavigationContainer` `initialState` (read once from AsyncStorage) + `onStateChange` (persist).
- *Mistakes:* holding the splash up for seconds as a fake loader, or adding a logo/animation to it (both ruled out); unconditional `hideAsync()` in an empty-deps effect before fonts/auth resolve → flash of wrong content.

## Settings

- **Best defaults; minimize the number of settings.** **Never duplicate a systemwide setting** (dark mode, Reduce Motion, Dynamic Type) — obey the system automatically instead of shipping a redundant in-app toggle. Task-specific options stay **in-context** (that screen's toolbar), not a global page.
- → `useColorScheme()` (default to system even if you offer an override); subscribe to `AccessibilityInfo` via `addEventListener` for **live** updates when the user toggles Control Center mid-session (`isReduceMotionEnabled`, `isReduceTransparencyEnabled`, `isBoldTextEnabled`, `isScreenReaderEnabled`); leave `allowFontScaling` on.
- *Mistakes:* `allowFontScaling={false}` to protect a layout (opts out of Dynamic Type — an accessibility failure); a custom Dark-Mode/Reduce-Motion toggle that drifts from the system setting.
