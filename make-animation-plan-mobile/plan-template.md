# Plan file template

Copy this structure for each `NN-short-slug.md`. Keep it under roughly 80 lines.

```markdown
# NN. <one-line title>

Disposition: Delete | Migrate | Tune | Add
Depends on: <plan numbers or "none">
Frequency tier: 100+/day | tens/day | occasional | rare
Purpose: feedback | spatial consistency | state indication | preventing a jarring change | explanation | delight

## Context (why this exists)
Two or three sentences. What is wrong today and what the user feels. No history, no blame.

## Files
- `path/to/Component.tsx:40-88`: what changes here
- `path/to/other.ts:12`: what changes here
Installed versions that matter: react-native-reanimated <x>, react-native-gesture-handler <y>, expo-haptics <z>.

## Current code
The smallest excerpt that shows the problem, with its file and line range.

## Target behaviour
Numbered, observable statements, each with exact values:
1. Property animated: `transform: [{ scale }]` (transform and opacity only).
2. Trigger and config: `withTiming(0.97, { duration: 120 })` on press-in; back to 1 with `withSpring(1, { duration: 300, dampingRatio: 1 })` on press-out.
3. Gesture hand-off (if any): capture the start value in `onBegin`; release with `withDecay({ velocity: e.velocityY, deceleration: 0.998, clamp: [min, max] })` or a duration-based `withSpring` seeded with `velocity`.
4. Interruption: new touch during the animation cancels it (`cancelAnimation(sv)`) and continues from the current value.
5. Haptic: `Haptics.<call>` fired on <causal event>, or "none, because <reason>".
6. Reduced motion: <exact behaviour, e.g. Reanimated `with*` defaults to System, so name only the gaps (core `Animated`, `LayoutAnimation`, Lottie) and any `ReduceMotion.Never`; drag still tracks the finger; the decorative part becomes a fade or is removed>.

## Steps
Ordered, mechanical. Each step is one edit an executor can do without judgment.

## Acceptance checks
- [ ] Observable check 1 (for example: dragging and releasing at speed carries the release velocity; no fixed-duration snap)
- [ ] Reduce Motion on (Settings > Accessibility > Motion): <what must be true>
- [ ] Reduce Motion off: <what must be true>
- [ ] No per-frame `setState`; no `scheduleOnRN` (Reanimated 4 + worklets) or `runOnJS` (Reanimated 3) in a gesture's per-frame callback
- [ ] Type check and lint pass
- [ ] Verified on a release build on a real iPhone, not only the simulator

## Out of scope
What the executor must not touch, including neighbouring animations that belong to other plans.
```
