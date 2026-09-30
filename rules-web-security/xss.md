# XSS

Attacker-controlled data must never reach an HTML/JS/URL interpreter as code; encode for the exact context, prefer auto-escaping and text-only sinks, sanitize when HTML is required, and treat CSP/Trusted Types as a backstop, not the fix.

## Impact (why it is never "just alert(1)")
- XSS = attacker JS running in your origin. It can read anything the logged-in user can read and perform any action they can. Effectively session takeover. [BAW §17]
- Any `alert(1)` PoC implies data exfiltration (`fetch` to attacker host) and UI actions (`.click()`, form submit). Rate severity accordingly.

## Types
- Reflected: request data (query, POST, cookie) echoed into the response. Delivered via a crafted link. [BAW §17]
- Stored: payload persisted (DB, third-party system) and rendered to later visitors; no link needed. Admin panels rendering user content are prime targets.
- DOM-based: client-side JS moves a source into a sink; payload may never reach the server (e.g. URL fragment). WAFs and server-side filters do not see it. [BAW §17]

## Injection contexts and the matching defense
| Context | Example slot | Defense |
|---|---|---|
| HTML text | `<div>{x}</div>` | HTML-entity encode `& < > " '` |
| Quoted attribute | `<div class="{x}">` | HTML-encode incl. quotes; always quote attributes |
| Unquoted attribute | `<img src={x}>` | Breaks on whitespace alone, no special chars needed. Never emit unquoted values |
| URL attribute | `href/src/action="{x}"` | Allowlist scheme (`http:`/`https:`, maybe `mailto:`); entity-escaping does NOT stop `javascript:` |
| JS string in `<script>` | `var a="{x}"` | Do not hand-build. Emit JSON with `<`, `>`, `&`, U+2028/9 escaped as `\uXXXX` (or use a data attribute / JSON endpoint) |
| Inline event handler | `onclick="f('{x}')"` | Browser HTML-decodes the attribute before JS runs, so `&#39;` still breaks out. Needs JS-string + HTML-attr encoding; better: no inline handlers |
| `javascript:` URL with data | `href="javascript:f('{x}')"` | Three layers (JS string, URL-decode, HTML entities). Refactor away |
- Nested contexts need one encoder per layer, applied innermost first. Missing any layer = bug. [BAW §17]
- Closing a `</script>` inside a JS string ends the script block at HTML-parse time, before JS escaping matters. Escape `<` in any data placed inside `<script>`. [BAW §17]
- Hand-rolled escaping is error-prone (backslash doubling, wrong layer). Prefer structure that avoids the context entirely. (updated: OWASP says the only safe place for a variable in JS is a quoted data value; never inside event handlers, comments or script text. [OWASP XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html))
- Content-Type matters: JSON endpoints must answer `application/json`, not `text/html`.

## DOM XSS: sources -> sinks
Sources (attacker-influenced input): `location.*` (hash, search, href), `document.referrer`, `document.cookie`, `window.name`, `postMessage` `event.data`, `localStorage`/`sessionStorage`, WebSocket/fetch responses that embed other users' data, form fields. [BAW §17, §13]
Finding a vuln = find a path source -> sink with no sanitization. [BAW §13]

| Sink family | Examples | Safe alternative |
|---|---|---|
| eval-family (string -> code) | `eval`, `new Function`, `setTimeout("str")`, `setInterval("str")`, `script.text/textContent/src` | Pass functions not strings; `JSON.parse`; lookup tables |
| HTML sinks | `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write(ln)`, `srcdoc`, `DOMParser` -> insert, jQuery `.html()/.append(str)` | `textContent`, `createElement` + `setAttribute`, sanitizer |
| URL sinks | `location`, `location.href/assign/replace`, `a.href`, `iframe.src`, `form.action`, `window.open`, `embed/object` | Parse with `new URL()`, allowlist scheme |
- Sink reached with attacker data AND an unsafe scheme (`javascript:`) gives code exec even without HTML. [BAW §17]
- Indirect flows count: data from `fetch().json()` into `eval` is exploitable if any other feature lets a user store that value. [BAW §17]
- postMessage handlers: validate `event.origin` against an exact allowlist and validate `event.data` shape before any sink. Treat `postMessage` data as untrusted even from your own frames.
```js
// ❌
el.innerHTML = `<img src="/i/${location.hash.slice(1)}.png">`;
form.action = ev.data.url; form.submit();
// ✅
img.src = `/i/${encodeURIComponent(id)}.png`;   // attribute via DOM API, encoded
el.textContent = userText;
```

## Output encoding and templates
- Default to a templating layer with contextual auto-escaping (server: Django/Jinja/Twig-style; client: React/Vue/Angular text bindings). It removes the "forgot to encode" class of bugs. [BAW §17]
- Auto-escaping handles text and quoted attributes, but NOT URL-valued attributes in most engines/frameworks: validate scheme yourself. [BAW §17]
- Framework escaping does not protect your own hand-written DOM code (`eval`, `innerHTML`, `location =`). [BAW §17]
- Raw/unescaped template output (`|safe`, `{!! !!}`, `v-html`, `{@html}`, `[innerHTML]` with bypass) is an escape hatch: each use needs a sanitizer or a constant.

## Allowing user HTML
- Use a maintained sanitizer (DOMPurify on the client, server equivalents like HtmlSanitizer / HTMLPurifier), allowlist-based. It strips `<script>`, event attributes, unsafe URL schemes, unlisted tags. [BAW §17]
- Sanitize at the point of output (or just before inserting into the DOM), with the configuration reviewed; keep the library patched since bypasses are found regularly. (updated: OWASP recommends DOMPurify and stresses patching. [OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html))
- Markdown renderers output HTML: sanitize that output too. [BAW §17]
- Never DIY filters. Known bypass classes: regex `<.*>` (`.` skips newlines), stripping `(`/`)` (entities, `\x28` escapes), requiring whitespace before `onerror` (quote then attribute directly). [BAW §17]
- Do not mutate sanitized output afterward (concatenation, re-parsing, a second sanitizer with a different parser).
- (updated: the native HTML Sanitizer API (`el.setHTML(str)`) is the intended built-in replacement for `innerHTML` + DOMPurify, but support is not universal yet; feature-detect and keep DOMPurify as a fallback. `setHTMLUnsafe` is NOT safe. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Sanitizer_API))

## File upload XSS
- User-uploaded `.html`, `.svg`, and any XML (with XHTML namespace) execute script when opened on your origin; blocking only `.html` is insufficient. [BAW §17]
- Best fix: serve uploads from a separate registrable domain (or at minimum a separate subdomain) that holds no cookies/app data. [BAW §17] Cookies scoped to the parent domain still leak to subdomains, so a fully separate domain is stronger.
- Also: serve with `Content-Disposition: attachment` or a safe fixed `Content-Type`, `X-Content-Type-Options: nosniff`, never echo the client-supplied MIME type; re-encode raster images; treat SVG as active content (sanitize or rasterize).
- In Next.js: do not write uploads into `public/` on the app origin.

## React / Next.js specifics
- JSX `{value}` text and normal attributes are escaped. The danger is the escape hatches and non-text slots below.
- `dangerouslySetInnerHTML={{ __html: x }}`: only with sanitized (DOMPurify) or constant content. React does no sanitizing. [BAW §17]
- `href={userUrl}` / `src` / `action` / `formAction`: React does not block `javascript:` (and `data:`) in these. Validate via allowlist. [BAW §17] (updated: React still only warns/does not reliably block this; OWASP lists React as unable to handle these URL schemes safely. [OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html))
```tsx
// ❌
<a href={user.website}>site</a>
// ✅
const safeHref = (u: string) => {
  try { const p = new URL(u, "https://x.invalid"); return ["http:", "https:"].includes(p.protocol) ? u : "#"; }
  catch { return "#"; }
};
<a href={safeHref(user.website)} rel="noopener noreferrer">site</a>
```
- Also validate URLs used in `router.push(userUrl)`, `window.location = x`, `window.open(x)`, `<iframe src>`, `redirect(searchParams.next)` (scheme and open-redirect).
- `ref.current.innerHTML = x` / `insertAdjacentHTML` / third-party DOM libs (charts, editors, tooltips, jQuery plugins) bypass React escaping entirely: same rules as any HTML sink.
- SSR/hydration data into `<script>`: `JSON.stringify` alone is not safe; `</script>` or `<!--` in a value terminates/alters the block. Escape `<` (to `\u003c`) plus U+2028/2029 (e.g. `serialize-javascript`), or pass state through `<script type="application/json">` / data attributes and `JSON.parse` it. Next's built-in data channels already do this; custom `<script dangerouslySetInnerHTML>` for bootstrap state does not.
```tsx
// ❌
<script dangerouslySetInnerHTML={{ __html: `window.__S=${JSON.stringify(state)}` }} />
// ✅
<script dangerouslySetInnerHTML={{ __html: `window.__S=${JSON.stringify(state).replace(/</g, "\\u003c")}` }} />
```
- JSON-LD `<script type="application/ld+json">` with user data has the same `</script>` problem: escape `<`.
- User-controlled props spread onto elements (`<div {...userProps} />`) can inject `dangerouslySetInnerHTML` or event-like props; allowlist keys.
- User-controlled element type / `React.createElement(userTag)`, and `style`/`className` strings from users: constrain to allowlists.
- Server Actions, Route Handlers and API routes returning user content as `text/html` reintroduce reflected XSS; return JSON with correct Content-Type.
- Markdown/MDX from users: render with a sanitizing pipeline (e.g. rehype-sanitize) or treat MDX as code (MDX compiles to executable JS; never compile untrusted MDX).
- `eval`/`new Function` on anything that came over the network, even "config" JSON, is an XSS sink. Framework does not help here. [BAW §17]

## Framework template-injection pitfalls [BAW §17]
- Client-side template engines evaluate expressions inside their delimiters (`{{ }}`). If the server puts user data into a page that a client template engine then compiles, HTML-encoding is not enough: braces become code. Old AngularJS-style engines were classic victims (expression -> constructor chain -> `Function`).
- Rule: templates are static and developer-authored. Never build a template string from user input (server or client); pass user data as model/props only. In Vue this includes `new Vue({template: userStr})` / runtime-compiled templates; in Angular, `bypassSecurityTrust*`; in Lit, `unsafeHTML`.
- Angular-style built-in sanitization of `[innerHTML]` and a URL scheme allowlist is the exception; React/Vue/others generally have neither: add DOMPurify and a URL check manually. [BAW §17]

## Trusted Types (updated: not in the book)
- Makes DOM XSS sinks (`innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval`, `Function`, `script.src/text`, `setTimeout(str)`, Worker URLs) reject plain strings and accept only values minted by named policies.
- Enable via CSP: `require-trusted-types-for 'script'` plus optional `trusted-types <policy-names>` allowlist. Start with report-only, fix violations, then enforce.
- One small policy (e.g. `createHTML: s => DOMPurify.sanitize(s)`) centralizes review. A `default` policy helps only for migrating legacy code.
- Support is now wide but verify current compatibility before relying on it; it is defense in depth, not a replacement for encoding. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/Trusted_Types_API)
- Next.js: CSP (with nonces) can be set in middleware/headers; nonce-based strict CSP blocks injected inline scripts but not DOM XSS via allowed scripts. [BAW §17 points to the CSP chapter]

## Browser XSS filters are not a defense (updated)
- The book notes the Chromium XSS auditor was already removed and that filters were bypassable and abusable for side-channel attacks. [BAW §17]
- Do not rely on `X-XSS-Protection`; if the header is set at all, set it to `0` (or omit it). Use CSP instead. Sources: [MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-XSS-Protection), [OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html).

## Other rules
- Encode on output, for the context, every time; input validation/WAF is additional, never primary.
- Use `textContent`/`innerText`, `setAttribute` (non-URL, non-handler attributes), `.value` instead of HTML sinks. [BAW §17]
- Quote all dynamic attribute values. No inline event handlers or `javascript:` links; attach listeners in code.
- Mark auth cookies `HttpOnly` to limit theft (does not stop actions in user context); add CSP as damage limitation.

## Review checks (flag when found)
- `dangerouslySetInnerHTML` whose value is not a constant or the direct output of DOMPurify/sanitizer.
- `\.innerHTML\s*=|\.outerHTML\s*=|insertAdjacentHTML|document\.write|\.srcdoc|createContextualFragment|\$\(.*\)\.html\(` with non-constant input.
- `eval\(|new Function\(|setTimeout\(\s*["'`]|setInterval\(\s*["'`]|script\.(text|textContent|src)\s*=`.
- `href=\{|src=\{|action=\{|formAction=\{` bound to non-literal data without a scheme allowlist helper; also `location(\.href)?\s*=|location\.(assign|replace)\(|window\.open\(|router\.(push|replace)\(|redirect\(` fed from query/params/body/storage.
- `addEventListener\(['"]message` handlers missing an exact `event.origin` check, or passing `event.data` to a sink.
- `<script` blocks built with `JSON.stringify(...)` and no `<` escaping; unquoted or string-concatenated HTML/attributes; inline `onclick="..."` with interpolation.
- `{...props}` spread from user/CMS data onto DOM elements; user-controlled tag names.
- Template strings compiled at runtime from user input (`Vue.compile`, `template:` from data, `bypassSecurityTrust`, `unsafeHTML`, `v-html`, `|safe`).
- Hand-written "sanitizers" (regex replace of `<script`, `on\w+=`, parentheses); markdown -> HTML without a sanitizer; MDX compiled from user content.
- Uploads: writes to `public/` or app origin, accepting `.svg/.html/.xml`, trusting client MIME, missing `nosniff`/`attachment`.
- `X-XSS-Protection` set to anything but `0`; absence of CSP / Trusted Types on apps handling sensitive data.
