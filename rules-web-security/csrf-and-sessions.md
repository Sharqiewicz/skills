# CSRF, cookies & sessions

Browsers attach cookies to any request, whoever triggered it, so every state-changing endpoint needs its own CSRF defense, hardened session cookies, and server-side authorization. [BAW §20, §32, §26]

## Cookie flags

| Flag | Do | Why |
|---|---|---|
| `HttpOnly` | Always on session/auth cookies | XSS cannot read the ID. It does not stop requests made *with* the cookie, and it is useless if the ID also appears in HTML/JSON/errors. [BAW §26] |
| `Secure` | Always | Cookie never sent over plain HTTP. [BAW §26] |
| `SameSite=Lax` | Default for sessions | Cookie withheld on cross-site subresource/iframe/POST; sent on top-level GET navigation. Breaks nothing for normal apps. [BAW §32] |
| `SameSite=Strict` | Only for sensitive cookies (or a second "write" cookie) | Also withheld on inbound links, so users look logged out after clicking in from email/chat. [BAW §32] |
| `SameSite=None; Secure` | Only for deliberate cross-site embedding (widgets, third-party iframes) | Turns CSRF protection off for that cookie, so it needs tokens. Invalid without `Secure`. (updated: [MDN Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie)) |
| `__Host-` prefix | Session cookie name, e.g. `__Host-sid` | Browser enforces `Secure` + `Path=/` + no `Domain`, so a sibling subdomain cannot overwrite or fixate it. (beyond the book; [MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie), [OWASP Session](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)) |
| `Domain` | Omit (host-only cookie) | Setting it shares the cookie with every subdomain, widening the attack surface. (beyond the book; MDN) |
| `Path` | `/`; never treat it as a security boundary | It only scopes sending, not reading or protection. (beyond the book; MDN) |
| Lifetime | Session cookie or bounded `Max-Age` | See session section. |

- Unset `SameSite` means Lax in modern browsers, but do not rely on it: set it explicitly. (updated: the book says the same default; Chromium's default is a looser "Lax+POST" that also sends the cookie on cross-site POST for about two minutes after it was set, [MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie))
- "Same-site" is the registrable domain, not the origin. `a.example.com` and `b.example.com` are same-site, so a hostile or XSS-able subdomain defeats SameSite. (updated: [OWASP CSRF](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html))
- SameSite does not cover same-site attacks (stored HTML injection in the same app, sibling subdomains) or non-cookie auth (device on LAN, HTTP Basic). [BAW §20]

```ts
// ✅ Next.js
(await cookies()).set('__Host-sid', id, {
  httpOnly: true, secure: true, sameSite: 'lax', path: '/', // no domain
});
// ❌
cookies().set('sid', id);                        // defaults, guessable name
document.cookie = `sid=${id}`;                   // JS-set cookie can never be HttpOnly
localStorage.setItem('token', jwt);              // readable by any XSS
```

- Never put the session ID in a URL: it lands in logs, history and `Referer`. [BAW §26]
- Keep the ID out of response bodies, error messages and props passed to Client Components, otherwise `HttpOnly` is moot. [BAW §26]

## CSRF: what it is

- The attacker makes the victim's browser send a valid-looking request; the server cannot tell it from a real one. The attacker cannot read the response, so **protect mutations, not reads**. [BAW §20]
- Not solved by Same-Origin Policy: `<img>`, `<form>`, `<iframe>` cross-origin requests are allowed. [BAW §20]
- "We only accept POST" is a myth: auto-submitting cross-site forms send POST. A `_method=DELETE` override parameter turns POST/GET into DELETE. [BAW §20]
- XSS defeats every CSRF defense below (script reads the token and sends the request). Fix XSS first. [BAW §20] ([OWASP CSRF](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html))

## CSRF defenses (layer them)

1. **Use the framework's protection** and confirm what is *actually* enforced (generation only, or verification too?). Generating tokens without validating them server-side is a real-world bug. [BAW §20]
2. **Never change state on GET/HEAD/OPTIONS.** Lax sends cookies on cross-site top-level GET, and a refresh can re-send a blocked request. [BAW §20, §32]
   ```ts
   // ❌ app/api/account/delete/route.ts: export async function GET() { ...delete... }
   // ✅ export async function POST(req) { ...verify origin + session + authz... }
   ```
   Also reject method-override params (`_method`) unless you truly need them.
3. **Synchronizer token**: random, per-session (or HMAC-bound to the session), verified server-side on every mutation. Do not send it to other origins, and do not put it in GET URLs (leaks via history/logs/Referer). [BAW §20]
4. **SameSite cookie** is defense in depth, not the only control. Client-side-only mechanisms are an extra layer. [BAW §20, §32]
5. **Verify Origin** (fallback Referer) against your own origin on unsafe methods; if both are absent on a state-changing request, reject. (updated: [OWASP CSRF](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html))
6. **Fetch Metadata** (beyond the book): reject unsafe-method requests where `Sec-Fetch-Site` is `cross-site` (allow `same-origin`, and `none` for user-initiated), with an Origin-check fallback for clients lacking the header.
   ```ts
   // ✅ route handler / middleware guard
   const site = req.headers.get('sec-fetch-site');
   const origin = req.headers.get('origin');
   const unsafe = !['GET','HEAD','OPTIONS'].includes(req.method);
   if (unsafe) {
     const ok = site ? site === 'same-origin' || site === 'none'
                     : origin === process.env.APP_ORIGIN;
     if (!ok) return new Response('Forbidden', { status: 403 });
   }
   ```
7. **Custom header for JSON APIs** (beyond the book): require e.g. `X-CSRF-Token` or a non-simple `Content-Type: application/json` plus a custom header; cross-site pages cannot send it without a CORS preflight that you refuse. Do not enable permissive CORS with credentials. ([OWASP CSRF](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html))
8. **Stateless apps**: use signed (HMAC, session-bound) double-submit, not a naive cookie-equals-body check that cookie injection from a subdomain beats. (beyond the book; OWASP)

## Login CSRF

- Protect the login form too: otherwise the attacker logs the victim into the *attacker's* account and later reads what the victim entered (e.g. search history, card details). [BAW §20]
- Use a pre-session token on the login form, then replace the session after success. (updated: OWASP CSRF)
- OAuth: the `state` parameter must be an unguessable per-request CSRF nonce bound to the user's session, never a redirect URL or other data, or you get token theft. [BAW §20]

## New vulns introduced by CSRF protection

- Token in the URL or sent to third-party forms/links leaks it. [BAW §20]
- Token present but never verified, or only verified for some routes or some methods. [BAW §20]
- Exemptions for "webhook-like" endpoints (the WordPress comment case) become the entry point of multi-step chains. [BAW §20]
- Re-using an OAuth `state` slot for redirect data. [BAW §20]

## Next.js specifics

- **Server Actions**: POST-only, and Next.js compares `Origin` with `Host`/`X-Forwarded-Host` and aborts on mismatch. Behind a proxy/different public domain, list trusted hosts in `serverActions.allowedOrigins`; never use a wildcard that admits untrusted hosts. (updated: [Next.js data security](https://nextjs.org/docs/app/guides/data-security))
- Action IDs are obscured, but every exported action is still a public POST endpoint. Re-check authn **and** authz inside each action; a page-level redirect does not protect the action. (beyond the book; Next.js docs)
- **Route handlers (`route.ts`)** get no automatic CSRF check: add your own Origin/Fetch-Metadata/token check for every non-GET handler, and do not export state-changing `GET`. (beyond the book)
- Middleware/proxy checks are an extra layer; do authorization next to the data access (a data-access layer), not only in a matcher. (beyond the book; Next.js docs)
- Logout, cache revalidation and other mutations must not run as a side effect of rendering or a GET link: use an action (`<form action={logout}>`). (Next.js docs)
- Third-party-embedded app (iframe/widget) needing `SameSite=None`: add explicit tokens and `frame-ancestors` allowlist.

## Sessions

- Use the framework/library session mechanism; do not hand-roll signed or encrypted blobs with user data as your auth. [BAW §26]
- **Regenerate the session ID at login and on every privilege change** (session fixation: attacker plants a known ID via URL, XSS or `Set-Cookie`, then rides it after the victim logs in). [BAW §26]
  ```ts
  // ❌ keep anonymous sid, just set userId on it
  // ✅ destroy old session, issue new random ID, then attach user
  ```
- IDs: at least 128 bits from a CSPRNG (OWASP says 64 is the floor), opaque, no meaning, generic cookie name. (updated: OWASP Session). [BAW §26]
- Two timeouts: idle timeout **and** absolute lifetime, so sessions cannot be kept alive forever. Pick per risk (finance: short). [BAW §26]
- **Logout must invalidate server-side** (delete the session record), not merely clear the cookie or hide UI. Stateless JWT sessions need a revocation path (denylist or short-lived token plus refresh rotation). [BAW §26]
- Concurrent sessions: if allowed, show the user their active sessions/devices and let them revoke; for high-risk apps consider one session and alert on a second. [BAW §26]
- Session ID or password-reset token as data: validate/parameterize it like any input. [BAW §26]
- **"Remember me"**: never store login/password in a cookie; never a bare long-lived token that equals full access. Prefer not having it. If needed: separate random selector+token stored hashed server-side, single-use or rotated, limited scope, and require re-auth for critical actions. [BAW §26]

## Authentication UX that leaks

- Login failure: one generic message for wrong user or wrong password ("Invalid email or password"), same status and similar timing. [BAW §26]
- Registration/reset must not reveal whether an account exists. Reset always answers "if the address exists, we sent instructions" and do the email work asynchronously so response time does not differ. [BAW §26]
  ```ts
  // ✅ enqueue mail job, return the same response either way
  // ❌ if (!user) return { error: 'No account with this email' }
  ```
- **Password reset**: never email the password, only a reset link; token random (session-ID quality), short expiry, single-use, invalidated after use; bind the token to the user server-side and never trust a user ID in a hidden field/URL next to it (attacker resets own token and swaps the ID). Prevent the token leaking via `Referer`/analytics (`Referrer-Policy: no-referrer`, no third-party scripts on that page). [BAW §26]
- No security-question recovery; use email-link reset. [BAW §26]
- After reset/password change, invalidate other sessions. (beyond the book; OWASP Session)
- **Re-authenticate** (password or second factor) before critical actions: change email/password, disable 2FA, add payout address, admin settings. The re-auth form needs the same brute-force protection as login. [BAW §26]
- **Brute force**: stack defenses: CAPTCHA after a few failures (verify it server-side, and bind it to a server-issued challenge the client cannot choose) then soft-lock/backoff plus notify the user, rather than hard lock-out (which enables DoS on victims). Count failures in the DB per account **and** per IP, not in the session (attacker just drops the cookie). Also defend against one password across many accounts. [BAW §26]
- **2FA**: disabling it needs an independent channel/re-auth; prefer non-SMS factors (SIM swap); rate-limit code verification; check old or alternate endpoints (API, mobile, legacy) cannot skip the second step. [BAW §26]

## Authorization is server-side; hiding a button is not authorization

- UI-only checks (hidden menu items, disabled buttons, `if (user.isAdmin)` in a Client Component, route guards in the router) protect nothing: the user can call the URL, Server Action or API directly. [BAW §26]
- Decisions must rest on server-held identity and role, never on client-controlled inputs (cookie `role=admin`, hidden field, query `isAdmin`, body `userId`). [BAW §26] (Next.js docs)
- Check both vertical (role) and horizontal (is this *your* record?) access on every request, including export/download/bulk endpoints that bypass the normal screen. [BAW §26]
- **IDOR / global IDs**: fetching by `id` from URL/body without an ownership check is the classic hole. Scope queries by the session user (`where: { id, ownerId: session.userId }`), or map per-user handles to internal IDs. UUIDs reduce guessing but are not authorization. [BAW §26]
  ```ts
  // ❌ const doc = await db.doc.findUnique({ where: { id: params.id } });
  // ✅ const doc = await db.doc.findFirst({ where: { id: params.id, ownerId: session.user.id } });
  ```
- Centralize authz (one data-access/policy layer) and apply least privilege; log denied attempts too. [BAW §26]
- Mass assignment / privilege escalation: never spread request bodies into update calls; whitelist fields (`role`, `ownerId`, `post_type`-style discriminators must not be client-settable). [BAW §26]
- "Internal only" tools need the same authz as public ones. [BAW §26]

## Review checks

- Session cookie has `HttpOnly`, `Secure`, explicit `SameSite` (Lax/Strict), `__Host-` name, no `Domain`; nothing sets auth cookies from JS or stores tokens in localStorage.
- Session ID absent from URLs, HTML, JSON, error responses and logs.
- New random session ID issued on login and on privilege/2FA/password change.
- Idle and absolute timeouts exist; logout deletes the server session (and other sessions die on password change).
- No `GET` (route handler, link, prefetchable URL, `searchParams`-triggered code) changes state; no `_method` override.
- Every POST/PUT/PATCH/DELETE route handler has a CSRF check (Origin/Sec-Fetch-Site, token, or custom header); CSRF tokens are verified, not just generated.
- Server Actions: `allowedOrigins` is minimal; each action re-checks authn and authz and ownership.
- `SameSite=None` cookies have a justification and additional token protection.
- Login form is CSRF-protected; OAuth `state` is a random nonce tied to the session.
- Login/reset/registration responses and timing do not reveal whether an account exists.
- Reset tokens: random, expiring, single-use, not leaked via Referer/analytics, not paired with a client-supplied user ID.
- Re-auth required for email/password/2FA changes and other critical actions.
- Brute-force limits keyed on account+IP stored server-side; no hard permanent lockout; CAPTCHA verified server-side.
- Every data fetch/mutation filters by the current user's permissions; no authorization only via hidden or disabled UI.
- No "remember me" that stores credentials or an unhashed, non-rotating, all-powerful token.
