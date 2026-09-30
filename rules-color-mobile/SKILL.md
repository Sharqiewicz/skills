---
name: rules-color-mobile
description: "Colour rules for React Native + Expo on iOS: design in OKLCH but emit only formats RN accepts (hex, rgb, hsl), use PlatformColor for iOS semantic colours, DynamicColorIOS for light, dark and high-contrast pairs, useColorScheme and Appearance for theming, contrast ratios and Increase Contrast, one tint colour, and dark-mode elevation. Every rule = principle + the exact RN/Expo API + the common RN mistake. For web, use /better-colors and /oklch-skill. Triggers on: color, colour, theme, dark mode, light mode, useColorScheme, Appearance, setColorScheme, userInterfaceStyle, PlatformColor, DynamicColorIOS, systemBackground, label, secondaryLabel, semantic colors, design tokens, palette, OKLCH, oklch, hex, contrast, WCAG, Increase Contrast, isDarkerSystemColorsEnabled, tint color, accent color, elevated background, separator, status bar, expo-system-ui."
user-invocable: true
---

Colour rules for React Native + Expo on iOS: author palettes in OKLCH, ship values RN can parse, prefer system semantic colours, and make every pair work in light, dark and high contrast.

## MANDATORY PREPARATION

1. Find the existing colour source: a theme file, tokens, `constants/Colors`, or inline hex. All fixes go there.
2. Check `app.json` / `app.config.*` for `userInterfaceStyle` and whether `expo-system-ui` is installed. [Expo: Color themes](https://docs.expo.dev/develop/user-interface/color-themes/)
3. Decide the target: iOS-only (use `PlatformColor` and `DynamicColorIOS`) or iOS plus Android (wrap platform calls in `Platform.select`).
4. For general HIG rules see `/sharqiewicz:rules-apple-mobile`. For OKLCH theory see `/oklch-skill`.

---

## Quick Reference

| Need | API |
|---|---|
| Native semantic colour | `PlatformColor('label')`, `PlatformColor('systemBackground')` |
| Custom light/dark/contrast pair | `DynamicColorIOS({ light, dark, highContrastLight, highContrastDark })` |
| Current scheme in JS | `useColorScheme()` returns `'light'`, `'dark'` or `null` |
| Force or release scheme | `Appearance.setColorScheme('light' \| 'dark' \| 'unspecified')` (`'auto'` removes the override per RN docs) |
| Follow system | `userInterfaceStyle: "automatic"` (Expo default) |
| User raised contrast | `AccessibilityInfo.isDarkerSystemColorsEnabled()` (iOS) |
| Inverted display | `accessibilityIgnoresInvertColors` on images and video (iOS) |

---

**CRITICAL**: RN documents hex, `rgb()`, `hsl()`, `hwb()`, named colours, `PlatformColor` and `DynamicColorIOS`, and does not list `oklch()`. Design in OKLCH if you like, but emit only a documented format, and take surfaces and text from semantic colours so light, dark and Increase Contrast work without per-screen branches.

## Core Principles

### 1. Design in OKLCH, emit what RN parses

RN documents these colour formats: hex (`#rgb`, `#rrggbb`, `#rgba`, `#rrggbbaa`), `rgb()`/`rgba()`, `hsl()`/`hsla()`, `hwb()`, colour ints, lowercase named colours, `'transparent'`, plus `PlatformColor` and `DynamicColorIOS`. OKLCH and LAB are not listed. [RN: Colors](https://reactnative.dev/docs/colors)

- Pick lightness, chroma and hue in OKLCH (even ramps, predictable contrast) and convert to sRGB hex **at design time or in a build script**. Commit the hex, keep the OKLCH source as a comment.
- Do not write `'oklch(...)'`, `'color(display-p3 ...)'`, `var()`, `color-mix()` or `rgb(from ...)` in a style. They are not in the documented list, so treat them as unsupported. <!-- UNVERIFIED: newer RN versions may parse more; test on device before relying on it -->
- Check the gamut: clamp out-of-gamut OKLCH to sRGB (reduce chroma) before converting, rather than letting a tool clip channels.
- Named colours must be lowercase; `'Red'` fails. [RN: Colors](https://reactnative.dev/docs/colors)
- Colour ints are `0xrrggbbaa` in RN, unlike Android's `0xaarrggbb`. Prefer hex strings to avoid the mix-up.
- **Common mistake:** pasting a web `oklch()` token straight into `StyleSheet`, which renders transparent or black with no error.

### 2. Prefer system semantic colours

`PlatformColor(name)` reads a native colour, which adapts to appearance and accessibility settings; extra arguments are fallbacks. [RN: PlatformColor](https://reactnative.dev/docs/platformcolor) iOS names come from UIKit: `label`, `secondaryLabel`, `tertiaryLabel`, `quaternaryLabel`, `systemBackground`, `secondarySystemBackground`, `tertiarySystemBackground`, `systemGroupedBackground`, `separator`, `opaqueSeparator`, `systemFill`, plus `systemBlue` and the other `system*` colours. [Apple: UI element colors](https://developer.apple.com/documentation/uikit/uicolor/ui_element_colors)

- Use system colours for text, backgrounds, separators and fills. You get dark mode, elevation and Increase Contrast for free. [HIG: Color](https://developer.apple.com/design/human-interface-guidelines/color)
- Use custom hex only for brand surfaces and accents that system colours cannot express.
- Wrap in `Platform.select({ ios: PlatformColor('label'), default: '#111111' })`; an iOS name on Android throws. [RN: PlatformColor](https://reactnative.dev/docs/platformcolor)
- A `PlatformColor` value is an opaque object: you cannot read its RGB, add alpha by string concatenation, or pass it to a colour library.
- **Common mistake:** `color: PlatformColor('label') + '80'` for opacity. Use the `opacity` style, or `DynamicColorIOS` with explicit alpha values.

### 3. Custom pairs with DynamicColorIOS

`DynamicColorIOS({ light, dark, highContrastLight?, highContrastDark? })` lets the system choose; missing high-contrast keys fall back to `light` or `dark`. [RN: DynamicColorIOS](https://reactnative.dev/docs/dynamiccolorios)

- Define every brand token as a pair; add the two high-contrast keys for text, separators and any fill that carries meaning.
- The system selects the value from the current appearance and accessibility settings, so you need no `useColorScheme()` branch for it. [RN: DynamicColorIOS](https://reactnative.dev/docs/dynamiccolorios)
- It is iOS-only. Guard with `Platform.OS === 'ios'`.
- **Common mistake:** a high-contrast key identical to the normal one, which makes Increase Contrast a no-op.

### 4. Theme tokens: semantic names, one switch point

- Name by role (`textPrimary`, `surface`, `surfaceRaised`, `border`, `accent`, `danger`), not by value (`gray700`). A token holds a light value and a dark value.
- Build the theme in one place: either `DynamicColorIOS`/`PlatformColor` per token, or a `light` and `dark` object selected by `useColorScheme()` through a context. `useColorScheme` subscribes to system, `setColorScheme` and scheduled changes. [RN: useColorScheme](https://reactnative.dev/docs/usecolorscheme)
- `useColorScheme()` can return `null` when the native module is unavailable. Treat `null` as light. [RN: useColorScheme](https://reactnative.dev/docs/usecolorscheme)
- Do not cache `Appearance.getColorScheme()` in a constant; call it per render, or use the hook. [RN: Appearance](https://reactnative.dev/docs/appearance)
- In Expo, `userInterfaceStyle` is `automatic` by default; `"light"` or `"dark"` forces one. On Android it needs `expo-system-ui`, or the setting is ignored. [Expo: Color themes](https://docs.expo.dev/develop/user-interface/color-themes/)
- Do not add an in-app light/dark switch; Apple says an app-specific appearance setting makes people adjust two settings and can look broken. Use `setColorScheme` only for a product reason such as a dark-only media app. [HIG: Dark Mode](https://developer.apple.com/design/human-interface-guidelines/dark-mode)
- Set the root background (and `StatusBar` style) from the theme, so overscroll and transitions do not flash white in dark mode.
- **Common mistake:** `userInterfaceStyle: "light"` left in `app.json` while the code supports dark, so the dark branch never runs.

### 5. Contrast, including Increase Contrast

Apple uses WCAG AA minimums: 4.5:1 for text up to 17pt at any weight, 3:1 for 18pt and larger, and 3:1 for bold text. If your colours miss that by default, provide a higher-contrast scheme when Increase Contrast is on, and check both light and dark. [HIG: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility) In Dark Mode the floor is 4.5:1 and custom foreground/background pairs should aim for 7:1, especially small text. Increase Contrast in Dark Mode can reduce contrast between dark text and a dark background, so test it (also together with Reduce Transparency). [HIG: Dark Mode](https://developer.apple.com/design/human-interface-guidelines/dark-mode)

- Check each text/background token pair in light, dark, and with elevated surfaces (principle 6).
- Read the setting with `AccessibilityInfo.isDarkerSystemColorsEnabled()` only when you need JS logic. Prefer `DynamicColorIOS` high-contrast keys, which need no code. [RN: AccessibilityInfo](https://reactnative.dev/docs/accessibilityinfo)
- `isHighTextContrastEnabled()` is the Android equivalent. [RN: AccessibilityInfo](https://reactnative.dev/docs/accessibilityinfo)
- Pair colour with an icon, label or shape for status (error, success, selected).
- Placeholder and disabled text still need to be legible; do not go below the pair's threshold to signal "disabled", use opacity on the whole control plus state semantics.
- Test with iOS Invert Colors: mark photos and video with `accessibilityIgnoresInvertColors`. [RN: Accessibility](https://reactnative.dev/docs/accessibility)
- **Common mistake:** light-grey secondary text (`#999` on white) that passes by eye on a bright phone and fails measured contrast.

### 6. Dark mode is not inversion

Dark Mode palettes are dimmer backgrounds and brighter foregrounds, not plain inversions. The system uses base (dimmer, recedes) and elevated (brighter, advances) backgrounds, switching automatically for popovers, modal sheets and multitasking separation. Custom background colours make those cues harder to see, so prefer the system ones. [HIG: Dark Mode](https://developer.apple.com/design/human-interface-guidelines/dark-mode)

- Surfaces: `systemBackground` for the screen, `secondarySystemBackground` for cards on it; grouped lists use the `*GroupedBackground` set. Modal sheets take elevated colours automatically with system colours. [HIG: Dark Mode](https://developer.apple.com/design/human-interface-guidelines/dark-mode)
- Custom dark surfaces: raise lightness in OKLCH (a few points of L per layer) instead of adding a shadow, since shadows are barely visible on dark.
- Drop saturation a little for large dark-mode fills; reduce chroma for accents that look neon on black.
- Avoid pure `#000000` text-on-white inversions and pure `#ffffff` text on black for long reading; use `label`.
- Provide dark variants of images and icons, or use template images tinted by a semantic colour.
- **Common mistake:** a hardcoded `backgroundColor: '#fff'` on a modal, which stays white in dark mode.

### 7. One tint colour

- Pick one accent for interactive elements and use it everywhere (links, selected tab, primary button). Do not colour decorative elements with it.
- Wire it once: native-stack `headerTintColor` (back button and title) and bottom-tabs `tabBarActiveTintColor` / `tabBarInactiveTintColor`. [React Navigation: Native Stack](https://reactnavigation.org/docs/native-stack-navigator), [Bottom Tabs](https://reactnavigation.org/docs/bottom-tab-navigator)
- Define the accent as a `DynamicColorIOS` pair: brighter or lighter in dark mode, deeper in high contrast.
- If there is no brand accent, use `PlatformColor('systemBlue')` so it matches the system.
- **Common mistake:** a tint that passes on white but fails on the dark surface, because only one value was chosen.

---

## Decision Flowchart

**Which colour source for this value?**
- Text, background, separator, fill → `PlatformColor` semantic name.
- Brand colour with light/dark → `DynamicColorIOS` pair with high-contrast keys.
- Cross-platform screen → theme object + `useColorScheme()`, with `Platform.select` for native ones.
- Needs alpha or maths on channels → a resolved hex pair, not `PlatformColor`.

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| `oklch(...)` in a style | Convert to hex at design time |
| Hex `#ffffff`, `#000000` everywhere | `PlatformColor` / tokens |
| `PlatformColor` + `'80'` alpha | `opacity`, or a `DynamicColorIOS` pair with alpha |
| Caching `getColorScheme()` in a constant | `useColorScheme()` |
| No high-contrast keys | Add `highContrastLight` / `highContrastDark` |
| Status by colour only | Add icon and text |
| `PlatformColor('label')` on Android | `Platform.select` |

---

## Review Checklist

- [ ] No `oklch()`, `color-mix()`, `var()` or other web syntax in styles
- [ ] Text, background and separators use semantic tokens, not raw hex
- [ ] Every custom token has a dark value, and text/line tokens have high-contrast values
- [ ] Contrast checked per pair in light, dark and elevated
- [ ] `userInterfaceStyle` matches the supported appearances
- [ ] Root background and status bar follow the theme
- [ ] One accent, defined once, contrast-checked in both modes
- [ ] Meaning never depends on colour alone

**NEVER:**
- Hardcode `#fff`/`#000` for surfaces or text.
- Invert light colours mechanically to get the dark theme.
- Cache the colour scheme in a module constant.
- Call `PlatformColor` with an iOS name on Android without `Platform.select`.
- Do string maths on a `PlatformColor` or `DynamicColorIOS` value.
- Use a second accent colour for interactive elements.

## Verify

- Toggle light/dark while the app is open; every screen, sheet and status bar follow.
- Turn on Settings, Accessibility, Display & Text Size, Increase Contrast: text and borders get stronger.
- Run contrast numbers for text tokens against `surface` and the elevated surface.

Colour is a set of roles that the system resolves for each appearance; author in OKLCH, ship hex, and let iOS pick.
