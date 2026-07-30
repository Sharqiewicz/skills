# Foundations (iOS · React Native)

The visual/structural bedrock for a native iPhone app, mapped to React Native + Expo. Apple values in pt; **1pt ≈ 1 RN density-independent unit**. Each rule reads as build guidance and as a review check. Format: rule → RN/Expo API → common mistake.

## Designing for iOS — ergonomics

- **Reachable controls win.** iPhone is used at arm's length, often one-handed — put primary actions in the **middle/bottom third**, not a top toolbar. → bottom tab bars (`@react-navigation/bottom-tabs`), bottom sheets, bottom-anchored CTAs above the home indicator. *Mistake:* building phone UIs like scaled-down web pages with a top nav stuffed with icons.
- **Limit onscreen controls; make secondary actions discoverable with minimal interaction** (swipe actions, context menus) rather than exposing every button at once.
- **Adapt to appearance changes** — orientation, Dark Mode, Dynamic Type — seamlessly. Lock portrait unless media-heavy (`expo-screen-orientation`), but never assume a fixed text size or theme.

## Layout & safe areas

- **Respect the safe area** — content must clear the Dynamic Island, camera housing, corner radius, and home indicator. → `react-native-safe-area-context`: wrap the app in `<SafeAreaProvider>`; use `useSafeAreaInsets()` for custom positioning, `<SafeAreaView edges={[...]}>` for containers.
- **Extend backgrounds edge-to-edge; inset only content.** Backgrounds/scroll content reach every edge; padding by insets applies to the *content*, not the background view. → `expo-status-bar` for style; let background `View`s bleed past the safe area.
- **Reserve the bottom inset** (typically **34pt** on Face ID devices) — never sit a button flush with the bottom edge: `bottom: insets.bottom + 16`.
- **Avoid full-width buttons flush to the edges** — inset from system margins.
- *Mistakes:* using the deprecated core `SafeAreaView` from `react-native` (no insets object, buggy in modals) instead of `react-native-safe-area-context`; double-padding (SafeAreaView **and** manual padding); forgetting `<SafeAreaProvider>` (insets return 0 on first render).

## Typography & Dynamic Type

- **iOS text scale** (default "Large") — use the named ramp, not hardcoded sizes:

  | Style | Weight | Size | Leading |
  | --- | --- | --- | --- |
  | Large Title | Regular | 34 | 41 |
  | Title 1/2/3 | Regular | 28/22/20 | 34/28/25 |
  | Headline | Semibold | 17 | 22 |
  | Body / Callout | Regular | 17 / 16 | 22 / 21 |
  | Subhead / Footnote | Regular | 15 / 13 | 20 / 18 |
  | Caption 1/2 | Regular | 12/11 | 16/13 |

  Body **17pt**, minimum **11pt**. Avoid Ultralight/Thin/Light weights.
- **Support Dynamic Type — enlarge text ≥200%.** → `<Text>` has `allowFontScaling` (**default `true`** — leave it on); use `dynamicTypeRamp="body"|"headline"|"largeTitle"|…` (iOS) to get Apple's text-style semantics instead of hardcoded `fontSize`. Cap only where truly needed with `maxFontSizeMultiplier` on a single node (e.g. a one-line badge).
- **Scale layout with text, not just the font.** → `PixelRatio.getFontScale()` to branch layout (e.g. row → stacked when scale > 1.3). **Scale meaningful icons up with text** too.
- *Mistakes:* `allowFontScaling={false}` globally to "fix" layout (an accessibility bug — fix the layout instead); hardcoding `fontSize: 17` everywhere; never testing at AX5.

## Color & Dark Mode

- **Contrast:** 4.5:1 for text ≤17pt/regular, 3:1 for ≥18pt or bold; aim **7:1** for custom small text. Brand colors that pass in light often fail in dark — test both.
- **Don't hard-code system colors; don't naively invert.** → `PlatformColor('label'|'secondaryLabel'|'systemBackground'|'systemBlue'|…)` for Apple's semantic colors (gate with `Platform.OS === 'ios'`); `DynamicColorIOS({ light, dark, highContrastLight?, highContrastDark? })` for your own adaptive colors — this is the correct way to get **Increase Contrast** support for free.
- **React to the system theme:** `useColorScheme()` → `'light'|'dark'|null` (handle `null`); or the `Appearance` module. Set app-wide default via `app.json` `ios.userInterfaceStyle`.
- **Dark mode uses base vs. elevated backgrounds** (elevated = brighter, for modals/sheets) — convey z-order by luminance, not just color. **Never rely on color alone** for state — pair with icon/shape/text.
- *Mistakes:* hand-rolling two hardcoded hex palettes instead of `DynamicColorIOS` (loses Increase Contrast); encoding row state via background color only.

## Materials (translucency)

- **Materials belong on floating chrome** (nav bars, tab bars, sheets, modals over media) so content shows through — **not on content-layer cards.** iOS material family: ultra-thin → thin → regular → thick (thicker = better text contrast; thinner = more context).
- → `expo-blur` `<BlurView tint intensity>` (`tint`: light/dark/default/regular/prominent…; `intensity` 1–100, animatable via reanimated). No public RN binding for iOS 26 Liquid Glass yet — don't hand-roll it into content.
- **Honor Reduce Transparency** — fall back to a solid tint when `AccessibilityInfo.isReduceTransparencyEnabled()` is true.
- *Mistakes:* faking blur with a semi-transparent overlay `View` (flat, wrong in dark mode); `BlurView` on every card (perf + violates "use sparingly"); the stale-blur bug when a `BlurView` renders above a `FlatList` — render it after / re-render on scroll.

## SF Symbols

- **Use SF Symbols for iconography** — they're Dynamic-Type-aware and weight-matched to text. → `expo-symbols` `<SymbolView name weight scale type>`.
  - `weight`: Apple's 9 (`ultraLight`…`black`) — **pair to the adjacent text weight**.
  - `scale`: `small|medium|large` (relative to cap height).
  - `type` (rendering mode): `monochrome|hierarchical|palette|multicolor`; use `fill` variants for tab bars / swipe actions, outline elsewhere.
  - Cross-platform fallback via `name={{ ios, android }}`.
- **Every icon-only control needs an accessible label** (`accessibilityLabel` on the wrapping `Pressable`).
- *Mistakes:* defaulting to a generic icon font (Ionicons) and never using SF Symbols; mismatching symbol weight/scale to adjacent text; `multicolor` when the intrinsic colors clash with your palette (use `monochrome`/`hierarchical` + `tintColor`).

## App icons

- **1024×1024px flat PNG**, square, no transparency, **no pre-rounded corners** — the system masks to the device curvature; don't bake in shadows/bevels; keep primary content centered so masking doesn't clip it.
- → `app.json` `icon` (single 1024 source; Expo/EAS generates all sizes). Optional `ios.icon` as `{ light, dark, tinted }` for the iOS 18+ appearance-aware icon.
- *Mistakes:* transparency or pre-rounded corners (double-masking / alpha artifacts); off-center art that clips after masking.

## Accessibility

- **Tap targets ≥ 44×44pt** (28pt absolute floor); ~12pt spacing around bezeled controls, ~24pt around icon-only ones. → `hitSlop` on `Pressable`/touchables when the visual is smaller than 44, or `minWidth/minHeight: 44`. *(Undersized icon-only targets are the #1 layout-related App Store rejection for RN apps.)*
- **Label everything for VoiceOver.** → `accessible`, `accessibilityLabel`, `accessibilityHint`, `accessibilityRole` (`button`/`header`/`link`/`image`/`adjustable`), `accessibilityState` (`disabled`/`selected`/`checked`/`busy`). iOS extras: `accessibilityViewIsModal`, `accessibilityElementsHidden`, `accessibilityIgnoresInvertColors`.
- **Check assistive settings before animating / blurring:** `AccessibilityInfo.isReduceMotionEnabled()`, `isReduceTransparencyEnabled()`, `isScreenReaderEnabled()`, `isBoldTextEnabled()`. Reduce Motion → tighten springs, drop z-axis/depth, replace slide with fade, avoid animating into/out of blur.
- **Minimize time-boxed UI** — don't auto-dismiss toasts on a timer with no manual dismiss.
- *Mistakes:* interactive `View`/`Text` without `accessibilityRole="button"` + `accessible`; never checking `isReduceMotionEnabled()`.

## Writing (microcopy)

- **Verb-first buttons** ("Send", not "Let's do it!"); never "Click here" (and on touch, "tap"/"select"). **No "we"** in errors — "Unable to load content", not "We're having trouble…". **No "oops"/"uh-oh".**
- **Errors state the fix:** "Choose a password with at least 8 characters", not "That password is too short."
- Applies to every `Text`, `Alert.alert(title, message)`, and inline field-error string. *Mistake:* pasting web-style toasts ("Oops! Something went wrong 😅") into `Alert.alert`.

## Privacy & permissions

- **Purpose strings: an active, specific, complete sentence** ending in a period. ✅ "The app records at night to detect snoring." ❌ "Microphone access is needed for a better experience."
- **Request at point of use**, not on launch (unless the app's core need is obvious immediately). → call `requestForegroundPermissionsAsync()` / `useCameraPermissions()` inside the feature's handler, not a root `useEffect`.
- → Purpose strings go in `app.json` `ios.infoPlist` (`NSCameraUsageDescription`, …) **or** the library's config-plugin fields (preferred — wires the correct key). **Native-build only — cannot ship over-the-air; needs a new EAS build.**
- **Custom pre-permission screen:** exactly one neutral button ("Continue"), no Cancel, never mimic the system dialog.
- *Mistakes:* leaving Expo's default boilerplate purpose strings (Apple rejects generic ones); requesting all permissions in one boot `useEffect`; expecting OTA updates to change Info.plist strings.
