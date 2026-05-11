---
name: z-index-doctor
description: "Diagnostic decision tree for analyzing and fixing z-index, stacking context, and overlay problems in CSS. Use when an element renders behind something it shouldn't, when z-index values aren't taking effect, when modals/popovers/toasts overlap incorrectly, or when an element is mysteriously trapped by a parent. Triggers on: z-index, stacking context, stacking order, paint order, modal behind sidebar, toast behind backdrop, dialog, showModal, popover API, top layer, ::backdrop, transform breaks z-index, opacity stacking, position fixed not on top, overlay z-index, z-index 9999, z-index not working, element trapped, popover trapped, isolation isolate, mix-blend-mode, filter stacking, contain paint."
user-invocable: true
argument-hint: "[describe the symptom — e.g. 'modal renders behind sidebar']"
---

Diagnose any z-index or layering bug by walking the decision tree below — almost every "z-index doesn't work" issue traces to one of five root causes encoded here.

## MANDATORY PREPARATION

1. Read the symptom the user described. If they haven't named one, ask: **"What element should be on top, what is actually on top, and where in the DOM does each one live?"**
2. Inspect the failing element's ancestor chain in DevTools. Note every ancestor with: `transform`, `filter`, `opacity < 1`, `position: fixed`, `position: sticky`, `mix-blend-mode`, `clip-path`, `mask`, `contain: paint`, `container-type`, `isolation: isolate`, or `z-index` other than `auto` on a positioned/flex/grid element.
3. Note the `position` value of the failing element itself — `z-index` does nothing on a `position: static` element that isn't a flex/grid child.
4. Identify whether the element should escape its document context (modal, toast, tooltip) or just stack locally.
5. Do not propose `z-index: 9999` or any escalation of an existing number. That's the symptom, not the fix.

---

## Quick Reference

| Symptom | Root Cause | Section |
|---------|-----------|---------|
| `z-index: 9999` ignored, sibling with `z-index: 10` wins | Element is trapped in a parent's stacking context | [Stacking Context Trap](#stacking-context-trap) |
| `z-index` does nothing | Element is `position: static` (and not a flex/grid child) | [Positioning Rule](#positioning-rule) |
| Modal renders behind something with `transform` | Same trap — `transform` creates a stacking context | [Stacking Context Trap](#stacking-context-trap) |
| Toast hidden behind dialog's `::backdrop` | Toast is in document flow; `::backdrop` paints from inside the top layer | [Top Layer Stack](#top-layer-stack) |
| Changed `z-index: auto` → `z-index: 0`, layout breaks | `0` creates a stacking context, `auto` doesn't | [The `auto` vs `0` Gotcha](#auto-vs-0) |
| Need overlay above everything regardless of ancestors | Use the top layer (`<dialog>` or `popover`) | [Top Layer Escape](#top-layer-escape) |

---

## Core Principles

### 1. `z-index` Is Local, Not Global

`z-index` only compares elements within the **same stacking context**. A child at `z-index: 9999` always loses to a sibling context at a higher level — no number wins across contexts.

Mental model: **version numbers**. Parent context = major version. Child `z-index` = minor version. `3.9999` < `5.0`, always.

### 2. Source Order Is the Baseline

Without positioning or z-index, **later DOM elements paint over earlier ones**. Positioned elements (`relative`, `absolute`, `fixed`, `sticky`) always paint above non-positioned ones regardless of DOM order. Everything else builds on this.

### 3. `z-index` Requires Positioning

`z-index` is ignored on `position: static` elements unless they are flex or grid children. If `z-index` "does nothing," check `position` first.

### 4. Dozens of Properties Create Stacking Contexts

Not just `position` + `z-index`. Also: `transform`, `filter`, `opacity < 1`, `mix-blend-mode`, `clip-path`, `mask`, `contain: paint`, `container-type`, `will-change`, `isolation: isolate`, `position: fixed/sticky` (always), and flex/grid children with any non-`auto` `z-index`. Any of these on an ancestor can trap a descendant.

### 5. The Top Layer Is the Only Real Escape

`<dialog>.showModal()` and `popover` promote an element into the **top layer** — a stack above all stacking contexts. It is the only mechanism that genuinely escapes a trap without restructuring the DOM.

### 6. Top Layer Is an Ordered Set

Last promoted = on top. If you need a toast above a modal's `::backdrop`, promote the toast to the top layer **after** the modal opens.

---

## Decision Flowchart

**CRITICAL**: Run the failing element through this tree before changing any number. Increasing `z-index` without identifying the root cause hides the bug — it doesn't fix it.

```
Is the element on the right layer?

Does z-index seem to have NO effect at all?
├── Yes → Is the element position: static and NOT a flex/grid child?
│   ├── Yes → Add position: relative (or absolute/fixed) → fixed
│   └── No → Check if the value is z-index: auto (treated as 0 without creating a context)
│
└── No, z-index "works" but the element is still behind something

    Should this element escape ALL ancestor contexts?
    (modal, global toast, tooltip pinned to viewport, command palette)
    ├── Yes → Use the TOP LAYER
    │   ├── Needs backdrop + focus trap + modal semantics → <dialog>.showModal()
    │   ├── Lightweight overlay, click-outside to dismiss   → popover="auto"
    │   ├── Must stay open regardless of outside clicks     → popover="manual"
    │   └── Already using top layer, still hidden behind ::backdrop?
    │       → Promote the hidden element to top layer AFTER the dialog
    │         (last promoted = on top)
    │
    └── No, this is local layering inside a component
        │
        Is the element trapped by a parent's stacking context?
        ├── Yes → Find the trapping ancestor (transform / opacity<1 / filter /
        │         fixed / sticky / mix-blend-mode / clip-path / mask /
        │         contain: paint / container-type)
        │   ├── Can you remove the trap-creating property? → Remove it
        │   ├── Can you raise the WHOLE trapping ancestor in its context?
        │   │   → Raise the ancestor (use the version-number model)
        │   └── Neither possible? → Promote to top layer (popover) or portal to <body>
        │
        └── No trap — just normal local stacking
            → Use a small, documented z-index scale (e.g. 10/20/30/40)
              Add `isolation: isolate` on the component root to prevent
              future ancestors from leaking through.
```

---

<a id="stacking-context-trap"></a>
### Resolving a Stacking Context Trap

1. Walk the failing element's ancestors. The first ancestor with a context-creating property is the trap.
2. Decide:
   - **Remove the property** if it's not load-bearing (often a stray `transform` or `will-change`).
   - **Raise the trapping ancestor** in its own context (version-number model).
   - **Escape via top layer** if the element is logically a global overlay.
3. Do not add more `z-index` to the trapped child — it cannot win.

<a id="positioning-rule"></a>
### Positioning Rule

`z-index` applies to:
- Positioned elements (`relative`, `absolute`, `fixed`, `sticky`)
- Flex children and grid children (regardless of `position`)

On a plain `position: static` non-flex/grid element, `z-index` is ignored entirely.

<a id="top-layer-escape"></a>
### Top Layer Escape Hatch

| API | Top Layer? | Backdrop | Focus Trap | Use For |
|-----|-----------|----------|------------|---------|
| `dialog.show()` | No | No | No | Non-modal dialog in document flow |
| `dialog.showModal()` | Yes | Yes (`::backdrop`) | Yes | Modal dialogs |
| `popover="auto"` | Yes | No | No | Menus, dropdowns, tooltips (light dismiss) |
| `popover="manual"` | Yes | No | No | Toasts, persistent overlays |
| `popover="hint"` | Yes | No | No | Hover tooltips (closes others of same type) |

<a id="top-layer-stack"></a>
### Top Layer Stack Ordering

The top layer is an **ordered set**. Every `showModal()` / `showPopover()` / fullscreen call appends to the top. If a toast is hidden behind a modal's `::backdrop`, the toast is still in normal document flow — promote it to the top layer **after** the modal so it sits above the backdrop.

<a id="auto-vs-0"></a>
### The `auto` vs `0` Gotcha

`z-index: auto` and `z-index: 0` paint at the same level. But `0` **creates a stacking context** and `auto` does not. Changing one to the other looks like a no-op — it isn't. Children of that element may now be trapped.

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `z-index: 9999` (or escalating numbers) | Find the trapping ancestor; raise it or escape to top layer |
| Setting `z-index` on `position: static` | Add `position: relative` or use a flex/grid context |
| Treating `z-index: auto` and `z-index: 0` as interchangeable | They paint the same but only `0` creates a stacking context |
| Putting a global toast inside a component with `transform` | Promote to top layer (`popover="manual"`) or portal to `<body>` |
| Using `dialog.show()` expecting top-layer behavior | Use `showModal()` — `show()` stays in document flow |
| Stacking a toast on top of a modal without promoting it | Top layer is ordered; promote the toast **after** the modal |
| Adding `transform` to "fix a paint bug" then losing child stacking | `transform` creates a context — descendants are now trapped |
| Ad-hoc z-index values per component | Establish a documented scale (e.g. 10 base, 20 sticky, 30 dropdown, 40 modal) |
| Layering with z-index when an overlay should be global | Modal → `<dialog>`. Lightweight overlay → `popover`. Local only → z-index |
| No isolation between sibling components | Add `isolation: isolate` on component roots — creates a context with zero visual side effects |

---

**NEVER:**
- Suggest increasing a `z-index` value as a fix without first walking the ancestor chain for context-creating properties.
- Recommend `z-index: 9999` (or any "max number") — it's a code smell, not a solution.
- Add `transform: translateZ(0)`, `will-change: transform`, or `opacity: 0.99` "to force a layer" without warning that each creates a stacking context that will trap descendants.
- Claim a child can "win" against a sibling context via a higher `z-index` — the version-number model says otherwise.
- Use `dialog.show()` and tell the user it escapes stacking contexts — only `showModal()` enters the top layer.
- Tell the user to "just portal to `<body>`" before considering `<dialog>` or `popover`, which solve the problem without restructuring the tree.
- Add `z-index` to a `position: static` element and call it a fix.
- Silently change `z-index: auto` to `z-index: 0` (or vice versa) during a refactor — they differ in stacking-context creation.
- Recommend `popover="auto"` for a toast — light dismiss will close it on the first outside click. Use `popover="manual"`.
- Stack two top-layer elements and assume DOM order decides who wins — promotion order does (last promoted = on top).

---

## Review Checklist

- [ ] The failing element's `position` was checked before any `z-index` change
- [ ] The ancestor chain was inspected for all context-creating properties (not just `z-index`)
- [ ] The root cause is named (specific ancestor + property), not just "z-index issue"
- [ ] If the element is a global overlay, top layer (`<dialog>` or `popover`) was preferred over portaling
- [ ] No `z-index` value above the project's documented scale was introduced
- [ ] `isolation: isolate` is used on component roots that need local stacking
- [ ] Top-layer overlays use the correct API: `showModal()` for modals, `popover="auto"` for menus, `popover="manual"` for toasts/persistent overlays
- [ ] When stacking multiple top-layer elements, promotion order reflects intended z-order
- [ ] `z-index: auto` vs `0` was considered if the value was changed
- [ ] The fix removes the cause, not the symptom

## Verify Result

- The originally-hidden element now paints in the intended position across all states (hover, focus, scroll, resize)
- No `z-index` value was raised above the documented scale to achieve the fix
- The trapping ancestor (if any) is named in the explanation
- No new stacking contexts were introduced that may trap future descendants
- For top-layer fixes, the chosen API matches the semantic role (modal vs menu vs toast)

`z-index` is local. Stacking contexts are invisible. The top layer is the only true escape. When something doesn't stack right, the answer is always a parent you didn't know about — find it before you change a number.
