# CSP & security headers

Use a nonce-based strict CSP as defense-in-depth against XSS and data exfiltration, and ship a small baseline of response headers everywhere; neither replaces fixing injection bugs. [BAW §12, §18]

## What CSP is (and is not)

- CSP is a browser-enforced allowlist of what a document may load/execute/submit. Main goal: limit the impact of XSS; side benefits: block exfiltration channels, clickjacking (`frame-ancestors`), mixed content. [BAW §18]
- It mitigates consequences, it does not remove the bug. An app with many unfixed XSS sinks should fix those first. [BAW §18]
- Deliver as an HTTP header. `<meta http-equiv>` supports fewer directives (no `frame-ancestors`, no report-only, no `sandbox`) and only protects markup after the tag, so an injection placed before it escapes the policy. Use meta for experiments only. [BAW §18]
- Syntax: directives separated by `;`, values by spaces, no colon after the name. Keywords need single quotes (`'self'`, `'none'`). Path sources must end in `/` to mean a directory.
- `default-src` is a fallback only for fetch directives that are absent; it is not inherited by a directive that is present. Start from `default-src 'none'` or `'self'` and open up per type. [BAW §18]
- Not covered by `default-src` (set explicitly): `base-uri`, `form-action`, `frame-ancestors`, `sandbox`, `report-*`, `upgrade-insecure-requests`.

## Strict CSP: nonce/hash, not host allowlists

Why: allowlists of hosts are routinely bypassable (see Bypasses). A strict policy trusts specific script elements, not hosts. [BAW §18] (updated: Google's strict-CSP guidance recommends exactly this shape — https://web.dev/articles/strict-csp)

```
# ✅ strict, nonce-based
script-src 'nonce-{RANDOM}' 'strict-dynamic'; object-src 'none'; base-uri 'none';
# ✅ strict, hash-based (static inline scripts that rarely change)
script-src 'sha256-{BASE64_HASH}' 'strict-dynamic'; object-src 'none'; base-uri 'none';
# ❌ host allowlist
script-src 'self' https://ajax.googleapis.com https://www.google-analytics.com
# ❌ defeats the purpose
script-src 'self' 'unsafe-inline' 'unsafe-eval'
```

- Nonce rules: fresh per response (never per build, never cached), >=128 bits from a CSPRNG, base64. A reused or guessable nonce lets an attacker inject a valid `<script nonce>`. Put the same value on every trusted `<script>`. [BAW §18]
- Nonce means the HTML must be rendered per request; a CDN/static cache serving one HTML body to many users breaks the guarantee. Use hashes (or SRI-based hashing) for static pages.
- Hash rules: SHA-256/384/512 of the exact inline script text; any whitespace change breaks it. Practical only for few, stable inline scripts. [BAW §18]
- `'strict-dynamic'`: scripts created by an already-trusted script (via `document.createElement('script')`) inherit trust, so tag managers and lazy chunks work without listing hosts. Side effect: browsers that understand it ignore host lists and `'unsafe-inline'` in the same `script-src`. [BAW §18]
- Compat fallback (old browsers ignore unknown tokens): `script-src 'nonce-X' 'strict-dynamic' https: 'unsafe-inline'`. Modern browsers ignore `https:`/`'unsafe-inline'` because of the nonce + strict-dynamic. (updated: web.dev strict-CSP)
- `'unsafe-inline'` alone = no XSS protection; if the app cannot drop it, postpone CSP rather than ship a policy that looks protective. [BAW §18]
- `'unsafe-eval'` re-enables `eval`/`new Function`/string `setTimeout`. Frameworks with runtime template compilation need it; prefer precompiled templates. WebAssembly needs `'wasm-unsafe-eval'` instead of `'unsafe-eval'`. (updated: MDN CSP)
- Inline event handlers (`onclick=`) and `javascript:` URLs are blocked by strict policies; nonces do not cover them. Use `addEventListener`.
- Inline styles: `style-src 'unsafe-inline'` is a much smaller risk than for scripts (data exfil via CSS is possible but hard); acceptable trade-off when CSS-in-JS forces it, but prefer nonces if the library supports them.

## Key directives

- `script-src` (+ `script-src-elem`/`-attr`): see above. Most important directive.
- `object-src 'none'`: always; blocks `<object>/<embed>/<applet>` plugin vectors. [BAW §18]
- `base-uri 'none'` (or `'self'`): always. Without it an injected `<base href>` redirects relative `<script src="/app.js" nonce=...>` to an attacker host while the nonce still matches. [BAW §18]
- `form-action 'self'` (or explicit list): not covered by `default-src`. Without it, injected unclosed `<form action=evil>` placed before a real form hijacks submission (HTML forbids nested forms), leaking tokens/passwords even under a strict `default-src`. [BAW §18]
- `frame-ancestors`: who may embed this page (clickjacking). `'none'` or `'self'` or explicit origins; checks the whole ancestor chain. Not supported in meta or report-only. [BAW §18]
- `frame-src`/`child-src`/`worker-src`/`connect-src`/`img-src`/`font-src`/`media-src`/`manifest-src`: narrow per resource type; `connect-src` governs fetch/XHR/WebSocket/EventSource/sendBeacon, so it limits exfiltration. [BAW §18]
- `upgrade-insecure-requests`: rewrites http subresource and navigation URLs to https before fetching. Cheap, add it. [BAW §18]
- `block-all-mixed-content` (updated: deprecated, and browsers now auto-upgrade/block mixed content; rely on `upgrade-insecure-requests` — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/block-all-mixed-content).
- `plugin-types` (updated: removed from the spec; drop it, `object-src 'none'` covers plugins).
- `sandbox`: same tokens as `<iframe sandbox>`. On a whole document it disables scripts, forms, popups, same-origin access unless re-enabled via `allow-*`. Use for user-content pages (uploads, previews) served from your origin. Never combine `allow-scripts` with `allow-same-origin` on content you do not control (it can remove its own sandbox). [BAW §18]
- Reporting: see Rollout.
- Trusted Types: `require-trusted-types-for 'script'` + `trusted-types` hardens DOM-XSS sinks (`innerHTML`, `eval`); not in the book. (updated: MDN/web.dev recommend it alongside strict CSP for DOM XSS; support is not universal, so roll out in report-only first.)

## Bypasses (why allowlists fail)

- JSONP endpoints on an allowed host: `?callback=alert(1)` returns attacker-controlled JS from an "allowed" origin. Popular analytics/API hosts were found to expose such endpoints. [BAW §18]
- Allowed CDNs hosting JS frameworks: loading an old AngularJS (or other template/"script gadget" framework) from an allowed CDN path plus an HTML injection yields code execution, even without `'unsafe-inline'`; research shows near any framework can serve as a gadget, also under `'strict-dynamic'` if the page already contains such gadgets. [BAW §18]
- Wildcards/broad hosts (`*.cloudfront.net`, `*.githubusercontent.com`, `https:`, `data:`, `*`): attacker can host scripts there. Also any host that lets users upload or proxy JS.
- `'unsafe-inline'` / `'unsafe-eval'` / missing `object-src` / missing `base-uri` / missing `form-action`: see above.
- Nonce leakage: nonce reflected in cacheable HTML, static nonce, nonce exposed through injection point before the script (dangling markup that swallows the nonce attribute).
- Mitigation: no host allowlist for scripts, strict-dynamic + nonce, audit policies with the Google CSP Evaluator. [BAW §18]

## Rollout

1. Inventory first: ship `Content-Security-Policy-Report-Only` with the target policy; collect reports (also useful to find unapproved third-party scripts such as marketing trackers). [BAW §18]
2. Fix violations: move inline scripts to files or nonce them, remove `eval`, replace inline handlers, pull third-party scripts to self-hosted or load them from a trusted nonced loader.
3. Enforce with `Content-Security-Policy`; keep a report-only copy of the next tighter policy running in parallel.
4. Expect noise: browser extensions and injected ad tooling cause reports you cannot fix; filter by `effectiveDirective`/`blockedURL`. [BAW §18]
5. Reporting (updated: `report-uri` is deprecated in favor of `report-to` + `Reporting-Endpoints`; keep both during transition, supporting browsers prefer `report-to` — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/report-to):

```
Reporting-Endpoints: csp-endpoint="https://example.com/csp-reports"
Content-Security-Policy-Report-Only: <policy>; report-to csp-endpoint; report-uri https://example.com/csp-reports
```

- Report body (report-to) is `application/reports+json` with `body.blockedURL`, `effectiveDirective`, `sample`; the legacy report-uri body is `application/csp-report` with a `csp-report` object. Accept both on the collector; rate-limit and treat content as untrusted input. [BAW §18]

## When CSP is worth it

- Worth it: apps with few third-party origins, modern framework with nonce support, handling sensitive data, a team able to keep it maintained; greenfield builds CSP in from day one. [BAW §18]
- Weak value: policy needs `'unsafe-inline'` for scripts, dozens of third-party script hosts, or the app has known unfixed XSS. Fix the bugs first; a policy that is trivially bypassable adds false confidence. [BAW §18]
- Even then, cheap wins stay valuable: `frame-ancestors`, `object-src 'none'`, `base-uri`, `form-action`, `upgrade-insecure-requests` work with no script changes (clickjacking-only policy: `frame-ancestors 'none'`). [BAW §18]

## Example policies

```
# A. No third parties, all scripts external
default-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'
# B. Same + per-request inline scripts
default-src 'self'; script-src 'self' 'nonce-{R}'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'
# C. Many third-party/tag-manager scripts (preferred modern shape)
default-src 'self'; script-src 'nonce-{R}' 'strict-dynamic'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'; upgrade-insecure-requests
# D. Clickjacking only
frame-ancestors 'none'
```

[BAW §18] (A-D follow the book's scenarios; C is modernized: no host list, `'self'` is ignored under strict-dynamic anyway.)

## Next.js implementation

(updated: current Next.js names the request hook `proxy.ts`/`proxy()`; older versions call it `middleware.ts`/`middleware()`. Same code. https://nextjs.org/docs/app/guides/content-security-policy)

```ts
// proxy.ts (or middleware.ts on older Next.js)
import { NextRequest, NextResponse } from 'next/server'

export function proxy(request: NextRequest) {
  const nonce = Buffer.from(crypto.randomUUID()).toString('base64')
  const isDev = process.env.NODE_ENV === 'development'
  const csp = `
    default-src 'self';
    script-src 'self' 'nonce-${nonce}' 'strict-dynamic'${isDev ? " 'unsafe-eval'" : ''};
    style-src 'self' 'nonce-${nonce}';
    img-src 'self' blob: data:;
    font-src 'self';
    object-src 'none';
    base-uri 'self';
    form-action 'self';
    frame-ancestors 'none';
    upgrade-insecure-requests;`.replace(/\s{2,}/g, ' ').trim()

  const requestHeaders = new Headers(request.headers)
  requestHeaders.set('x-nonce', nonce)
  requestHeaders.set('Content-Security-Policy', csp) // Next reads the nonce from here to tag its own scripts
  const response = NextResponse.next({ request: { headers: requestHeaders } })
  response.headers.set('Content-Security-Policy', csp)
  return response
}

export const config = {
  matcher: [{
    source: '/((?!api|_next/static|_next/image|favicon.ico).*)',
    missing: [{ type: 'header', key: 'next-router-prefetch' }, { type: 'header', key: 'purpose', value: 'prefetch' }],
  }],
}
```

- Nonce requires dynamic rendering (`await connection()` or use of `headers()`/`cookies()`); static/ISR pages and PPR cannot carry a per-request nonce, and the page loses CDN caching. If that cost is unacceptable, use the experimental SRI/hash mode or a non-nonce policy and accept weaker script protection.
- Next.js auto-applies the nonce to framework scripts and `<Script nonce>`; pass it manually to your own inline scripts and third-party components (`const nonce = (await headers()).get('x-nonce')`).
- `'unsafe-eval'` only in development (React debugging); never in production.
- Do not generate the nonce at build time or in `next.config` `headers()`; that value is static.
- Static CSP without nonce (`next.config` `headers()`) is fine for baseline directives, but then scripts need `'unsafe-inline'`, which voids XSS protection.
- CSS-in-JS/inline style libs: nonce support or `style-src 'unsafe-inline'` as a knowing trade-off.
- Browsers/clients cache nothing about nonces; ensure the `Vary`/cache layer never stores HTML across users.

## Security headers (value + why)

- `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload` Force HTTPS after first visit; turns cert errors into hard failures. Without `includeSubDomains`, an attacker controlling a sibling subdomain's DNS can capture or overwrite domain-scoped cookies over HTTP even if they are `Secure`. `preload` needs submission to the preload list and is hard to reverse: add only once every subdomain serves HTTPS. First visit is unprotected unless preloaded. Also redirect http to https at the edge. [BAW §12] (OWASP now suggests a two-year max-age; one year is the floor for preload.)
- `X-Content-Type-Options: nosniff` Stops MIME sniffing that turns a mislabeled upload (e.g. avatar with HTML inside, extension stripped) into executable HTML/JS. Always set; serve user uploads with a correct `Content-Type` (and ideally from a separate origin). [BAW §12]
- `Referrer-Policy: strict-origin-when-cross-origin` Avoids leaking full internal paths/tokens in URLs to third parties via `Referer`. Use `no-referrer` for sensitive apps/admin tools, `same-origin` if analytics needs only internal referrers. Never put secrets in URLs regardless. Avoid `unsafe-url`. (updated: this value is now the browser default, but set it explicitly because older browsers defaulted to the weaker `no-referrer-when-downgrade`; OWASP recommends it.) [BAW §12]
- `Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()` (updated: `Feature-Policy` was renamed to `Permissions-Policy` with different syntax: structured list `feature=(self "https://x.com")` instead of `feature 'self' https://x.com`; set only the new one. https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Permissions-Policy). Disable powerful features the site does not use, which also limits what a compromised third-party iframe/script can request. To delegate to an iframe use `allow="..."` on the tag. [BAW §12]
- `X-Frame-Options: DENY` (or `SAMEORIGIN`) Legacy clickjacking control. (updated: superseded by CSP `frame-ancestors`, which wins when both are present in modern browsers; keep XFO only as a cheap fallback for old browsers. Do not use `ALLOW-FROM`: obsolete and ignored by modern browsers.) [BAW §12]
- `Content-Security-Policy: ...` see above.
- `Cross-Origin-Opener-Policy: same-origin` (not in the book) Isolates the browsing context from cross-origin popups (defeats opener-based attacks/XS-Leaks); breaks OAuth/payment popups that rely on `window.opener`, so test; `same-origin-allow-popups` is the softer option. (OWASP HTTP Headers cheat sheet)
- `Cross-Origin-Resource-Policy: same-site` (or `same-origin`) on non-public resources to block cross-origin embedding/leak; leave public assets/CDN files alone. COEP `require-corp` only when you need cross-origin isolation; it breaks third-party embeds.
- Remove/neutralize: `X-XSS-Protection` (updated: legacy filter removed and itself exploitable; send `0` or omit, rely on CSP), `X-Powered-By`/verbose `Server` (fingerprinting; Next.js: `poweredByHeader: false`), `Expect-CT`, `Public-Key-Pins` (deprecated). [BAW §12] notes headers are a rich source of tech fingerprints.
- `Cache-Control: no-store` on authenticated/sensitive responses (not in the book) so shared caches/back button don't expose them.
- Headers are layered hardening, not a fix: never treat them as complete protection. [BAW §12]

## Trusting client-supplied headers

- `X-Forwarded-For`, `X-Forwarded-Host`, `X-Real-IP`, `Client-IP`, `X-Originating-IP`, `X-Backend-*` etc. are attacker-settable. Using them for IP allowlists, "internal network" bypass of CAPTCHA/dev mode, password-reset link host, or redirects enables access-control bypass, poisoned reset emails, open redirect, log poisoning. [BAW §12]
- ✅ Build absolute URLs from a configured canonical origin (env var), never from `Host`/`X-Forwarded-Host`; only trust forwarding headers set by your own proxy and strip them at the edge; never gate authorization on IP headers.

## Clickjacking

- Attack: attacker page frames yours invisibly and tricks the victim into clicking a real button. Needs framing, so block framing. [BAW §12, §18]
- ✅ `Content-Security-Policy: frame-ancestors 'none'` (or `'self'` / explicit origins if you must be embedded) plus `X-Frame-Options: DENY`/`SAMEORIGIN` fallback. Applies to every HTML response incl. error pages, not just the homepage.
- ✅ If embedding is a product feature, allowlist specific origins in `frame-ancestors` and keep sensitive actions (payments, settings, deletions) re-confirming via user-initiated top-level flow.
- ❌ JS frame-busting (`if (top !== self)`) as the only defense; bypassable with `sandbox` on the attacker's iframe.
- Cookies: `SameSite` lax/strict reduces clickjacking of logged-in state in cross-site frames but does not replace frame blocking.

## Copy-paste baseline (Next.js `next.config.ts`; CSP via the proxy above)

```ts
const securityHeaders = [
  { key: 'Strict-Transport-Security', value: 'max-age=31536000; includeSubDomains; preload' },
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
  { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=(), payment=(), usb=()' },
  { key: 'X-Frame-Options', value: 'DENY' }, // fallback; CSP frame-ancestors is the real control
  { key: 'Cross-Origin-Opener-Policy', value: 'same-origin' }, // test OAuth/popup flows
]
export default {
  poweredByHeader: false,
  async headers() { return [{ source: '/:path*', headers: securityHeaders }] },
}
```

Static-host equivalent: same names/values in nginx `add_header ... always;` or the host's headers config; `always` matters so error responses also carry them. [BAW §12]

## Review checks

- Is a CSP sent as an HTTP header (not only `<meta>`), on every HTML response?
- Does `script-src` avoid `'unsafe-inline'`, `'unsafe-eval'`, `*`, `https:`, `data:` and broad CDN/analytics hosts? Flag host allowlists that include JSONP-capable or framework-hosting origins.
- Is the nonce generated per request from a CSPRNG (>=128 bits), never static/build-time/cached, and applied to all inline/third-party scripts? Are pages that use it dynamically rendered?
- Are `object-src 'none'`, `base-uri 'none'|'self'`, `form-action`, and `frame-ancestors` all present (they are not covered by `default-src`)?
- `upgrade-insecure-requests` present; no `block-all-mixed-content` or `plugin-types` (obsolete).
- New/changed CSPs first go through `Content-Security-Policy-Report-Only` with `report-to` (+ `report-uri` fallback) and a working collector.
- Dev-only relaxations (`'unsafe-eval'`) gated on `NODE_ENV` and absent from production output.
- HSTS present with `max-age` >= one year; `includeSubDomains` only if all subdomains are HTTPS-ready; `preload` only deliberately.
- `X-Content-Type-Options: nosniff`, `Referrer-Policy` (not `unsafe-url`), `Permissions-Policy` (not `Feature-Policy`) present.
- Framing blocked via `frame-ancestors` (+ XFO fallback); no `ALLOW-FROM`; no JS-only frame busting.
- No `X-XSS-Protection: 1`, `X-Powered-By`, or version-revealing `Server` headers.
- No authorization, redirect, or absolute-URL logic based on `X-Forwarded-*`/`Host`/`Client-IP` from the client.
- CSP is not used as an excuse to leave XSS sinks (`dangerouslySetInnerHTML`, `innerHTML`) unsanitized.
