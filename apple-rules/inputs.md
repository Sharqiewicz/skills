# Inputs

Gestures, keyboard, pointer/hover, focus & selection. Native-hardware inputs (Digital Crown, Apple Pencil, Action button, Camera Control, remotes, eye-tracking) are excluded — no web surface. Rules read as build guidance and as review checks.

## Gestures

- **Give more than one way to do anything** — never gate a task behind a single gesture; provide keyboard/pointer/voice equivalents.
- **Respond consistently with expectations** — don't remap tap/swipe to nonstandard actions; don't invent a custom gesture for a standard action (scroll, activate).
- Standard set: tap (activate), swipe (reveal/dismiss/scroll), drag (move), touch-and-hold (reveal more), double-tap (zoom), pinch (zoom), rotate.
- **Custom gestures** only for specialized, frequent tasks — must be discoverable, distinct, easy, and **never the sole way** to do something important.
- **Indicate when a gesture is unavailable** (disabled/visual cue) or people think the UI froze.

## Keyboard

- **Full keyboard access:** every window/menu/control reachable and activatable via keyboard alone — everything reachable via Tab/Enter/Space, **no keyboard traps**.
- **Respect standard shortcuts** — never repurpose ones people know: Cmd/Ctrl+Z (undo), +Shift+Z / +Y (redo), +F (find), +C/V/X, +A. Esc cancels/closes.
- Standard focus traversal: **Tab / Shift-Tab** forward/reverse; arrow keys within a composite widget; arrow+Shift extends selection.
- **Define custom shortcuts only for the most-used app-specific commands** — over-defining makes an app feel hard to learn. Modifier ordering convention: Control, Option/Alt, Shift, Command/Ctrl. Shortcuts auto-mirror for RTL.

## Pointing devices (mouse/trackpad)

- **Hit-slop padding:** ~12px around **bezeled** controls (filled buttons), ~24px around **icon-only/bezel-less** targets — roughly 2× the slop for glyph-only buttons.
- **Contiguous hit regions** for adjacent bar buttons — no dead zones where the pointer "reverts" between icons.
- Hover effect tiers: **highlight** (small transparent elements), **lift** (small opaque elements — scale + shadow together), **hover** (large elements — custom scale/tint/shadow). Don't add a shadow without scale (an unscaled element doesn't read as "closer").
- **Hover is additive, never a touch replacement** — never make an action reachable *only* on `:hover`; it must have a touch/keyboard equivalent. Gate hover-only enhancements behind `@media (hover: hover) and (pointer: fine)`.
- Avoid instructional text that a pointer/tooltip has to explain — fix the IA instead.

## Focus & selection

- **Focusing usually selects** — except when selecting would trigger a distracting context shift (opening a new view); then keep focus and activate separate (don't auto-navigate on focus, require Enter/click).
- **Rely on system/default focus effects** — a visible focus ring; only customize with real cause. **Ring for point-targets** (text/search fields), **full-row highlight** for list/collection rows.
- **Don't move focus without user interaction.** Exception: when a focused item disappears during keyboard navigation, move focus to a nearby remaining item; if focus context would be unpredictable, hide the indicator instead.
- **Focus/tab order = reading order** (leading→trailing, top→bottom; auto-mirrors in RTL) — keep DOM order logical so tab order follows.
- State vocabulary for a component's interaction matrix: unfocused / focused / highlighted-pressed / selected / unavailable.
