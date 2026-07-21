# Components

Per-component spec, each mapped to its web/ARIA equivalent, with when-to-use / when-*not* / labels / sizing / states / accessibility. Rules read as build guidance and as review checks. Current-state notes: **Navigation bars merged into Toolbars** (2025); the standalone **Badges** page was retired (folded into Tab bars / Notifications).

## Buttons — `<button>`

- Target ≥ 44×44px (60 in spatial). Always give a visible **pressed/active** state (`:active`), not hover-only.
- **One prominent (filled/accent) button per view** (two max). Mark the preferred choice by **style, not size**.
- Roles: Normal / Primary (responds to Enter) / Cancel / Destructive. **Never make a destructive action the visually dominant/primary button** — people click without reading.
- Prefer a short **verb-first label** ("Add to Cart") over an icon when text is clearer. Append "…" when the button opens another dialog/window for more input.
- **Loading:** swap label + inline spinner ("Checkout" → "Checking out…"), not a separate spinner-only state.
- A11y: label describes the action (not "click here"); icon-only buttons need `aria-label`; destructive actions get a confirming step.

## Menus — ARIA `menu`/`menuitem` (or `<select>`)

- Verb-phrase, title-case item labels, no articles ("View Settings"). Append "…" when more input is needed.
- **Dim unavailable items** rather than removing them (preserves spatial memory). Group related items; separate groups with dividers.
- Keep short: use a submenu once 3+ items share a term; cap ~5 items, **one nesting level** — avoid multi-level flyouts.
- Toggled items: prefer one label that changes ("Show Map"/"Hide Map") + checkmark for in-effect attributes. Icons all-or-none within a group.
- A11y: arrow-key nav + type-ahead + Esc; `aria-haspopup`/`aria-expanded` on trigger; roving tabindex.

## Pull-down vs. pop-up buttons

- **Pull-down** = a menu of **actions** related to the button ("More"/kebab, a Sort button). ≥3 items to justify the click; keep primary actions visible elsewhere; destructive items styled distinctly + confirm.
- **Pop-up** = a menu of **mutually exclusive states** (styled `<select>`/listbox). Label reflects current selection; always define a default; offer a trailing "Custom…" for rare values.

## Segmented controls — `role="radiogroup"` / `tablist`

- Mutually-exclusive set. **Cap ≤5–7 wide, ≤5 narrow/mobile**; equal segment widths; all-icons or all-text, never mixed.
- Don't mix action-segments and selection-segments. For switching **subviews** use segmented control; for top-level app **sections** use a tab bar.
- A11y: `radiogroup` + `aria-checked`, arrow-key nav.

## Toolbars (incl. former navigation bars) — app/header toolbar

- **Three zones:** leading (back/sidebar-toggle + title), center (contextual controls, collapse into overflow as width shrinks), trailing (search, one primary action, "More" overflow).
- **≤3 logical groups**; space icon-only from text-labeled buttons so they don't merge. Title concise (<~15 chars if tight); never title with just the app name.
- Icon-only from a recognized set; text only where an icon reads poorly ("Edit"). Let one auto overflow menu handle what doesn't fit — don't hand-roll a second one or design to overflow by default.
- A11y: `role="toolbar"`, arrow-key roving focus (APG toolbar pattern); icon-only need `aria-label`.

## Sheets — modal dialog / bottom sheet / side panel

- **Cancel/Close** (leading) dismisses without saving; **Done** (trailing) confirms. **Never show Cancel + Done + Back together** — at most two per step.
- Resizable via **detents** ("medium" ≈ half, "large" ≈ full) → snap points for progressive disclosure; show a **grabber** (drag handle, also a screen-reader resize affordance); support swipe/drag-to-dismiss.
- **One sheet at a time** — never a sheet from a sheet. For complex multistep flows use a full-screen modal or a dedicated route instead.
- Confirm before discarding unsaved changes.
- A11y: `role="dialog"` + `aria-modal="true"`, trap focus, restore focus to trigger on close, label via `aria-labelledby`.

## Popovers — floating anchored panel (Floating UI/Popper)

- Small amount of info/functionality; transient — dismisses on outside click. Arrow points at the trigger; don't cover the trigger or essential content.
- **One popover at a time**; never cascade. Nothing renders above a popover except an alert/toast.
- **Don't use a popover for a warning** (easy to miss/dismiss) — use an alert. In compact/narrow viewports, fall back to a sheet.
- Add an explicit Close/Done only to clarify save-vs-discard. A11y: focus management on open/close, Esc closes.

## Alerts — blocking `role="alertdialog"` (NOT a toast)

- Use **sparingly**, only for information that's both important AND actionable. **Never on page/app load.** Never for routine undoable deletes — only uncommon, non-undoable destructive actions.
- **Up to 3 buttons.** Title = short specific complete description (not "Error"), ≤2 lines. Button labels = 1–2 word specific verbs ("Erase", "Keep"); "OK" only for purely informational alerts.
- Destructive style **only when the outcome wasn't the user's deliberate intent**; always pair a destructive option with Cancel; Cancel is never the default-focused button.
- Default/primary on the trailing side (or top of a vertical stack); Cancel leading (or bottom). Esc dismisses.
- A11y: `aria-modal`, move focus in on open and restore on close.

## Action sheets — mobile bottom action-sheet / choice dialog

- Use (instead of an alert) when the **user deliberately triggered** the situation and there are multiple related choices (e.g. "Discard draft? Save / Delete / Cancel").
- **Destructive choice styled + placed at the top** (opposite of alerts). Cap ~4 buttons incl. Cancel on small screens; provide Cancel whenever data could be destroyed; the list must **never scroll** (too many options if it does).

## Activity / share views — Web Share API or custom panel

- Don't duplicate what the platform sheet already provides; give custom actions distinguishing titles (single verb). One consistent entry point; exclude irrelevant actions contextually.

## Toggles — switch / checkbox / radio

- Manages exactly **one on/off state** — don't overload with multi-option selection. **Never color-only** for state — pair with position/shape/checkmark.
- Switch (`role="switch"` + `aria-checked`) unlabeled only inside a list row where row text gives context; otherwise label it.
- **Checkboxes support indeterminate** (`aria-checked="mixed"`) for a "select all" over mixed children.
- **Radios** for mutually exclusive choices, **2–5** options (beyond ~5 use a pop-up/select). Never a lone radio — use a checkbox for a single on/off.

## Sliders — `<input type="range">` / `role="slider"`

- Min at leading/bottom, max at trailing/top. **Live feedback** as the value changes (no lag until release). Pair with a text field + stepper when the range is wide and exact values matter.
- Optional tick marks for discrete ranges; label min, max, and only necessary intermediates. Use a purpose-built widget for very common controls (e.g. volume).
- A11y: `aria-valuemin/max/now`, arrow keys + Page Up/Down.

## Steppers — `+/−` flanking a value

- **Always show the value** in an adjacent field/label (a bare stepper is a failure). Pair with a typable field for wide ranges; **Shift-click = ×10** step. A11y: `role="spinbutton"` or native `<input type="number">`.

## Text fields — `<input>`

- Persistent external **`<label>`** always (placeholder is a hint, not the label — it disappears on typing). Secure/masked for sensitive input; never prefill passwords.
- Size to expected input length; correct `inputmode`/`type` (email/url/numeric); trailing **Clear (×)** for search/filter. Validate at sensible moments (on blur for email; before submit for credentials).
- A11y: programmatically associate the label; never rely on placeholder as the accessible name.

## Text views — `<textarea>` / rich editor

- Only for long/rich/editable-at-length content (else a label or text field). Respect user font-size/zoom (`rem`). Make informational text (IDs, serials, errors) **selectable/copyable**.

## Pickers — `<select>` / combobox / date picker

- **Medium-to-long** value lists (short list → pull-down/pop-up; very large → searchable list). Predictable/logical order (alphabetized). Show **inline/in-context** (below the field or in a popover), not a separate screen.
- A11y: combobox/listbox pattern, `aria-expanded`/`aria-activedescendant`, full keyboard.

## Lists & tables — `<ul>`/`<table>` / data grid

- Lists/tables for **text-heavy, scannable** content; a grid for varied-size/image-heavy items. Clear selection feedback: persistent highlight for drill-down rows, transient highlight + checkmark for option-toggle rows.
- Distinguish an **info/detail-disclosure** (reveals info) from a **navigation chevron** (drills in). Multicolumn tables: descriptive `<th scope>` headers; desktop tables get sortable/resizable columns + row striping.
- A11y: `<th scope>`; custom grids use `role="grid"` + roving tabindex if interactive.

## Disclosure controls — `<details>`/`<summary>`

- Hide advanced/secondary content by default; keep most-used controls visible. **Descriptive label**, not a bare arrow. Limit to **one disclosure button per view**. A11y: `aria-expanded` (state not conveyed by icon rotation alone).

## Tab bars — bottom nav / primary tabs

- **Navigation between sections only** — never page-level actions. **Persistently visible** across sections; only a full modal may cover it. Never disable/hide a tab because its section is empty — show an empty state inside.
- **Always label** (single words) alongside icons; **≤5** tabs; treat the "More" overflow as something to avoid designing into.
- **Badges** (small red oval, number or "!") for genuinely critical/unread info only — never for unrelated numbers (scores, prices); clear when viewed; expose count via `aria-label` ("3 unread"), not a bare dot.
- A11y: `tablist`/`tab`/`tabpanel`, arrow-key nav, `aria-selected`.

## Sidebars — left nav rail

- Needs wide space — on narrow viewports collapse to a tab bar or off-canvas drawer. Cap directly-shown hierarchy at **2 levels** (deeper → split-view content list). Provide multiple discoverable show/hide affordances; **never hidden by default**.
- A11y: `nav` landmark + `aria-label`; current section via `aria-current="page"`.

## Search fields — `<input type="search">` + filter chips

- **Search as the user types**, not only on submit. Placeholder describes what's searchable; offer recent/suggested terms. **Scope bar** = filter tabs; **tokens** = filter chips (pair with suggestions so they're discoverable). Default to the broadest scope and let people narrow.

## Progress indicators — `<progress>` / spinner / skeleton

- **Determinate whenever duration is knowable** (lets people decide to wait/multitask/cancel); indeterminate only when it isn't. Switch indeterminate→determinate when duration becomes known, but **never switch shape** mid-flow.
- Keep the pace honest (don't crawl the last 10%) and **always moving** (a stationary bar reads as frozen). Avoid vague "Loading…" copy. Offer Cancel/Pause when interrupting is safe; confirm when it isn't.
- A11y: `role="progressbar"` + `aria-valuenow/min/max`, or `aria-busy` for indeterminate; announce completion via a live region.

## Boxes / gauges / image views (brief)

- **Boxes** (`<fieldset>`/`<section>`): noticeably smaller than the containing view; avoid nested boxes (use padding); short sentence-case title.
- **Gauges:** label the current value **and both range endpoints** (screen readers surface only visible labels). Gradient fill can reinforce meaning.
- **Image views** (`<img>`): if clickable, wrap in a real `<button>`/`<a>` — never a click-handler on a bare image; scrim/shadow behind text over images for contrast; SVG for glyphs.
