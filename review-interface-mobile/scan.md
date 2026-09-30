# Diagnostic scan commands

Run from the repo root with `rg` (ripgrep), or `grep -rnE` if unavailable. Restrict to the target with a trailing path list. All commands are read-only. Every hit is a candidate to confirm by reading the file.

```bash
T="src app components"        # replace with the resolved target paths
G='-g *.tsx -g *.ts -g *.jsx -g *.js'

# Hardcoded colors (hex, rgb/hsl literals) outside a theme file
rg -n $G '#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(' $T --glob '!**/theme*' --glob '!**/colors*'

# Non-RN color functions
rg -n $G 'oklch\(|lab\(|lch\(|color\(' $T

# Legacy touchables
rg -n $G 'TouchableOpacity|TouchableHighlight|TouchableWithoutFeedback|TouchableNativeFeedback' $T

# Pressables: list, then read each for an icon-only child and a label
rg -n $G -A6 '<(Pressable|TouchableOpacity)\b' $T
rg -n $G 'accessibilityLabel|aria-label|accessibilityRole|role=' $T

# Font scaling off or pinned line heights
rg -n $G 'allowFontScaling=\{false\}|maxFontSizeMultiplier|lineHeight:' $T
rg -n $G 'fontSize:' $T

# Static window metrics
rg -n $G 'Dimensions\.get\(' $T
rg -n $G 'useWindowDimensions' $T

# Safe area handling (absence is the signal: check each screen file)
rg -L 'useSafeAreaInsets|SafeAreaView|contentInsetAdjustmentBehavior|headerTransparent|edges=' $T --glob '*Screen*.tsx' --glob 'app/**/*.tsx'
rg -n $G 'paddingTop: *(20|44|47|50|54|59)\b|marginTop: *(44|47|54|59)\b' $T

# Web idioms
rg -n $G 'hover|onMouseEnter|onMouseLeave|cursor:|outline|:focus|\brem\b|\b[0-9.]+(vh|vw|rem|em)\b|@media|env\(safe-area|<div|<span|className=|position: *.fixed.|transition:|will-change|IntersectionObserver' $T

# Motion and threading
rg -n $G 'PanResponder|LayoutAnimation|Animated\.(timing|spring|loop|Value)|runOnJS|scheduleOnRN' $T
rg -n $G 'withTiming|withSpring|withDecay|withRepeat|entering=|exiting=|useAnimatedStyle' $T
rg -n $G 'reduceMotion|useReducedMotion|isReduceMotionEnabled|ReducedMotionConfig' $T
rg -n $G 'autoPlay|loop\b|LottieView|useVideoPlayer|\.play\(\)' $T
rg -n $G 'animat\w*\(.*(width|height|top|left|margin|padding)' $T

# Gestures
rg -n $G 'GestureDetector|usePanGesture|Gesture\.Pan|activeOffset|failOffset|simultaneousWith|GestureHandlerRootView' $T

# Touch target hints
rg -n $G '(width|height|minWidth|minHeight): *(1[0-9]|2[0-9]|3[0-9]|40)\b' $T
rg -n $G 'hitSlop' $T

# Haptics
rg -n $G 'expo-haptics|Haptics\.' $T
```

How to read the output:
- An absent signal is only a finding when the file should have it (a screen with no safe-area handling, Lottie or core `Animated` with no Reduce Motion check).
- For the `-L` (files without a match) command, inspect each listed file before reporting.
- Theme and token files legitimately contain hex values; report colors only where they are consumed in components.
- `fontSize:` hits are not findings by themselves; look for fixed heights or `numberOfLines` next to them and for `allowFontScaling={false}`.
