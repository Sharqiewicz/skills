# Patterns

The flows and behaviors. Strongest 1:1 web mappings in the whole skill: **loading** (skeletons), **entering data** (inline validation), **modality** (modal discipline), **managing accounts** (delayed sign-in), **onboarding**, **feedback**. Rules read as build guidance and as review checks.

## Loading

- **Show content structure immediately** — skeletons/placeholders shaped like the final content — and progressively replace as data arrives. Never a blank/waiting screen. (React Suspense + streaming SSR, `react-loading-skeleton`.)
- **Let people interact with the rest of the UI** while one region loads — don't block the whole app on one slow fetch.
- Determinate `<progress>` when duration is knowable; indeterminate spinner only when it isn't.
- **Prefetch large assets in the background** (`<link rel="prefetch">`, SWR/React Query revalidation) ahead of need.
- If the wait is unavoidably long, give something useful to look at; a custom branded loader is fine only if "still loading" stays clear.

## Entering data

- **Validate dynamically as people type/tab; surface errors at the field level — never wait until submit.** HTML constraint validation + `onBlur`/`onChange`, inline messages next to the field.
- **Disable submit until required fields are validly filled** so people see what's outstanding without a failed round-trip.
- Infer from context/autofill wherever possible (`autocomplete` attrs, geolocation, prior data); prefill sensible defaults.
- **Offer choices over free text** (`<select>`/`<datalist>`/autocomplete) when the option set is known. Support paste and drag-drop into fields. Secure fields for sensitive input; never prefill passwords.

## Feedback

- **Multi-channel** (color + text/icon + optional sound/haptic) — never color alone. Place status **near the relevant element**, not a modal that pulls people out of context.
- **Reserve blocking/alert feedback for critical, actionable interruptions** — overuse trains people to ignore it.
- **Warn before irreversible/negative actions; don't over-confirm routine ones.** Surface failures loudly; don't toast every trivial success ("Saved!").
- On failure, **explain why + the next step**, not a generic "Something went wrong". Use `aria-live` for accessible status.

## Modality

- **Present modally only with a clear benefit** — focused, critical, or narrowly-scoped tasks, not general content browsing. Keep the task simple and short; complex → full-screen modal or a dedicated route.
- **No "app within an app"** — no nested navigation inside a modal; keep any multistep path linear. Avoid buttons that could be confused with dismiss.
- **Never stack modals / never two alerts at once** — let one fully dismiss first. Consistent close-button placement across the system.
- Instantly identifiable purpose (clear title). Confirm before closing if dismissal loses data. Web: `<dialog>` + focus trap + `inert` background + scroll lock; a modal-stack guard.

## Managing accounts

- **Only require an account if core function needs it** — otherwise allow guest/anonymous use.
- **Delay sign-in as long as possible** — let people get value first; defer signup to the action that truly needs it (save, checkout, publish).
- Explain the concrete benefit in context (not "Sign up to continue"). Minimize required data; progressive profiling over one big form.
- **Prefer passkeys/magic links/SSO** over password fields. **Name the actual method** ("Continue with Google"), showing only methods available in context.

## Onboarding

- **Teach through interactivity** — let people perform the action, not watch a slideshow. Prefer contextual tips during real usage over one long flow.
- **Brief and skippable**; if skipped, don't force it again but keep it findable (help/settings). Scope it to your app's own features, not generic platform behavior.
- **Ship good defaults** — postpone nonessential setup. Tie any sensitive permission request to the moment the feature is used (with the "why"). Let people experience value before any rating/upgrade prompt. Don't let large downloads block first use.

## Offering help

- **Match help depth to task complexity** — a one-line inline hint for a 1–2 step task, a fuller tutorial only for genuinely complex flows. Don't explain standard/familiar UI — only what's unique to your app.
- **Keep it contextual, short, and dismissible** — tips 1–2 sentences, no promo. Tooltips: describe the one control, **lead with a verb, don't repeat the control's label, ~60–75 chars**.
- **Gate by eligibility and throttle frequency** — don't show a "new feature" tip to people already using it; don't stack multiple tips in one session. Product tours (Shepherd/driver.js) sparingly and always skippable.

## Settings

- **Best defaults for most people** — minimize both the number of settings and the need to touch them.
- **Read and honor systemwide/browser settings** (`prefers-color-scheme`, `prefers-reduced-motion`, `prefers-contrast`) — don't build redundant in-app equivalents.
- **Task-specific options in-context** (sort/filter/density in that view's toolbar), not a global settings modal. Keep the global settings page lean.

## Search

- Prominent, always-reachable entry (search bar / `Cmd+K` palette) if search matters; prefer one unified location (scoped local search within sections is fine).
- **Make current scope obvious** (placeholder, section title, active filter chips). Offer recent + predictive suggestions. Facets/scoping for large datasets. Let people clear history (privacy).

## Undo & redo

- Standard `Cmd/Ctrl+Z` / `Cmd/Ctrl+Shift+Z`; **multi-step** history, no arbitrary depth limit (command pattern / state history).
- **Label the specific action** ("Undo Delete Row", toast "Undid: deleted row" + Undo button). **Show the result even if off-screen** — scroll/highlight the affected element.

## File management

- **Autosave by default** — avoid requiring an explicit Save; debounce to backend / IndexedDB / localStorage with a synced "Saving…"/"Saved"/"Unsaved changes" indicator (Notion/Docs pattern).
- If autosave is off, show a clear **unsaved-changes indicator** (dot on the close control, asterisk in the title) and confirm before discarding.
- Provide **inline preview** even for unknown/unsupported types (iframe/PDF.js/image) rather than forcing a download-and-open cycle. Hide technical details (file extensions) by default but let people reveal them. Obvious create/open affordances; support rename/move/sort/search if you build a file browser.

## Drag & drop

- **Always provide a non-drag alternative** (menu/button/keyboard) — never the only path. Keyboard reordering + `aria-grabbed`.
- Visible drag preview past the threshold; **clear valid vs. invalid drop targets** (highlight / not-allowed); on invalid drop animate back to origin. Support multi-item + reordering; undo or confirm before unrecoverable drops. Auto-scroll near container edges; placeholder + progress for async (upload) drops.

## Collaboration & sharing

- Share action in a consistent, easy-to-find spot. **Plain-language permission summaries** ("Anyone with the link can view"), not raw enums. Keep options minimal/grouped. Surface active collaboration status persistently (presence avatars, "Shared" chip). Provide a way to manage/revoke access later.

## Notifications (managing)

- **Explicit opt-in before sending** — never on first load; request contextually after a relevant action. Represent urgency honestly; never use the most-interrupting channel for marketing. **Separate opt-in for promotional vs. transactional.** Provide per-category preference toggles in-app; easy to mute/revoke.
- **Content/authoring:** concise, factual, non-repetitive — never fire multiple notifications for the same unresolved event. Offer real inline **action buttons (≤~4)** instead of instructive text people won't remember. **Never put sensitive/private content in the body** (lock-screen/preview visibility is outside your control) — provide short, non-revealing **fallback preview text** ("New comment", "Friend request"). **Suppress when the app is already foregrounded/focused** — update the badge or insert the content into the visible view instead. **Use an alert, not a notification, for errors** — notifications are glanceable updates, not blocking problems. Title-case, unambiguous action labels; avoid unconfirmed destructive actions.

## Going full screen / launching / multitasking (brief)

- **Full screen:** aid focus, don't trap — keep essential controls reachable, let the user choose when to exit (bind Esc), animate transitions, preserve/resume state.
- **Launching:** perceived speed matters — avoid blank/FOUC; a skeleton matching the final layout beats a spinner; **no branded/text splash**; restore session state (scroll, route, tab, form) on reload.
- **Multitasking:** pause attention-requiring media when the tab is hidden (Page Visibility API) and resume; keep user-initiated background tasks running (Service Worker / Background Sync); one completion toast, not per-step spam.

## Lower-priority for web (brief)

- **Video:** prefer native `<video>`/standard controls; mirror standard keys (Space); preserve aspect ratio (`object-fit: contain`); resume position without prompting; PiP API.
- **Audio:** Media Session API; don't hijack other tabs' audio or system volume.
- **Printing:** `@media print` stylesheet hiding chrome; hide Print when nothing's printable.
- **Haptics:** Vibration API sparingly (PWA), always disable-able. **Ratings/reviews:** ask only after demonstrated engagement, never mid-task, rate-limit repeats. **Workouts/live sessions:** distinct "active/recording" visual state, large primary controls, completion summary, legible under stress.
