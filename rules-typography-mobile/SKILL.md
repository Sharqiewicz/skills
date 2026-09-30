---
name: rules-typography-mobile
description: "Typography rules for React Native + Expo on iOS: Dynamic Type (allowFontScaling, maxFontSizeMultiplier, dynamicTypeRamp, PixelRatio.getFontScale), the system font and iOS text styles, tabular numbers, line height in points, truncation with numberOfLines and ellipsizeMode, custom fonts with expo-font, adjustsFontSizeToFit caveats, and letter spacing. Every rule = principle + the exact RN/Expo API + the common RN mistake. For web, use /better-typography. Triggers on: typography, font, font size, Dynamic Type, allowFontScaling, maxFontSizeMultiplier, dynamicTypeRamp, getFontScale, fontScale, large text, text size, San Francisco, system font, fontFamily, fontWeight, fontVariant, tabular-nums, lineHeight, letterSpacing, numberOfLines, ellipsizeMode, truncate, adjustsFontSizeToFit, minimumFontScale, expo-font, useFonts, custom font, Text component, text styles, heading, caption."
user-invocable: true
---

Typography rules for React Native + Expo text on iOS: scale with the user's text size, use the system font by default, and keep numbers, lines and truncation predictable.

## MANDATORY PREPARATION

1. Find how text is styled today: a shared `Text` wrapper, a theme object, or inline styles. Fix typography in that one place.
2. Check for custom fonts (`expo-font` plugin or `useFonts`) and any global `Text.defaultProps` or `allowFontScaling={false}`.
3. Read `/sharqiewicz:rules-apple-mobile` for the HIG Dynamic Type basics and do not repeat them here. For layout that must survive large text see `/sharqiewicz:rules-layout-mobile`.

---

## Quick Reference

| Need | API | Note |
|---|---|---|
| Respect user text size | leave `allowFontScaling` at default `true` | iOS and Android |
| Cap runaway scaling | `maxFontSizeMultiplier={1.5}` | `0` means no cap; `undefined` inherits |
| Pick the iOS scaling curve | `dynamicTypeRamp="body"` | iOS only, default `body` |
| Read the user's scale | `PixelRatio.getFontScale()` or `useWindowDimensions().fontScale` | hook re-renders on change |
| System font | omit `fontFamily`, or `'system-ui'`, `'ui-rounded'`, `'ui-serif'`, `'ui-monospace'` | generic families are iOS only |
| Aligned digits | `fontVariant: ['tabular-nums']` | |
| Truncate | `numberOfLines` + `ellipsizeMode` | |
| Custom font | `expo-font` config plugin or `useFonts` | one file per weight |

---

**CRITICAL**: Text scales with the user's Text Size setting. Leave `allowFontScaling` on for reading text, cap it with `maxFontSizeMultiplier` only where layout demands it, and build the layout so it can grow instead of clipping.

## Core Principles

### 1. Text scales with the user, and layout must follow

`allowFontScaling` defaults to `true`; `maxFontSizeMultiplier` sets the largest scale, where `0` means no limit and it inherits from a parent when `undefined`. [RN: Text](https://reactnative.dev/docs/text) The scale comes from iOS Settings, Display & Brightness, Text Size and Accessibility, Larger Text. [RN: PixelRatio](https://reactnative.dev/docs/pixelratio)

- Leave scaling on for all reading text. Turning it off with `allowFontScaling={false}` is an accessibility bug, not a styling choice.
- When something genuinely cannot grow (a tab-bar label, a badge count, a fixed-height chip), cap it with `maxFontSizeMultiplier` around 1.2 to 1.5 rather than disabling. <!-- values are a house recommendation, not from Apple -->
- Set a global cap once, in the shared `Text` wrapper, and let individual nodes override it.
- Never fix a container's `height` around text. Use `minHeight` plus padding, so the row grows with the font.
- Stack horizontal rows vertically when `useWindowDimensions().fontScale` is large, instead of clipping.
- **Common mistake:** `allowFontScaling={false}` on everything to "keep the design", or fixed-height buttons that cut off text at larger sizes.

### 2. Use iOS text styles as the size scale

`dynamicTypeRamp` picks which Apple text style's curve scales the element: `caption2`, `caption1`, `footnote`, `subheadline`, `callout`, `body` (default), `headline`, `title3`, `title2`, `title1`, `largeTitle`. [RN: Text](https://reactnative.dev/docs/text) Apple scales fonts per text style, and custom fonts follow the same curve through `UIFontMetrics`. [Apple: Scaling fonts automatically](https://developer.apple.com/documentation/uikit/scaling-fonts-automatically)

- Define a small token set (`largeTitle`, `title`, `headline`, `body`, `footnote`, `caption`) with size, weight, line height **and** `dynamicTypeRamp`, then use only tokens.
- Match the ramp to the role: a 13pt footnote should use `dynamicTypeRamp="footnote"` so it does not scale like body text.
- Apple's iOS sizes at the default (Large) setting, size/leading in points: Large Title 34/41, Title 1 28/34, Title 2 22/28, Title 3 20/25, Headline 17/22 (semibold), Body 17/22, Callout 16/21, Subhead 15/20, Footnote 13/18, Caption 1 12/16, Caption 2 11/13. Default text size is 17pt, minimum 11pt. [HIG: Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
- Hierarchy comes from weight and size together. Keep to few weights (regular, semibold, bold).
- **Common mistake:** every `Text` uses the default `body` ramp, so headings and captions scale at the wrong rate.

### 3. System font first

Omit `fontFamily` and iOS renders the system font (San Francisco). For explicit system variants RN accepts `'system-ui'`, `'ui-sans-serif'`, `'ui-serif'`, `'ui-monospace'`, `'ui-rounded'` on iOS. [RN: Text Style Props](https://reactnative.dev/docs/text-style-props)

- The system font picks optical sizes and handles Dynamic Type for you; a custom font costs weight and tracking tuning.
- `fontWeight` accepts `'100'` to `'900'`, `'normal'`, `'bold'`; unsupported weights fall back to the nearest one. [RN: Text Style Props](https://reactnative.dev/docs/text-style-props)
- `fontFamily` takes one name, not a CSS fallback list, and does not inherit through a `View`. Put it in the shared wrapper. [RN: Text](https://reactnative.dev/docs/text)
- **Common mistake:** `fontFamily: 'Helvetica, Arial, sans-serif'`; RN reads it as a single font name.

### 4. Numbers: tabular when they change or line up

`fontVariant` accepts `'small-caps'`, `'oldstyle-nums'`, `'lining-nums'`, `'tabular-nums'`, `'proportional-nums'`, as an array. [RN: Text Style Props](https://reactnative.dev/docs/text-style-props)

- Use `fontVariant: ['tabular-nums']` on prices, timers, counters, table columns and anything that updates live, so width does not jitter.
- Leave proportional figures for running prose.
- **Common mistake:** a live countdown in proportional digits that shifts neighbours every second.

### 5. Line height is in points, and text must not clip

`lineHeight` is a number, the distance between baselines. [RN: Text Style Props](https://reactnative.dev/docs/text-style-props) There is no unitless multiplier as in CSS.

- Copy Apple's leading per style (see the table in principle 2): body is 17 on 22, about 1.3 times the size. Tighter leading only where height is constrained, and never for three or more lines; looser for long wide columns. [HIG: Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
- `lineHeight` does not scale with `allowFontScaling` automatically in every case; verify visually at the largest size and update tokens if lines collide. <!-- UNVERIFIED: scaling behavior of lineHeight not stated on the docs page -->
- Android only: `includeFontPadding: false` removes extra ascender padding, and pairs with `textAlignVertical: 'center'`. [RN: Text Style Props](https://reactnative.dev/docs/text-style-props)
- **Common mistake:** `lineHeight: 1.5` (treated as 1.5 points, so lines overlap).

### 6. Truncate and wrap with props, not CSS

`numberOfLines` truncates after layout (`0` means unlimited). `ellipsizeMode` is `'tail'` (default), `'head'`, `'middle'` or `'clip'`; Android only supports `'tail'` when `numberOfLines > 1`. [RN: Text](https://reactnative.dev/docs/text)

- Titles and list rows: `numberOfLines={1}` or `2`. Paths, file names and emails: `ellipsizeMode="middle"`.
- Keep truncation to a minimum as text grows, and avoid truncating in scrollable regions unless a detail view shows the rest. [HIG: Typography](https://developer.apple.com/design/human-interface-guidelines/typography) Never truncate the only place content appears (error messages, totals); let it wrap.
- In a row, the `Text` needs `flexShrink: 1` to truncate, otherwise it never hits the limit (see `/sharqiewicz:rules-layout-mobile`).
- `lineBreakStrategyIOS` (iOS 14+) tunes wrapping for languages like Korean; default `'none'`. No `text-wrap: balance`, `word-break` or `overflow-wrap`.
- **Common mistake:** `numberOfLines` on a `Text` whose parent has no width constraint, so it never truncates.

### 7. `adjustsFontSizeToFit` shrinks text: use sparingly

It scales the font down to fit the box; `minimumFontScale` (0.01 to 1.0) sets the floor. [RN: Text](https://reactnative.dev/docs/text)

- Fine for a single short line in a fixed slot (a large amount, a score). Always set `numberOfLines={1}` and a sensible `minimumFontScale` (around 0.7).
- It fights Dynamic Type: users who enlarged text get it shrunk back. Do not use it for paragraphs or as a substitute for wrapping.
- **Common mistake:** `adjustsFontSizeToFit` on body copy, which cancels the user's setting.

### 8. Custom fonts: embed, one file per weight

Two routes: the `expo-font` config plugin embeds fonts at build time (dev build, not Expo Go), and `useFonts` loads at runtime and works everywhere but you must hold the splash screen until loaded. OTF and TTF are supported. [Expo: Fonts](https://docs.expo.dev/develop/user-interface/fonts/)

- Keep files in `assets/fonts`. Name files after the PostScript name; on Android (config plugin) the family is the filename without extension, on iOS it comes from the font file itself.
- Declare each weight as its own family or face, and avoid `fontWeight` tricks on a family with only one file. When several files share one family name via `useFonts`, declare every face with weight and style. A later `useFonts` call for an already-loaded name adds no faces. [Expo: Fonts](https://docs.expo.dev/develop/user-interface/fonts/)
- A custom font still scales (`allowFontScaling` applies), but check the ramp and line height.
- **Common mistake:** rendering before `useFonts` resolves, which flashes the fallback font.

### 9. Letter spacing

`letterSpacing` is a number in points (default 0). [RN: Text Style Props](https://reactnative.dev/docs/text-style-props)

- Leave it at 0 for body text in the system font; the system font tracks by size already.
- Add small positive spacing to all-caps labels (`textTransform: 'uppercase'`). Avoid tracking on long text.
- There is no `em` unit: convert to points from the font size.

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| `allowFontScaling={false}` on all text | Keep on; cap with `maxFontSizeMultiplier` where needed |
| Fixed `height` on buttons and rows | `minHeight` + padding |
| `lineHeight: 1.4` | Points: `lineHeight: 24` |
| `fontFamily: 'Inter, sans-serif'` | One name, loaded through `expo-font` |
| `rem`, `clamp()`, `text-wrap: balance` | Point sizes, tokens, `numberOfLines` |
| Live number in proportional digits | `fontVariant: ['tabular-nums']` |
| `fontFamily` on a parent `View` | Put it on `Text` via a wrapper |

---

## Review Checklist

- [ ] One shared `Text` wrapper or token set; no ad hoc sizes in screens
- [ ] `allowFontScaling` not disabled anywhere without a stated reason
- [ ] Each token has a matching `dynamicTypeRamp`
- [ ] Live or aligned numbers use `tabular-nums`
- [ ] Line heights are point values; no overlap at the largest size
- [ ] Truncated text can also be read in full somewhere
- [ ] `adjustsFontSizeToFit` only on single-line short text
- [ ] Custom fonts load before first render; every weight has a file

**NEVER:**
- Disable font scaling to protect a layout; change the layout.
- Write `lineHeight` as a unitless ratio, or sizes in `rem`/`em`.
- Put `fontFamily` fallback lists in a style.
- Use `adjustsFontSizeToFit` on multi-line body text.
- Set a fixed height on any container that holds text.
- Invent sizes: take point sizes and leading from the HIG table, and keep custom-font text at or above its 11pt minimum (larger for thin weights).

## Verify

- Set Settings, Accessibility, Display & Text Size, Larger Text to the maximum, then open every screen: nothing clips, overlaps or hides an action.
- Switch to the smallest size: hierarchy is still visible.
- Put a long string and a long number in every row: truncation and alignment hold.

Text is the user's setting first and your design second; build the layout so that it can grow.
