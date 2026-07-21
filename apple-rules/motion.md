# Motion

Fluid-interface craft (springs, velocity, interruptibility, momentum) plus the HIG accessibility rules for motion. The through-line: **an interface feels alive when motion starts from the current on-screen value, inherits the user's velocity, projects momentum forward, and can be grabbed and reversed at any instant.** Springs are the tool — inherently interruptible and velocity-aware. Rules read as build guidance and as review checks.

## Response — kill latency

- **Respond on pointer-down, not release.** Highlight the instant a control is pressed; waiting for `click` feels dead.
- Audit every latency (debounces, artificial timers, the ~300ms tap delay). Anything non-essential on the input path is a regression.
- **Feedback is continuous *during* the interaction**, not just at the end — a drag/slider/drawer updates 1:1 with the pointer the whole way.

```css
.button:active { transform: scale(0.97); transition: transform 100ms ease-out; }
```

## Direct manipulation — 1:1 tracking

- Dragged content stays glued to the finger and **respects the grab offset** (don't snap to center on grab).
- Use Pointer Events + `setPointerCapture` so tracking continues outside the element's bounds. Track a short **velocity/position history** (last few `pointermove` events) — you need release velocity.

## Interruptibility — the single most important principle

- **Never lock out input during a transition.** A moving element must be grabbable and reversible mid-flight; a closing modal the user grabs should follow the finger, not finish closing first.
- **Always animate from the presentation (current) value**, never the target — on interrupt, read the live on-screen transform and start there (avoids a jump).
- **Avoid CSS transitions/`@keyframes` for gesture-driven motion** — they can't be smoothly grabbed and reversed. Springs animate from the current value by default.
- **On reversal, blend velocity — don't hard-cut it** (a velocity discontinuity is a "brick wall"). Choose a spring library that re-targets from current velocity.
- **Decompose 2D motion into independent X and Y springs** — a single spring on a 2D distance desyncs when the axes have different velocities.

## Springs — behavior over prescribed animation

Think in Apple's two designer-friendly params (not mass/stiffness/damping):

- **Damping ratio** — overshoot. `1.0` = critically damped, smooth settle, no bounce. `<1.0` overshoots; lower = bouncier.
- **Response** — how quickly it reaches the target (seconds). Lower = snappier. Not a fixed "duration".

Defaults: start most UI at **damping `1.0`**; add bounce (**~`0.8`**) **only when the gesture carried momentum** (a flick/throw/drag release). Overshoot on a menu that just faded in feels wrong; on a flicked card it feels right.

| Interaction | Damping | Response |
| --- | --- | --- |
| Move / reposition | 1.0 | 0.4 |
| Rotation | 0.8 | 0.4 |
| Drawer / sheet | 0.8 | 0.3 |

Web (Motion / Framer Motion) — `bounce` + `duration` maps to Apple's damping + response:

```js
import { animate } from 'motion';
animate(el, { y: 0 }, { type: 'spring', bounce: 0, duration: 0.4 });        // critically damped default
animate(el, { y: t }, { type: 'spring', bounce: 0.2, duration: 0.4 });      // momentum — bounce only after a flick
```

## Velocity handoff & momentum projection

- **Continue at the finger's exact release velocity** — no seam between drag and animation. Pass release velocity as the spring's initial velocity (some APIs want it normalized: `gestureVelocity / (target − current)`; Motion takes raw px/s).
- **Project the resting position from velocity** (like scroll deceleration), then snap to the nearest target to that projection — this is what makes a flick "throw" the element.

```js
function project(v /* px/s */, decel = 0.998) { return (v / 1000) * decel / (1 - decel); }
const target = nearestSnapPoint(currentPosition + project(releaseVelocity));
// then hand off releaseVelocity to the spring
```

## Spatial consistency & hinting

- **Enter and exit along the same path** — a panel in from the right dismisses to the right. Mirror the easing on reversible transitions (inverse cubic-bézier).
- **Anchor to the source** — a menu/popover/sheet originates from its trigger (`transform-origin` on the trigger), not the screen center.
- **Hint in the direction of the gesture** — intermediate frames telegraph the outcome (Control Center modules "grow up and out toward your finger").
- **Rubber-band at boundaries** — resist progressively instead of a hard stop (a hard stop reads as frozen).

```js
function rubberband(overshoot, dim, c = 0.55) { return (overshoot * dim * c) / (dim + c * Math.abs(overshoot)); }
```

## Frame-level smoothness

- Keep per-frame positional change below the perception threshold to avoid strobing. Animate only compositor-friendly properties (`transform`, `opacity`); hint with `will-change`. `requestAnimationFrame` is the display-synced clock. Target a consistent **30–60fps**.
- For very fast motion, a subtle motion blur/stretch encodes speed better than a hard streak.

## Reduced motion & accessibility (HIG rules)

- **Motion is never the sole channel** for essential info — always a static/text/icon equivalent.
- **`prefers-reduced-motion: reduce`:** tighten springs (less bounce/overshoot), track directly with the gesture, **replace x/y/z positional transitions with fades**, avoid animating z-axis/depth and into/out of blur. Keep opacity/color changes that aid comprehension.
- Avoid full-viewport moving backgrounds and slow looping oscillation near **~0.2Hz** (one cycle / 5s — vestibular discomfort); keep amplitude low if unavoidable. Ease dark↔light theme changes rather than snapping brightness.
- **Keyboard-initiated state changes should feel instant** — don't animate them.

```css
@media (prefers-reduced-motion: reduce) { .sheet { transition: opacity 200ms ease; transform: none !important; } }
```

## Multimodal feedback (motion + sound + haptics)

1. **Causality** — trigger on the actual causal event (the toggle flipping, the item snapping home); match character to the action.
2. **Harmony** — visual, sound, and haptic fire on the **same frame**; latency destroys the illusion.
3. **Utility** — reserve haptics/sound for meaningful moments (success, error, commit, snap); over-feedback trains people to ignore all of it.
