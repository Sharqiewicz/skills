# Gesture recipes (React Native, iOS)

Code shapes for the rules in [SKILL.md](SKILL.md). Hook API (Gesture Handler 3) first, builder mapping at the end. Tune every number on a device.

## Draggable that catches mid-flight, releases with velocity

```tsx
import { GestureDetector, usePanGesture } from 'react-native-gesture-handler';
import Animated, { useSharedValue, useAnimatedStyle, withDecay, cancelAnimation } from 'react-native-reanimated';

function Draggable({ minX, maxX }: { minX: number; maxX: number }) {
  const x = useSharedValue(0);

  const pan = usePanGesture({
    onBegin: () => { cancelAnimation(x); },          // catch it mid-animation
    onUpdate: (e) => { x.value += e.changeX; },      // accumulate: no jump on re-grab
    onDeactivate: (e) => {                           // skipped when never activated
      x.value = withDecay({ velocity: e.velocityX, clamp: [minX, maxX], rubberBandEffect: true });
    },
  });

  const style = useAnimatedStyle(() => ({ transform: [{ translateX: x.value }] }));
  return <GestureDetector gesture={pan}><Animated.View style={style} /></GestureDetector>;
}
```

`rubberBandEffect` needs `clamp`. Props: `velocity`, `deceleration`, `clamp`, `velocityFactor`, `rubberBandEffect`, `rubberBandFactor`, `reduceMotion`. [Reanimated: withDecay](https://docs.swmansion.com/react-native-reanimated/docs/animations/withDecay)

## Swipe to dismiss (distance or velocity), with a button twin

```tsx
const dismiss = usePanGesture({
  activeOffsetY: 12,                  // only a clear downward drag activates
  failOffsetX: [-20, 20],             // horizontal travel means "not mine"
  onBegin: () => { cancelAnimation(y); },
  onUpdate: (e) => { y.value = Math.max(0, y.value + e.changeY); },   // no upward travel
  onDeactivate: (e) => {
    const far = y.value > height / 3;
    const fast = e.velocityY > 600;   // heuristic
    if (far || fast) {
      y.value = withSpring(height, { velocity: e.velocityY, overshootClamping: true }, (done) => {
        if (done) scheduleOnRN(close);   // from react-native-worklets (Reanimated 3: runOnJS(close)())
      });
    } else {
      y.value = withSpring(0, { velocity: e.velocityY });
    }
  },
});
```

If the content scrolls, dismiss only while the scroll offset is at the top, and pass the `ScrollView` native gesture relation (`simultaneousWith` / `requireToFail` / `block`) rather than relying on render order. Always render a Close button too. [HIG: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)

## Snap points from projected end position

```tsx
const snaps = [0, -200, -500];
onDeactivate: (e) => {
  const projected = y.value + e.velocityY * 0.15;          // k is a tuning constant
  const target = snaps.reduce((a, b) => Math.abs(b - projected) < Math.abs(a - projected) ? b : a);
  y.value = withSpring(target, { velocity: e.velocityY });
}
```

For a real sheet use native `formSheet` detents first (see SKILL.md section 8).

## Haptic on crossing a threshold (once)

```tsx
const armed = useSharedValue(false);
onUpdate: (e) => {
  x.value += e.changeX;
  const past = Math.abs(x.value) > THRESHOLD;
  if (past !== armed.value) {
    armed.value = past;
    if (past) scheduleOnRN(() => Haptics.selectionAsync());
  }
}
```

## Simultaneous pinch + rotate; single vs double tap

```tsx
const both = useSimultaneousGestures(pinch, rotation);          // same component
const tap = useExclusiveGestures(doubleTap, singleTap);         // double tap has priority
const outer = useTapGesture({ simultaneousWith: innerTap });    // across components
```

`useCompetingGestures` = first to activate cancels the rest. [RNGH: Composition](https://docs.swmansion.com/react-native-gesture-handler/docs/composition/overview)

## Callback and relation mapping, Gesture Handler 2 to 3

| v2 builder | v3 hooks |
|---|---|
| `Gesture.Pan().minDistance(25)` | `usePanGesture({ minDistance: 25 })` |
| `Gesture.Tap/LongPress/Fling/Pinch/Rotation()` | `useTapGesture/useLongPressGesture/useFlingGesture/usePinchGesture/useRotationGesture` |
| `.onStart` / `.onEnd` | `onActivate` / `onDeactivate` |
| `.onChange` | folded into `onUpdate` (`changeX`, `changeY`) |
| `(e, success)` | `e.canceled` (inverted) |
| `Gesture.Simultaneous/Race/Exclusive` | `useSimultaneousGestures/useCompetingGestures/useExclusiveGestures` |
| `simultaneousWithExternalGesture` / `requireExternalGestureToFail` / `blocksExternalGesture` | `simultaneousWith` / `requireToFail` / `block` |

Hook and builder gestures cannot be related to each other. [RNGH: Upgrading to 3](https://docs.swmansion.com/react-native-gesture-handler/docs/guides/upgrading-to-3)

## Sheet detents

```tsx
<Stack.Screen name="Filters" options={{
  presentation: 'formSheet',
  sheetAllowedDetents: [0.4, 1],
  sheetGrabberVisible: true,
  sheetLargestUndimmedDetentIndex: 0,   // parent stays interactive at the small detent
}} />
```
[React Navigation: Native Stack](https://reactnavigation.org/docs/native-stack-navigator/)
