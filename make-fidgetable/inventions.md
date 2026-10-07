# Inventions

A growing library of fidget patterns. Each run of `/make-fidgetable` appends the new gate-passing patterns it invents.

Entry format:

### <Name>
- **Feel:** what it's like in the hand, in one line
- **Fits:** where it belongs, and its frequency tier
- **Web:** recipe
- **RN:** recipe
- **Reduce Motion:** fallback (when it isn't obvious)
- **Lenses:** F/E/I
- **Origin:** seed | <app — surface>

---

### Squish + Surprise
- **Feel:** squishes on every press, and on a random 3rd–5th press it does something extra. Rapid presses build a combo, and lifetime presses unlock new tricks.
- **Fits:** like/favorite, counters, add-to-cart, logo, mascot, refresh. Occasional to tens/day; haptic-only bonus at 100+/day.
- **Web:** `whileTap={{ scale: 0.92 }}` with `transition={{ type: "spring", stiffness: 500, damping: 15 }}`. Keep a press count and `next = 3 + Math.floor(Math.random() * 3)` in refs. On a hit, `animate(el, { scaleX: [1, 1.15, 0.95, 1], scaleY: [1, 0.85, 1.05, 1] }, { duration: 0.45 })` or `{ rotate: [0, -10, 8, 0] }`, then re-roll `next`.
- **RN:** `onPressIn` → `scale.value = withSpring(0.92, { duration: 150, dampingRatio: 0.6 })`, `onPressOut` → `withSpring(1, { duration: 300, dampingRatio: 0.5 })`. Press count and next interval in `useRef`. On a hit, `rotate.value = withSequence(withTiming(-10, { duration: 80 }), withTiming(8, { duration: 80 }), withSpring(0))` plus `Haptics.impactAsync(Heavy)`. Store the lifetime count in MMKV or AsyncStorage for milestone unlocks.
- **Reduce Motion:** no scale or rotation. The press gives an opacity dip, and the bonus becomes haptic-only.
- **Lenses:** 3/2/1. Lifetime unlocks raise Expansive; an unexpected bonus variant raises Inventive.
- **Origin:** seed

### Dial
- **Feel:** a value you spin rather than type, with a detent per step.
- **Fits:** steppers, quantity, time, and rating inputs. Tens/day.
- **Web:** `useDrag` → motion value, snap to integers, `animate(v, target, { type: "spring", velocity })` on release.
- **RN:** `Gesture.Pan()` → shared value, `withDecay({ velocity, clamp, rubberBandEffect: true })`, `selectionAsync()` on each integer crossing.
- **Lenses:** 3/0/2
- **Origin:** seed

### Worry Stone
- **Feel:** an idle object (logo, avatar, mascot) that squishes under the finger, follows a little, and springs back.
- **Fits:** headers, empty states, splash. Rare or idle.
- **Web:** pointer offset → `scaleX`/`scaleY` skew via motion values, `stiffness`-based spring back.
- **RN:** `Pan` + `Pinch` → transform shared values, `withSpring` to rest, `impactAsync(Light)` on release.
- **Lenses:** 3/1/2
- **Origin:** seed

### Patina
- **Feel:** controls that show wear where you use them most: a slightly warmer edge or a softer corner.
- **Fits:** the most-used actions. Any tier, because it's static.
- **Web:** a per-control use count in storage, mapped to a subtle CSS variable such as border tint or radius.
- **RN:** the same idea, with the count in MMKV or AsyncStorage feeding a style.
- **Lenses:** 0/3/3
- **Origin:** seed

### Trophy Tray
- **Feel:** finished things become small objects in a tray that you can shake and toss around.
- **Fits:** a history or archive screen. Occasional.
- **Web:** a 2D physics lib only if one is already installed; otherwise a simple velocity + wall-bounce loop on `requestAnimationFrame` with transforms.
- **RN:** Skia canvas or Reanimated `useFrameCallback`, with device-tilt gravity if a sensors lib exists.
- **Lenses:** 3/3/3
- **Origin:** seed

### Pull Tab
- **Feel:** pull a tab past a detent to reveal something, with resistance building until it gives.
- **Fits:** secondary reveals, receipts, details. Occasional.
- **Web:** drag with `dragElastic`, commit past a threshold, otherwise spring back.
- **RN:** `Pan` with a nonlinear resistance curve, `impactAsync(Medium)` at the give point.
- **Lenses:** 3/0/2
- **Origin:** seed

### Throwaway
- **Feel:** dismiss by flinging. The item lands where the velocity says it should, not at a fixed spot.
- **Fits:** toasts, cards, notifications. Occasional.
- **Web:** project the release velocity to a destination, then `animate` to it and remove.
- **RN:** `withDecay({ velocity })` past the threshold, otherwise `withSpring` home.
- **Lenses:** 2/0/1
- **Origin:** seed

### Riffle Stack
- **Feel:** a stack of cards that fans out on long press and riffles under a drag like a real deck.
- **Fits:** collections, saved items. Occasional.
- **Web:** a per-card rotation and offset derived from one drag motion value, staggered by index.
- **RN:** a `LongPress` + `Pan` composition with per-card `useAnimatedStyle` reading one shared value.
- **Lenses:** 3/1/2
- **Origin:** seed

### Tactile Calendar
- **Feel:** scrubbing through dates ticks once per day and thuds at each month boundary.
- **Fits:** date ranges, timelines. Tens/day, using haptics only.
- **Web:** no haptics, so use a 1px "notch" nudge at month boundaries instead.
- **RN:** `selectionAsync()` per day and `impactAsync(Medium)` per month, fired on crossings.
- **Lenses:** 2/0/2
- **Origin:** seed

### Evolving Overscroll
- **Feel:** pulling past the top reveals a small scene that changes over weeks of use.
- **Fits:** the top of the main screen. The scene only appears on overscroll, so it costs the 100+/day path nothing.
- **Web:** overscroll distance → reveal; the scene state is keyed off a stored count of overscrolls.
- **RN:** `onScroll` negative offset on the UI thread → reveal, with the scene stage stored locally.
- **Lenses:** 2/3/3
- **Origin:** seed
