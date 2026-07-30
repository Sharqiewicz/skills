# Technologies & App Store (iOS · React Native)

Apple technologies an RN iPhone app actually uses, plus the App Store Review rules that get RN apps rejected. Format: Apple rule → RN/Expo module → pitfall / rejection risk.

## Sign in with Apple — `expo-apple-authentication`

- **Offer only in exchange for value; delay as long as possible** (not at first launch). **Never ask for a password.** **Respect Private Relay emails** — never reject or require a "real" one.
- Present alongside other providers, same prominence, no scroll to see it. Button text is fixed: "Sign in / Sign up / Continue with Apple". → `<AppleAuthenticationButton buttonStyle={WHITE|WHITE_OUTLINE|BLACK} buttonType={SIGN_IN|CONTINUE|SIGN_UP}>`.
- Gate with `AppleAuthentication.isAvailableAsync()` (iOS 13+). `signInAsync({ requestedScopes: [FULL_NAME, EMAIL] })`. Config: `app.json` `ios.usesAppleSignIn: true`.
- **The name/email come back only on the FIRST sign-in** — persist them immediately (server or `expo-secure-store`); re-auth returns only the stable user ID.
- ⚠️ **Guideline 4.8 — effectively mandatory when you offer any social login** (Google/Facebook/…): missing it is one of the most common RN rejections. Also: custom buttons that deviate from Apple's spec get flagged; losing the one-time name/email is a frequent bug.

## Apple Pay — `@stripe/stripe-react-native`

- **Feature-detect**; make Apple Pay the primary (pre-selected) option, not necessarily the only one. **Only the official button** — never a custom "Apple Pay" replica. Text is always "Apple Pay" (two words, never translated).
- → `<StripeProvider merchantIdentifier="merchant.com.yourapp">`; `isPlatformPaySupported()` to gate; `<PlatformPayButton type={Order} appearance={Black}>` (this *is* the native Apple Pay button); `confirmPlatformPayPayment(clientSecret, { applePay: { cartItems, merchantCountryCode, currencyCode } })`. Needs a Merchant ID + Apple Pay capability + Stripe cert; **not in Expo Go** (dev build required).
- ⚠️ No async work between tap and `confirmPlatformPayPayment()` — the sheet must appear immediately. **Digital goods/subscriptions consumed in-app must use In-App Purchase (StoreKit), not Stripe/Apple Pay** (Guideline 3.1.1) — Apple Pay is for physical goods/services. Frequent confusion → rejection.

## Push notifications — `expo-notifications`

- **Opt-in before sending**; a **separate** consent for marketing (don't bundle it into the system prompt). Provide **in-app** per-category preferences, not just OS Settings. **No sensitive content in the banner body** (lock-screen visibility). Ask contextually where the value is obvious.
- Interruption levels: Passive / Active (default) / **Time Sensitive** (immediate relevance only — never marketing) / Critical (special entitlement, health/safety).
- → `requestPermissionsAsync()` (read `settings.ios?.status`, not the top-level status); `getPermissionsAsync()` for a silent check before your own pre-prompt; `setNotificationHandler` (respond <3s); `setBadgeCountAsync()`; `scheduleNotificationAsync()`; `setNotificationCategoryAsync()` for actions.
- ⚠️ **SDK 53+: remote push doesn't work in Expo Go — needs a dev build.** Sending marketing as "Time Sensitive" to dodge Focus is an HIG violation.

## Ratings & reviews — `expo-store-review`

- **Ask after real engagement** (task/level completed), never onboarding, never mid-task. System caps at **3 prompts / 365 days** automatically. → `StoreReview.requestReview()`; gate with `isAvailableAsync()` (silently no-ops in TestFlight).
- ⚠️ **Guideline 4.10 — never gate the native prompt behind a satisfaction filter** ("Enjoying the app? Yes→rate / No→feedback"). Explicit rejection reason. Don't wire `requestReview()` to a "Rate us" button tap — call it after a signature interaction.

## Universal links & deep linking — `expo-linking` / React Navigation / Expo Router

- **Links open directly to the content if it exists; degrade gracefully** (search/home) if not — never a dead/blank screen. Prefer **Universal Links** (`https://`, domain-verified) over custom schemes (work when the app isn't installed; can't be squatted).
- → `app.json` `ios.associatedDomains: ["applinks:app.example.com"]` + host `/.well-known/apple-app-site-association`. React Navigation `linking={{ prefixes: ['myapp://','https://app.example.com'], config }}`. **Expo Router** auto-wires per-route deep linking (recommended default).
- ⚠️ AASA must be served with correct content-type, no redirect, matching Team+Bundle ID — a silent break while the custom scheme still "works" masks the bug. Custom-scheme-only links can be hijacked by other apps.

## App Store Review — the design/UX rules RN devs trip on

| Guideline | Rule | RN action |
| --- | --- | --- |
| **4.8** | Offering social login → must offer a privacy-preserving equivalent | Add Sign in with Apple whenever any social login SDK is present |
| **5.1.1(v)** | Account creation → must offer **in-app account deletion** | Build a real "Delete Account" flow in settings; web-redirect-only or "contact support" gets rejected |
| **5.1.1(ii)** | Every permission needs a clear, specific purpose string | Info.plist via config plugins; vague strings ("needs your location") are rejected |
| **5.1.2(i)** | **App Tracking Transparency** before cross-app ad tracking; can't gate core features behind granting it | `expo-tracking-transparency` `requestTrackingPermissionsAsync()` + `NSUserTrackingUsageDescription` mandatory the moment any ad/attribution SDK is bundled |
| **4.2** | No "repackaged website" — need real native functionality | A `WebView` wrapper of your marketing site is rejected |
| **2.1(a)** | Fully functional build + working demo account for login-gated apps | Always put demo creds in review notes |
| **2.3 / Privacy labels** | App Privacy nutrition label must match actual data collection | Must reflect what RN native modules (analytics, crash, ads) actually collect — mismatches cause suspensions |

## Other Apple tech — triage for RN

**Feasible via native modules / config plugins:** HealthKit (`react-native-health` / `react-native-healthkit`) · Home-Screen **Widgets** & **Live Activities** (`expo-live-activity`, Voltra, `react-native-widget-extension` — needs a WidgetKit target, not Expo Go) · CarPlay (`react-native-carplay`) · NFC (`react-native-nfc-manager`) · iCloud KV/docs (`react-native-cloud-store`) · App Clips (separate native target) · SiriKit/Shortcuts (`react-native-siri-shortcut`).

**Out of scope for typical RN:** HomeKit (no maintained bridge) · SharePlay/GroupActivities · advanced ARKit/RealityKit · Matter / secure-enclave work — all fully-custom-native territory.
