---
name: make-motion-brief-mobile
description: "Decide an animation before building it, for a React Native / Expo iOS app. Runs a one-question-at-a-time interview (each question with a recommended answer), then writes a short brief: a verdict (build, or don't build because iOS already does it or it shouldn't animate) plus exact Reanimated config, gesture hand-off, haptic pairing and reduced-motion fallback. For web, use /motion-brief. Triggers on: motion brief mobile, should this animate, decide animation React Native, spec an animation, animation spec Expo, spring or timing, haptic pairing, design a gesture, plan an interaction, is there a native way."
user-invocable: true
disable-model-invocation: true
argument-hint: [the interaction to decide, e.g. "swipe to dismiss card"]
---

Decide what an interaction should do, and whether it should animate at all, before any code exists. The output is a short brief that `/animate-expo` (or a person) can build from without guessing.

On iOS the first answer is often "the platform already does this." A brief that ends in "don't build" is a successful brief.

## MANDATORY PREPARATION

1. Read `/sharqiewicz:rules-apple-mobile` (interactions and components files) for what the system owns, and skim `/animate-expo` for the tools available.
2. Look at the code around the interaction: the screen, the navigator it lives in, and any existing spring/timing configs (`grep -rn "withSpring\|withTiming\|withDecay"`). The brief reuses the app's vocabulary.
3. Check which libraries are installed (`react-native-reanimated`, `react-native-gesture-handler`, `expo-haptics`, `expo-router`) so the brief names only what exists.
4. Restate the interaction in one sentence and confirm it with the user.

**CRITICAL**: Ask one question per message. Give a recommended answer with each, and a one-line reason, so the user can reply "yes". Wait for the reply before the next question. Never batch the interview.

**IMPORTANT**: If the codebase can answer a question, read it instead of asking.

---

## The Interview

Ask in this order. Stop early when a question produces a "don't build" verdict.

1. **Trigger.** What starts it: a tap, a gesture (which one), a state change, or navigation? Recommend the narrowest true answer.
2. **Does the platform already do this?** Check before designing anything:
   - screen push/pop, edge-swipe back: native stack, see [Expo Router: Stack](https://docs.expo.dev/router/advanced/stack/)
   - a bottom sheet that is its own screen: `presentation: 'formSheet'` with `sheetAllowedDetents`, see [Expo Router: Modals](https://docs.expo.dev/router/advanced/modals/)
   - a long-press menu or peek: `Link.Menu` / `Link.Preview`, see [Expo Router: Link preview](https://docs.expo.dev/router/advanced/apple-link-preview/)
   - a collapsing header: `headerLargeTitleEnabled`
   - pull to refresh, alerts, action sheets, keyboard movement: `RefreshControl`, `Alert`, `ActionSheetIOS`, system keyboard behaviour
   If yes, the verdict is **don't build**. Write the brief with the native API to use and stop.
3. **Frequency.** How often will one person see it per day? Recommend a tier. Per [HIG: Motion](https://developer.apple.com/design/human-interface-guidelines/motion), avoid adding motion to frequent interactions because the system already animates standard elements. Very frequent means no animation, or near-imperceptible.
4. **Purpose.** Name one: feedback, spatial consistency, state indication, preventing a jarring change, explanation, or delight (rare moments only). No purpose means don't build.
5. **What animates.** `transform` and `opacity` only; they avoid layout recalculation, see [Reanimated: Performance](https://docs.swmansion.com/react-native-reanimated/docs/guides/performance/). If the natural idea animates `height`, `width` or `top`, propose a transform or opacity alternative, or accept the cost explicitly for a single short-lived view.
6. **Anchor.** Where does it originate and return to? Motion should come from its trigger and leave the way it came (HIG: a view revealed by sliding down should not be dismissed sideways). RN has a `transformOrigin` style prop (`'left top'`, `'10px 2px'`, or an array), not a CSS `transform-origin` property name; see [RN: Transforms](https://reactnative.dev/docs/transforms). Check it is supported by the app's RN version before relying on it.
7. **Spring or timing.** Recommend by rule:
   - driven by a finger or needs to be interruptible: a spring (`withSpring`); config rules live in `/sharqiewicz:rules-gestures-mobile`. Never mix `stiffness`/`damping` with `duration`/`dampingRatio`.
   - fixed, non-interactive, short (fade, press scale): [`withTiming`](https://docs.swmansion.com/react-native-reanimated/docs/animations/withTiming/) with `duration` and `Easing.bezier(x1, y1, x2, y2)`. CSS `cubic-bezier(...)` strings do not exist in RN.
   - momentum after release: `withDecay`; see `/sharqiewicz:rules-gestures-mobile` for `velocity`, `deceleration` and `clamp`.
   Then write the exact config object. Brevity matters: HIG asks for brief, precise feedback animations.
8. **Gesture hand-off and velocity** (skip if no gesture). Which pan constraints (`usePanGesture` in RNGH 3, `Gesture.Pan()` in RNGH 2; match the installed version) (`activeOffsetX/Y`, `failOffsetX/Y`) keep it from fighting scroll views and edge-swipe back? Capture the start value on begin, add the translation, and pass `event.velocityX` or `velocityY` into the release animation, see [Reanimated: Handling gestures](https://docs.swmansion.com/react-native-reanimated/docs/fundamentals/handling-gestures/). Name the dismiss threshold (distance and velocity) in points.
9. **Interruption.** What if the user touches it mid-animation, or the state flips again? Recommend: the new input cancels the running animation ([`cancelAnimation`](https://docs.swmansion.com/react-native-reanimated/docs/core/cancelAnimation/)) and continues from the current value. HIG: don't make people wait for an animation to finish.
10. **Haptic pairing.** Recommend one [expo-haptics](https://docs.expo.dev/versions/latest/sdk/haptics/) call or none:
    - `selectionAsync()`: a selection changes (segment, picker tick)
    - `impactAsync(ImpactFeedbackStyle.Light | Medium | Heavy | Soft | Rigid)`: a physical collision or snap; match intensity to the motion's weight
    - `notificationAsync(NotificationFeedbackType.Success | Warning | Error)`: the outcome of a task
    Fire on the causal event (the snap, the commit), never every frame of a drag. Keep meanings consistent across the app ([HIG: Playing haptics](https://developer.apple.com/design/human-interface-guidelines/playing-haptics)). Haptics are silent in Low Power Mode and when the user disabled the Taptic Engine, so the interaction must read without them; offer an in-app toggle if haptics are frequent.
11. **Reduced motion.** Apple's guidance for Reduce Motion: tighten springs, track gestures directly, and replace x/y/z travel with fades ([HIG: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)). In Reanimated, `with*` calls default to `ReduceMotion.System`, so state only deviations (`Never`, or motion to replace rather than disable) and any non-Reanimated motion; note the docs say a completed-instantly animation snaps to its end value, so the end state must be correct on its own ([Reanimated: Accessibility](https://docs.swmansion.com/react-native-reanimated/docs/guides/accessibility/)). State what the fallback looks like: a fade, or an instant change. Anything essential must not depend on motion alone.

## Write the Brief

Write to the path the user gives, or `.scratch/motion-briefs/<slug>.md`. Keep it to one screen of text.

```markdown
# <interaction>
Verdict: Build | Don't build (<native API to use instead>) | Don't animate (<reason>)
Frequency: <tier>   Purpose: <one word>
Trigger: ...
Animates: <property list>   Anchor: ...
Motion: <API + exact config>
Gesture: <constraints, hand-off, thresholds>   (or "none")
Interruption: ...
Haptic: <exact call + event>   (or "none, because ...")
Reduced motion: <exact fallback>
Build with: /animate-expo
```

**NEVER:**
- Ask more than one question per message, or ask without a recommended answer
- Skip question 2: designing custom motion for something native-stack, `formSheet`, `Link.Menu` or `RefreshControl` already does is the most common waste
- Write a value as "a quick spring" or "subtle"; give the config or leave the field as an open question
- Specify `Animated`, `LayoutAnimation` or `PanResponder` as the implementation
- Recommend haptics inside per-frame callbacks, or one haptic meaning different things in different places
- Leave the reduced-motion field blank, or write "respects system setting" without the concrete fallback
- Write or edit app code; the brief ends at `/animate-expo`

## Verify the Brief

- [ ] Verdict stated first, and consistent with the answers
- [ ] A "don't build" verdict names the native API that replaces it
- [ ] Every spring/timing/decay value is an exact config using one parameter family
- [ ] Gesture fields name thresholds in points and the velocity hand-off
- [ ] Haptic is one named call tied to one event, or explicitly none
- [ ] Reduced-motion fallback is concrete
- [ ] Only APIs present in the project's installed libraries are named

Remember: the cheapest animation is the one the platform already ships, and the second cheapest is the one you decided not to build.
