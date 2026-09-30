---
name: rules-web-security
description: "Frontend and full-stack web security rules for React, Next.js and TypeScript. Covers XSS sinks, CSP and security headers, SOP, CORS, postMessage, WebSocket, CSRF, cookies, sessions, JWT, OAuth/PKCE, and secrets leaked to the browser. Distilled from Securitum's 'Bezpieczeństwo aplikacji webowych' and checked against current OWASP and MDN. Use it when building or reviewing any code that renders user data, handles auth or tokens, sets headers or cookies, or talks cross-origin. Triggers on: security, XSS, dangerouslySetInnerHTML, innerHTML, eval, sanitize, DOMPurify, CSP, Content-Security-Policy, nonce, security headers, HSTS, clickjacking, CORS, Access-Control-Allow-Origin, same-origin, postMessage, WebSocket, CSRF, SameSite, cookie flags, HttpOnly, session, login, logout, password reset, authorization, IDOR, JWT, OAuth, PKCE, token storage, localStorage token, NEXT_PUBLIC, secrets, source maps, .env, Server Actions security."
user-invocable: true
---

Frontend web security rules, distilled from the book *Bezpieczeństwo aplikacji webowych* (Securitum) and checked against current OWASP and MDN guidance. Every rule works two ways: as build guidance ("do X") and as a review check ("flag when not X").

## MANDATORY PREPARATION

1. Identify which trust boundary the code touches: rendering untrusted data, response headers, cross-origin communication, cookies/sessions/CSRF, tokens/OAuth, or what ships to the browser.
2. Read the matching reference file before answering or writing code (see **Quick Reference**). If the code touches several boundaries, read every file that applies.
3. Before reviewing, read the actual code: the handler or Server Action, and the component that renders the data. Also check `next.config.*`, `middleware.ts`/`proxy.ts`, and the auth library config. Never judge security from one component in isolation.
4. Find the framework and auth stack (Next.js App or Pages Router, Auth.js or a custom setup, where headers are set) in `package.json` and the config files, so every fix uses the project's real APIs.

---

## Quick Reference

| Boundary | Typical code | Reference |
|---|---|---|
| Rendering untrusted data | `dangerouslySetInnerHTML`, `href={url}`, `innerHTML`, `eval`, SSR state in `<script>`, uploads | [xss.md](xss.md) |
| Response headers | CSP with nonces, HSTS, `nosniff`, `Referrer-Policy`, `Permissions-Policy`, `frame-ancestors` | [csp-and-headers.md](csp-and-headers.md) |
| Cross-origin | CORS config, `fetch(..., { credentials })`, `postMessage`, `window.open`, WebSocket | [cross-origin.md](cross-origin.md) |
| State-changing requests | Route handlers, Server Actions, cookies, login/logout/reset, role checks | [csrf-and-sessions.md](csrf-and-sessions.md) |
| Tokens and third-party auth | JWT verify, token storage, OAuth/OIDC, PKCE, `redirect_uri` | [tokens-and-oauth.md](tokens-and-oauth.md) |
| What the browser gets | `NEXT_PUBLIC_*`, source maps, `.git`/`.env` in the web root, verbose errors, dependencies | [exposure.md](exposure.md) |

---

## Core Principles (the load-bearing rules)

If you check nothing else, check these.

1. **The server decides; the client only displays.** Every Server Action, route handler and API endpoint authenticates and authorizes on its own. Hidden buttons, disabled inputs, page redirects, client checks and UUIDs are not access control. [BAW §26]
2. **Untrusted data never reaches a code, HTML or URL sink.** Use JSX text or `textContent`. Pass HTML through DOMPurify only when HTML is truly required. User URLs pass an `http:`/`https:` allowlist before they reach `href`, `src`, `location`, `router.push` or `window.open`. React does not block `javascript:`. [BAW §17]
3. **Everything shipped to the browser is public and editable.** No secrets in client code or `NEXT_PUBLIC_*`, no production source maps, and nothing but build output in the web root. [BAW §13, §16]
4. **Session cookies are `__Host-`, `HttpOnly`, `Secure` and `SameSite=Lax` (or `Strict`).** Every mutation also gets its own CSRF check (Origin or `Sec-Fetch-Site`, or a token) and never runs on GET. SameSite is only defense in depth. [BAW §20, §32]
5. **Cross-origin trust is an exact-match allowlist.** CORS never reflects `Origin`, never allows `null` and never uses `*` with credentials. `postMessage` checks `event.origin` for strict equality and sends to an explicit `targetOrigin`. WebSocket handshakes check `Origin`. [BAW §19, §31]
6. **CSP uses nonces with `'strict-dynamic'`, not host allowlists**, together with `object-src 'none'`, `base-uri 'none'` and `frame-ancestors`. Roll it out in report-only mode first. [BAW §18]
7. **Tokens: prefer server sessions or HttpOnly cookies over `localStorage`.** Always *verify* a JWT (pinned algorithm, `iss`, `aud`, `exp`), never just decode it. For OAuth, use authorization code + PKCE through a vetted library. [BAW §29, §30]

**CRITICAL**: One XSS defeats every other defense here: CSRF tokens, HttpOnly (the attacker acts *as* the user without needing the cookie), and token storage. Fix XSS first, and treat CSP as a second layer, never as the fix.

---

## Decision Flowcharts

**Rendering a value from a user, the URL, an API or the CMS?**
- Plain text? → JSX `{value}`. Done.
- A URL? → Parse it with `new URL()` and allowlist the `http:`/`https:` protocol. Otherwise render a fallback.
- Must render HTML? → Sanitize with DOMPurify at render time, then use `dangerouslySetInnerHTML`. Never use a regex.
- Going into a `<script>` block? → Use `<script type="application/json">` + `JSON.parse`, or escape `<` as `\u003c`.

**Where does this auth token live?**
- You control the backend (the Next.js BFF) → server session with an HttpOnly `__Host-` cookie, and no token in JS.
- A pure SPA must call the API directly → access token in memory only, short-lived, with a rotating refresh token. Never `localStorage`.
- Third-party login → OIDC authorization code + PKCE through Auth.js or `oidc-client-ts`, with exact `redirect_uri`, and `state`/`nonce` enforced.

**Should this endpoint allow cross-origin calls?**
- Only same-origin callers → no CORS headers at all. The default is the defense.
- Public, non-credentialed data → `Access-Control-Allow-Origin: *`, without credentials.
- Specific partner origins with cookies → exact-match set + `Allow-Credentials: true` + `Vary: Origin`, plus a CSRF check anyway.

---

## Common Mistakes

| Mistake | Why it's wrong | Fix |
|---|---|---|
| `<a href={user.website}>` | `javascript:` URLs run code, and React doesn't stop them | Allowlist the protocol |
| `if (!isAdmin) return null` as the only guard | The endpoint is still callable | Check the role inside the handler or Server Action |
| JWT in `localStorage` | Any XSS exfiltrates it | HttpOnly cookie or in-memory token |
| `jwt.decode(token)` to read the user | No signature check | `jwtVerify` with pinned `algorithms`, `iss`, `aud` |
| `res.setHeader('Access-Control-Allow-Origin', req.headers.origin)` | Reflects any origin, cookies included | Exact-match allowlist + `Vary: Origin` |
| `window.addEventListener('message', e => handle(e.data))` | Any window can send messages | `if (e.origin !== TRUSTED) return;` + schema validation |
| `NEXT_PUBLIC_STRIPE_SECRET` | Inlined into the bundle | Server-only env + `import 'server-only'` |
| CSP `script-src 'self' https://cdn.example.com 'unsafe-inline'` | Bypassable through CDN gadgets and inline script | Nonce + `'strict-dynamic'` |
| `GET /api/logout` or `GET /delete?id=` | CSRF through an `<img>` or a link | POST + CSRF check |
| Login says "no such user" and reset says "email not found" | User enumeration | One generic message and identical timing |

---

## Review Checklist

- [ ] No untrusted value reaches `dangerouslySetInnerHTML`, `innerHTML`, `insertAdjacentHTML`, `eval`, `new Function`, or string-form `setTimeout`/`setInterval`
- [ ] Every user-controlled `href`/`src`/`router.push`/`window.open` passes a protocol allowlist
- [ ] Each Server Action and route handler checks the session and ownership/role itself
- [ ] Mutations never run on GET; unsafe methods check Origin/`Sec-Fetch-Site` or a CSRF token
- [ ] Session cookie is `__Host-`, `HttpOnly`, `Secure` and `SameSite`; it's regenerated at login and invalidated server-side on logout
- [ ] No tokens in `localStorage`/`sessionStorage`; JWTs verified with a pinned algorithm, `iss`, `aud` and `exp`
- [ ] OAuth uses authorization code + PKCE, exact `redirect_uri` and `state`; no implicit or password grant
- [ ] CORS is an exact allowlist, with no reflected origin, `null` or `*` with credentials, and `Vary: Origin` set
- [ ] `postMessage` receivers check `event.origin`; senders never use `'*'` with sensitive data
- [ ] CSP is nonce-based with `'strict-dynamic'`, `object-src 'none'`, `base-uri` and `frame-ancestors`
- [ ] Baseline headers present: HSTS, `nosniff`, `Referrer-Policy`, `Permissions-Policy`; no `X-Powered-By`
- [ ] No secrets in `NEXT_PUBLIC_*` or client bundles; production browser source maps off; no `.git`/`.env` served
- [ ] Error responses don't leak stack traces, SQL or internal hostnames

**IMPORTANT**: Each reference file ends with a grep-able **Review checks** list. When auditing, run those patterns across the codebase rather than only reading the files you already have open.

**NEVER:**
- Treat hidden, disabled or client-guarded UI as authorization. The endpoint behind it must reject unauthorized callers on its own.
- Sanitize HTML with a regex or a hand-rolled blocklist. Use DOMPurify, or the platform Sanitizer API where it's supported.
- Recommend `localStorage` or `sessionStorage` for access tokens, refresh tokens or session IDs.
- Use `jwt.decode()` (or `atob` on the payload) to make an auth decision. Only `verify` with pinned algorithms counts.
- Reflect the request's `Origin` into `Access-Control-Allow-Origin`, or allow the `null` origin.
- Use `'unsafe-inline'`, `'unsafe-eval'` or broad CDN hosts in `script-src` as a production CSP.
- Put a secret behind a `NEXT_PUBLIC_` prefix or import a server secret into a `'use client'` module.
- Rely on SameSite, POST-only, or "the API only accepts JSON" as the sole CSRF defense.
- Recommend `X-XSS-Protection: 1`, `Feature-Policy`, OAuth implicit grant, or the password grant. These are obsolete or insecure.
- Quote or reproduce passages from the source book. It's copyrighted. Cite it as `[BAW §N]` and paraphrase.

## Verify Security Review

- Every finding names the file and line, the attacker's input, the sink or endpoint it reaches, and the concrete fix
- Fixes use the project's own APIs (Next.js version, auth library, where headers live), confirmed in preparation step 4
- Every Review Checklist item above is marked pass, fail or not applicable, never skipped silently
- New or changed headers and CSP are tested in report-only mode, or checked in DevTools, before being called done

Security is decided on the server and at every sink: assume every byte from the browser is hostile and every byte sent to it is public.
