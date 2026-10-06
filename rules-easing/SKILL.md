---
name: rules-easing
description: "Reference for easing curves: the 18 Penner cubic-bezier tokens (quad, cubic, quart, quint, expo, circ × in, out, in-out) as CSS custom properties, which family to pick for enter, exit, move and hover, and the same curves as Reanimated `Easing.bezier` for React Native. Triggers on: easing, ease curve, cubic-bezier, timing function, transition-timing-function, ease-out, ease-in, ease-in-out, quad, cubic, quart, quint, expo, circ, Easing.bezier, withTiming easing, motion tokens."
user-invocable: true
---

Use these curves instead of the built-in `ease`, `ease-in`, `ease-out` and `ease-in-out` keywords, which are too weak for deliberate motion.

## Tokens

Paste into the root stylesheet once. Reference by name. Never inline a raw `cubic-bezier(...)` in a component.

```css
:root {
  --ease-in-quad: cubic-bezier(.55, .085, .68, .53);
  --ease-in-cubic: cubic-bezier(.550, .055, .675, .19);
  --ease-in-quart: cubic-bezier(.895, .03, .685, .22);
  --ease-in-quint: cubic-bezier(.755, .05, .855, .06);
  --ease-in-expo: cubic-bezier(.95, .05, .795, .035);
  --ease-in-circ: cubic-bezier(.6, .04, .98, .335);

  --ease-out-quad: cubic-bezier(.25, .46, .45, .94);
  --ease-out-cubic: cubic-bezier(.215, .61, .355, 1);
  --ease-out-quart: cubic-bezier(.165, .84, .44, 1);
  --ease-out-quint: cubic-bezier(.23, 1, .32, 1);
  --ease-out-expo: cubic-bezier(.19, 1, .22, 1);
  --ease-out-circ: cubic-bezier(.075, .82, .165, 1);

  --ease-in-out-quad: cubic-bezier(.455, .03, .515, .955);
  --ease-in-out-cubic: cubic-bezier(.645, .045, .355, 1);
  --ease-in-out-quart: cubic-bezier(.77, 0, .175, 1);
  --ease-in-out-quint: cubic-bezier(.86, 0, .07, 1);
  --ease-in-out-expo: cubic-bezier(1, 0, 0, 1);
  --ease-in-out-circ: cubic-bezier(.785, .135, .15, .86);
}
```

Tailwind v4: put the same values in `@theme` as `--ease-out-quint: ...` and use `ease-out-quint` as a class.

## Picking a curve

The direction (in, out, in-out) matters more than the strength.

| Motion | Direction | Default token |
|---|---|---|
| Element enters, opens, reveals, responds to a press or hover | out | `--ease-out-quint` |
| Element leaves the screen for good | in | `--ease-in-cubic` |
| Element moves or morphs between two on-screen positions | in-out | `--ease-in-out-cubic` |
| Pure rotation (not a spinner) | in-out | `--ease-in-out-quad` |
| Spinners, marquees, progress tied to time | none | `linear` |

- **Default to ease-out.** It starts fast, so the UI feels like it reacts at once. Most UI motion is ease-out.
- **Avoid ease-in for anything the user triggered.** The slow start reads as lag. Keep it for exits, and keep exits shorter than entrances.
- **Strength scales with duration.** Order from gentle to steep: quad, cubic, quart, quint, expo. `circ` sits near quart and has a sharper knee.
  - Up to 200ms (press, hover, small toggles): quad or cubic.
  - 200–400ms (menus, popovers, cards): quart or quint.
  - Above 400ms (page reveals, large panels): quint or expo. A steep curve covers most of the distance early, so a long duration does not feel slow.
- **`--ease-in-out-expo` is extreme** (`1, 0, 0, 1`): near-frozen at both ends, a snap in the middle. Use it only on purpose.
- **Use a spring instead of a curve** when the motion is interruptible or driven by a gesture (drag, swipe, sheet). A curve restarts from zero velocity when it is interrupted.

## React Native (Reanimated)

RN has no CSS strings. Pass the same four numbers to `Easing.bezier`. Keep them in one module:

```ts
import { Easing } from 'react-native-reanimated';

export const ease = {
  inQuad: Easing.bezier(0.55, 0.085, 0.68, 0.53),
  inCubic: Easing.bezier(0.55, 0.055, 0.675, 0.19),
  inQuart: Easing.bezier(0.895, 0.03, 0.685, 0.22),
  inQuint: Easing.bezier(0.755, 0.05, 0.855, 0.06),
  inExpo: Easing.bezier(0.95, 0.05, 0.795, 0.035),
  inCirc: Easing.bezier(0.6, 0.04, 0.98, 0.335),

  outQuad: Easing.bezier(0.25, 0.46, 0.45, 0.94),
  outCubic: Easing.bezier(0.215, 0.61, 0.355, 1),
  outQuart: Easing.bezier(0.165, 0.84, 0.44, 1),
  outQuint: Easing.bezier(0.23, 1, 0.32, 1),
  outExpo: Easing.bezier(0.19, 1, 0.22, 1),
  outCirc: Easing.bezier(0.075, 0.82, 0.165, 1),

  inOutQuad: Easing.bezier(0.455, 0.03, 0.515, 0.955),
  inOutCubic: Easing.bezier(0.645, 0.045, 0.355, 1),
  inOutQuart: Easing.bezier(0.77, 0, 0.175, 1),
  inOutQuint: Easing.bezier(0.86, 0, 0.07, 1),
  inOutExpo: Easing.bezier(1, 0, 0, 1),
  inOutCirc: Easing.bezier(0.785, 0.135, 0.15, 0.86),
} as const;

// withTiming(1, { duration: 280, easing: ease.outQuint })
```

The picking rules above apply unchanged. On mobile, prefer `withSpring` for anything the finger touches (see `/sharqiewicz:rules-gestures-mobile`).

## Review checks

- A raw `cubic-bezier(...)` or `Easing.bezier(...)` inside a component instead of a token.
- `ease-in` (keyword or token) on an entrance, hover or press.
- A built-in keyword (`ease`, `ease-out`) on deliberate motion above 200ms.
- A long duration (above 400ms) on a gentle curve (quad), which feels sluggish.
- A curve on drag, swipe or another interruptible motion that should be a spring.
