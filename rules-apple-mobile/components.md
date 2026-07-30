# Components & Navigation (iOS · React Native)

iOS HIG components mapped to React Navigation / React Native / Expo, with current (RN 0.86 / latest Expo SDK) API names. Format: Apple rule → RN API → common mistake. **Prefer native-backed components over hand-rolled JS** — you get gestures, blur, haptics, safe-area, and VoiceOver for free.

## Navigation — `@react-navigation/native-stack`

Use **native-stack** (native `UINavigationController`), *not* `@react-navigation/stack` (JS-rendered — loses native swipe-back physics, large-title collapse, header blur; feels web-like).

- **Large titles** orient people; collapse to inline on scroll. → `headerLargeTitleEnabled: true` (⚠️ current name — not `headerLargeTitle`), `headerLargeTitleStyle`, `headerLargeTitleShadowVisible`. native-stack handles content-inset automatically.
- **Standard Back button** — chevron only, **never a text label saying "Back"**. → `headerBackTitle`, `headerBackButtonDisplayMode`, `headerBackButtonMenuEnabled` (iOS 14+ long-press history), `headerBackVisible`.
- **Edge-swipe-back is additive, never a replacement** for the Back button. → `gestureEnabled` (default `true`, iOS), `fullScreenGestureEnabled` (default `false` — swipe from anywhere, not just the edge), `animationMatchesGesture`.
- **Title concise (<15 chars); never the app's own name.** Header blur via `headerTransparent` + `headerBlurEffect`.
- *Mistakes:* using JS `stack` instead of `native-stack`; disabling `gestureEnabled` globally to paper over a conflict; custom "Back" text label.

## Tab bars — `@react-navigation/bottom-tabs` (or Expo Router **Native Tabs**)

- **Navigation between sections only — never actions** (a "+" tab that opens a modal violates this). **Persistently visible**; only a full modal may cover it.
- **≤5 tabs** (preserve continuity across sizes); avoid the auto **"More"** overflow tab (HIG says it hurts discoverability). **Always labeled** (single words). **Never disable/hide a tab** when its section is empty — show an empty state inside.
- → `tabBarLabel`, `tabBarIcon` ({focused,color,size}), `tabBarBadge`, `tabBarActiveTintColor`, `tabBarHideOnKeyboard`. For a truly native `UITabBar` + Liquid Glass, use **Expo Router Native Tabs** (`NativeTabs.Trigger.Icon/Label/Badge`, SDK 54+).
- **Badges** (red oval, number or "!") for critical/unread only — don't dilute.
- *Mistakes:* hand-rolled `View` tab bar (loses safe-area + blur + a11y); letting tab count creep past 5; a badge on every tab.

## Sheets & modals — native-stack `presentation`

- **Detents:** large (full) always; add **medium** (~half) for progressive disclosure on iPhone. Show a **grabber**. **Support swipe-to-dismiss** (confirm via an **action sheet** if there are unsaved changes). **One sheet at a time** — never chain sheet→sheet. Full-screen modal only for complex/prolonged flows (editing, camera) — it can't be swipe-dismissed.
- → `presentation: 'formSheet'` maps 1:1 to iOS detent sheets: `sheetAllowedDetents: ['medium','large']`, `sheetInitialDetentIndex`, `sheetGrabberVisible: true`, `sheetCornerRadius`, `sheetLargestUndimmedDetentIndex`. Other values: `modal`, `fullScreenModal`, `transparentModal`. **Define modal screens on the root stack**, not nested in tabs/drawers.
- For sheets with internal `FlatList`/keyboard/custom snap logic → **`@gorhom/bottom-sheet`** (`BottomSheetModal`, `snapPoints` = detents, `enablePanDownToClose`, built-in handle + `BottomSheetBackdrop`).
- *Mistakes:* plain RN `Modal` (no grabber/detents/native swipe) for what should be a sheet; `fullScreenModal` for a simple form (use swipe-dismissable `formSheet`); chaining sheets.

## Alerts & action sheets

**Alerts** — `Alert.alert(title, message, buttons)`:
- **≤3 buttons.** Default/most-likely on the trailing side (or top of a stack); Cancel leading (or bottom), titled exactly **"Cancel"**, never the default. Specific verbs ("Erase", "Keep"), not "OK" (OK only for purely informational). **Destructive style only when the outcome wasn't the user's deliberate intent** — not for an intentional "Empty Trash". Never on launch; use sparingly.
- → `AlertButton.style: 'default'|'cancel'|'destructive'` (iOS), `isPreferred` (iOS emphasis). `Alert.prompt()` (iOS) for quick text/secure entry.
- ⚠️ **Android hard-caps at 3 buttons** — self-impose ≤3 to stay cross-platform-safe.

**Action sheets** — `ActionSheetIOS.showActionSheetWithOptions(options, cb)`:
- Use (instead of an alert) when the user **deliberately triggered** a choice with **multiple related options** (e.g. discard draft → Delete / Save / Cancel). **Destructive option at the top**, styled red. Provide Cancel; the list must **never scroll**.
- → `cancelButtonIndex`, `destructiveButtonIndex`, `anchor` (iPad), `disabledButtonIndices`. Cross-platform: `@expo/react-native-action-sheet`.
- *Mistakes:* custom JS confirm dialog instead of `Alert` (loses native styling/VoiceOver/red convention); destructive styling on an already-intentional action; a 4-button iOS-only alert that breaks on Android.

## Selection & input

- **Toggle/Switch** — one on/off state, used **in a list row** (row text = its label); outside a list use a toggle button. → core `Switch` (`value`, `onValueChange`, `trackColor`, `ios_backgroundColor`). *Mistake:* a bare `Switch` with no row context; custom JS toggle when native gives haptics/tint/dark-mode free.
- **Slider** — min leading / max trailing; live feedback; pair with a field for wide/precise ranges; **never for volume**. → `@react-native-community/slider`.
- **Stepper** — shows no value itself; **always pair with a visible value field**. No core RN component — build with `Pressable` +/- around a `TextInput`/`Text` (`react-native-numeric-stepper`), add haptics. *Mistake:* a stepper with no adjacent value.
- **Text fields** — `TextInput`: correct `keyboardType` (`email-address`/`number-pad`/`decimal-pad`/`url`…); `secureTextEntry` for passwords (⚠️ **doesn't work with `multiline`**); `textContentType` for autofill (`'oneTimeCode'` for SMS 2FA, `'newPassword'`, `'username'`, `'emailAddress'`) — takes precedence over `autoComplete` on iOS, don't set conflicting values; **`clearButtonMode: 'while-editing'`** for the trailing Clear (×) — iOS defaults to `'never'`, the most-forgotten native affordance.
- **Pickers** — medium-to-long lists (short → pull-down; huge → searchable list); logical/alphabetized order; show in-context. → `@react-native-picker/picker`; dates via `@react-native-community/datetimepicker` (`mode: date|time|datetime|countdown`, `display: default|spinner|compact|inline` ≈ Apple's styles; `minuteInterval` must divide evenly into 60).
- **Segmented control** — switch **closely related subviews** (not top-level nav — that's a tab bar); **≤5** on iPhone; equal widths; all-text or all-icons, not mixed. → `@react-native-segmented-control/segmented-control` (`values`, `selectedIndex`, `momentary`). *Mistake:* using it as primary navigation.

## Lists & tables

- **Grouped/inset style** with section headers/footers to separate sections. **Disclosure chevron = navigation**; **info/detail-disclosure button = reveal more info** — don't conflate. Edit mode gates reordering/multi-select.
- → `SectionList` for grouped; **`@shopify/flash-list` (FlashList)** for anything large/complex (v2 auto-measures — `estimatedItemSize` etc. removed; ⚠️ **v2 requires the New Architecture/Fabric**). 
- **Swipe actions (swipe-to-delete)** → gesture-handler's **`ReanimatedSwipeable`** (`renderRightActions` receiving a progress SharedValue) — *not* hand-rolled `PanResponder`.
- **Pull-to-refresh** → `RefreshControl` on the list's `refreshControl` prop; ⚠️ `refreshing` is a **controlled prop** — flip it back to `false` in `onRefresh` or the spinner snaps away instantly.
- *Mistakes:* ignoring safe-area/`useSafeAreaInsets()` in list padding so content clips under the floating tab bar or notch; `FlatList` for big frequently-updated lists (blank-cell jank — use FlashList); FlashList v2 on old architecture (silently won't work).

## Context menus — `@react-native-menu/menu`

- Provide **either** a context menu **or** an edit menu, never both. Keep items few. **Hide unavailable items — don't dim.** **Destructive items at the end**, styled red. Mirror context-menu actions in the toolbar (and vice versa).
- → `MenuView` (native `UIMenu`): `actions` (`MenuAction` with `attributes: {destructive, disabled, hidden}`, nested `subactions`), `onPressAction`, `shouldOpenOnLongPress` (long-press = context menu; tap = pull-down).
- *Mistakes:* faking it with a `Modal` popup (loses the native squish/preview/haptic/VoiceOver); dimming instead of hiding; missing `attributes.destructive`.

## Search fields — native-stack `headerSearchBarOptions`

- Placement: nav bar (animates into a field above the keyboard), a search tab, toolbar, or inline. **Scope bars** filter by category, defaulting broad. Suggest recent (before typing) + predictive (while typing).
- → `headerSearchBarOptions`: `placeholder`, `hideWhenScrolling`, `onChangeText`, `onCancelButtonPress`, `placement`, ref for focus/blur/clear. No native scope-bar prop — put a segmented control directly beneath. Expo Router Native Tabs supports a dedicated search tab.
- *Mistake:* a custom `TextInput` in the header (loses the native collapse/expand + system Cancel).

## Progress & activity

- **Determinate whenever duration is knowable**; indeterminate spinner only when not. Keep it **moving** (stationary = frozen). Don't swap circular↔bar mid-flow. Specific status text ("Uploading 2 of 5"), not "Loading…". Offer Cancel/Pause when safe.
- → `ActivityIndicator` (`animating`, `size: 'small'|'large'`, `hidesWhenStopped`). Determinate bar: no maintained core component (`ProgressViewIOS` removed) — animate a `View` width with Reanimated or use `react-native-progress`.
- *Mistake:* reaching for the removed `ProgressViewIOS`; vague "Loading…" everywhere.

## Buttons — `Pressable`

- **≥44×44pt target** (`hitSlop` when the visual is smaller). **Visible press state is mandatory** — `style={({pressed}) => …}` opacity/scale; a button with no feedback reads as broken. Verb-first labels; SF Symbols for icon buttons.
- **Roles:** normal / primary (accent, one or two prominent per view max) / cancel / **destructive (red) — must never also be the primary/default**, to prevent confirm-by-habit data loss. RN has no role concept — apply this manually.
- *Mistakes:* sub-44pt icon-only targets; destructive action styled with the accent color; zero press feedback; >2 prominent buttons per screen.
