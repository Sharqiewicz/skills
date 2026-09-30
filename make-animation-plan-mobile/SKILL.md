---
name: make-animation-plan-mobile
description: "Survey a React Native / Expo app's motion, audit it, and write self-contained plan files (one per change) that a cheaper model can execute without re-deriving context. Planning only, never edits app code. Run it on the most capable model. For web, use /improve-animations. Triggers on: plan animation fixes mobile, motion plan, animation audit plan, improve animations React Native, Expo motion cleanup plan, migrate Animated to Reanimated plan, reduce motion rollout plan, haptics rollout plan."
user-invocable: true
disable-model-invocation: true
argument-hint: [path, screen, or "whole app"]
---

Turn a React Native / Expo app's current motion into a set of small, self-contained plan files, so a cheaper model can execute each change without re-reading the codebase or re-deciding anything.

The expensive part is judgment: what is wrong, what the target is, what counts as done. This skill does that once, on the strongest model, and freezes it into files. Execution is mechanical.

## MANDATORY PREPARATION

1. Read `/sharqiewicz:review-animations-mobile` and `/sharqiewicz:rules-animation-performance-mobile` in full. They are the audit standard; this skill does not restate them.
2. Read `/sharqiewicz:rules-apple-mobile` (motion, haptics and accessibility sections) and skim `/animate-expo` so target code matches how the app's animations are built.
3. Confirm the scope with the user in one question if `$ARGUMENTS` is empty: whole app, one feature, or one screen.
4. Check whether the output directory already holds plans (default `.scratch/motion-plans/`). If it does, read them and continue the numbering instead of overwriting.

**CRITICAL**: This skill writes plan files only. Do not change application code, install packages, or run migrations. If the user wants implementation, hand the plan to `/animate-expo` or a cheaper model afterwards.

**IMPORTANT**: Opportunity-finding ("what should animate that doesn't") belongs to `/sharqiewicz:find-animations-mobile`. Run it when the user wants new motion, and turn its surviving rows into plans. Do not re-run its gate here.

---

## Survey the Motion

Build an inventory before judging anything. Record `file:line` for every hit.

| Question | Search for |
| --- | --- |
| Which animation stacks exist? | `from 'react-native-reanimated'`, `from 'react-native'` with `Animated`, `LayoutAnimation`, `PanResponder`, `lottie-react-native`, `@shopify/react-native-skia` |
| How are gestures built? | `react-native-gesture-handler`, `usePanGesture` (RNGH 3), `Gesture.Pan` (RNGH 2), `GestureDetector`, `PanResponder` |
| Which thread does each animation run on? | `useNativeDriver`, `scheduleOnRN`, `runOnJS`, `useAnimatedStyle`, `setState` inside a gesture callback |
| What is the config vocabulary? | `withSpring`, `withTiming`, `withDecay`, `Easing.`, `duration:`, `dampingRatio`, `stiffness` |
| Is reduced motion handled? | `ReduceMotion`, `reduceMotion:`, `useReducedMotion`, `isReduceMotionEnabled` |
| Are haptics used, and where? | `expo-haptics`, `impactAsync`, `selectionAsync`, `notificationAsync` |
| What does navigation own? | `native-stack`, `presentation`, `formSheet`, `animation:` screen options, JS `stack` navigator, `NativeTabs` |
| What is Lottie doing? | every `.json` Lottie import: illustration, or UI state? |

Also read `package.json` for the Reanimated, worklets, Gesture Handler and Expo SDK versions; plan code must match what is installed, not what is newest.

## Audit Against the Standards

Run each inventory entry through `/sharqiewicz:review-animations-mobile` and `/sharqiewicz:rules-animation-performance-mobile`. Every finding gets one of four dispositions:

- **Delete**: the app rebuilt something the platform owns (a JS bottom sheet, a hand-rolled push transition, a custom pull-to-refresh). Target is the native API, see [RN: Navigation](https://reactnative.dev/docs/navigation) and [Expo Router: Modals](https://docs.expo.dev/router/advanced/modals/).
- **Migrate**: right idea, wrong runtime (core `Animated`, `LayoutAnimation`, `PanResponder`, per-frame `setState`). Target is Reanimated shared values plus Gesture Handler on the UI thread.
- **Tune**: right runtime, wrong feel (fixed-duration snap after a flick, no velocity hand-off, a spring with both physics and duration params, animating `height` on a long list).
- **Add**: missing reduced-motion handling or a missing haptic. Cross-cutting items here become one plan each, not one per file.

Reduced motion is checked app-wide first. Reanimated animations default to following the system setting, but nothing in the docs says core `Animated`, `LayoutAnimation` or Lottie do, so treat them as unhandled unless the code checks `AccessibilityInfo.isReduceMotionEnabled()` itself. See [Reanimated: Accessibility](https://docs.swmansion.com/react-native-reanimated/docs/guides/accessibility/) and [RN: AccessibilityInfo](https://reactnative.dev/docs/accessibilityinfo).

## Write the Plans

One file per change, named `NN-short-slug.md` (two-digit order), in the output directory. Also write `00-index.md`: a table of plans with disposition, files touched, dependency on other plans, and a recommended execution order (cross-cutting and deletions first).

Use the structure in [plan-template.md](plan-template.md). The rule for every plan: the executor has never seen this repo. If it would need to open another file to know what to do, inline that information.

Sizing: one plan is one reviewable change, ideally one commit. Split by component, not by concern. A plan that touches more than about four files, or mixes Delete with Tune, gets split.

**IMPORTANT**: Target behaviour uses exact values: the API, the config object, the properties animated, the haptic type and the trigger event. "A snappy spring" is a defect in a plan. Take values from the app's existing vocabulary first, then from `/animate-expo`.

**CRITICAL**: Every plan that animates carries its reduced-motion behaviour and its haptic decision (including "no haptic, because..."). A plan without them is incomplete.

**NEVER:**
- Edit application code, `package.json`, or config while planning
- Write a plan that says "see the audit" or "as discussed"; each file stands alone
- Paste the whole component into a plan; include only the lines that change, with `file:line` anchors
- Specify an API or prop without checking it against the installed version's docs
- Propose motion for a surface the platform owns (native-stack push, sheet detents, tab switches, `RefreshControl`)
- Plan a JS-thread animation as the target; UI thread or nothing
- Put two behaviour changes in one plan
- Write acceptance checks that only say "looks good"; each is observable (a value, a log, a device behaviour)
- Skip the index, or leave plans unordered when one depends on another

## Verify the Plans

- [ ] Every finding from the audit is in a plan or explicitly listed as "left alone" with a reason in the index
- [ ] Each plan contains file paths, current code, target code or values, reduced-motion behaviour, haptic decision, and acceptance checks
- [ ] A reader with no repo access could execute each plan from the file alone
- [ ] Each plan names the device check: a release build on a real iPhone, with Reduce Motion on and off
- [ ] Dependencies and order are in `00-index.md`
- [ ] No application file was modified

Remember: a good plan leaves the cheaper model nothing to decide. Every judgment call is already made and written down.
