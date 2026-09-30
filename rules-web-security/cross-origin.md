# Cross-origin: SOP, CORS, postMessage, WebSocket

Cross-origin access is opt-in and enforced by the browser only; every allowlist you write (CORS, postMessage, WebSocket Origin) is a server/app decision that must be exact, and none of it replaces auth or CSRF defenses. Sources: [BAW §19] (SOP/CORS), [BAW §31] (WebSocket); MDN [CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS), OWASP HTML5 Security / WebSocket cheat sheets.

## 1. Origin and what SOP does and doesn't block [BAW §19]

- Origin = scheme + host + port, compared strictly. `app.example.com` != `example.com`; `http` != `https`; different port = different origin.
- Rule of thumb: cross-origin **writes** (send a request) and **embeds** (img, script, iframe, form target) are generally allowed; cross-origin **reads** of the response are blocked unless the server opts in.
- Consequence: SOP does NOT stop CSRF. A cross-origin GET or simple POST is still executed by the server; the page just can't read the answer. Never rely on CORS to protect state-changing endpoints.
- Consequence: a blocked read still leaks side channels (timing, frame count, response size). Don't let sensitive, cookie-authenticated endpoints be triggerable by GET or simple POST.
- XSS turns everything same-origin: no CORS/CSRF token defense survives XSS on any origin you trust. Every origin you allow via CORS inherits the XSS risk of that origin.
- SOP is browser-only. curl, servers and native clients ignore it, so `Origin` checks are not authentication.
- Server-side "proxy to bypass CORS" endpoints: SSRF risk. Allowlist target hosts, block private/loopback ranges, never forward user cookies. Prefer a fixed-upstream route handler over a generic `?url=` proxy.
- Legacy flash/`crossdomain.xml` policies: dead tech, delete any remnants.

## 2. Simple vs preflighted requests [BAW §19]

- Simple = GET/HEAD/POST + only safelisted headers + Content-Type limited to form-urlencoded, multipart/form-data, text/plain. Sent immediately, no preflight; the server executes it even if the browser then hides the response.
- Anything else (custom header like `Authorization`/`X-*`, `Content-Type: application/json`, PUT/PATCH/DELETE) triggers an `OPTIONS` preflight carrying `Access-Control-Request-Method/Headers`. If preflight fails, the real request is never sent.
- (updated: `Range` is now a safelisted request header; the book's list with DPR/Width/Viewport-Width is outdated. See MDN CORS link above.)
- Design implication: require `Content-Type: application/json` or a custom header (e.g. CSRF token) on mutating endpoints so forged cross-site requests need a preflight you can refuse. Reject mutations sent as `text/plain`/form bodies when the API is JSON-only.
- Preflight is not authorization: the actual request still needs its own authn/authz. Don't reason "the preflight passed so the caller is trusted".
- `Access-Control-Max-Age` caches preflights (browsers cap it); fine for perf, but remember cached permissions outlive config changes.
- `Access-Control-Expose-Headers` only when the client JS truly needs non-safelisted response headers.

## 3. Credentials in CORS [BAW §19]

- Cookies/`Authorization` are sent cross-origin only if the client opts in (`fetch(..., { credentials: 'include' })`, XHR `withCredentials`) AND the server answers `Access-Control-Allow-Credentials: true` with an explicit origin.
- With credentials, `Access-Control-Allow-Origin` cannot be `*`; (updated: the same ban applies to `*` in Allow-Headers, Allow-Methods and Expose-Headers. Source: MDN CORS link.)
- Missing ACAC on a credentialed simple request: request (with cookies) still executes, response is withheld. On a preflighted one: the real request is never sent.
- `*` is weak-by-design safe for public, unauthenticated data. It is dangerous only for location-based trust (intranet/IP-allowlisted services), since the victim's browser reaches them.
- Default to no credentials. Use `credentials: 'include'` only for a first-party API you fully control, from an allowlisted origin.

```ts
// ❌ cross-site cookie API with blanket opt-in
fetch('https://api.other.com/me', { credentials: 'include' }) // other.com not controlled by you
// ✅ public data, no ambient authority
fetch('https://api.other.com/public', { credentials: 'omit' })
```

## 4. Server-side CORS misconfigurations [BAW §19]

- Wildcard `*` on anything non-public. ❌ `Access-Control-Allow-Origin: *` on an API that serves user data by IP/network trust.
- Reflecting the request `Origin` = wildcard that *also* works with cookies. The most common critical bug.
- Prefix/suffix/substring/regex checks. Attackers register lookalike hosts.
  - ❌ `origin.startsWith('https://example.com')` matches `https://example.com.evil.net`
  - ❌ `origin.endsWith('example.com')` matches `notexample.com`
  - ❌ unescaped dot in regex (`/^https:\/\/app.example.com$/`) matches `appXexample.com`
  - ❌ `origin.includes('example.com')`
  - ✅ exact match against a `Set` of full origins (scheme+host+port); if wildcard subdomains are required, parse with `new URL()`, require `https:`, and compare `hostname` to `example.com` or `endsWith('.example.com')` (leading dot), accepting the risk of any subdomain takeover/XSS.
- `null` origin: sent from sandboxed iframes, `file:`, data URLs, some redirects. Allowing `null` = allowing any attacker page. Also guard against an unset variable serializing to the string `null`/`undefined`.
- Over-trusting third parties: each allowed origin (partner, CDN, staging, preview deploys, `localhost`) can read authenticated responses if it has XSS. Keep the list minimal, per-route, and env-specific (no `localhost` in production).
- Missing `Vary: Origin` when ACAO is dynamic (or varies at all): caches serve one origin's CORS headers to another, and combined with a reflected-header bug this enables cache poisoning. Always send `Vary: Origin` with any non-static ACAO. The book advises it even for static values. (updated: MDN only requires it for dynamically-chosen ACAO; adding it always is harmless.)
- Validate/sanitize the `Origin` value before echoing into headers (header injection/splitting).
- Allowing `*`-style ACAO plus reflecting headers/methods from `Access-Control-Request-*` is the same bug as reflecting Origin. Allowlist them.

```ts
// ❌ reflect
res.setHeader('Access-Control-Allow-Origin', req.headers.origin ?? '*')
res.setHeader('Access-Control-Allow-Credentials', 'true')

// ✅ exact allowlist + Vary
const ALLOWED = new Set(['https://app.example.com', 'https://admin.example.com'])
const o = req.headers.origin
if (o && ALLOWED.has(o)) {
  res.setHeader('Access-Control-Allow-Origin', o)
  res.setHeader('Access-Control-Allow-Credentials', 'true')
}
res.setHeader('Vary', 'Origin')
```

### Next.js / framework notes

- Route handlers (`app/api/**/route.ts`) have no automatic CORS: export an `OPTIONS` handler and add headers to every response, including errors and redirects. Put the allowlist helper in one module; don't sprinkle `*`.
- `headers()` in `next.config` is static: fine only for fixed public values; it cannot do per-request origin allowlisting, use middleware or the handler. Note that `Access-Control-Allow-Origin: *` set globally there covers HTML and API routes alike.
- Prefer same-origin: call your own route handlers / Server Actions from the UI, or use a `rewrites()` proxy to the backend, and you need no CORS and no credentials opt-in.
- Use a maintained CORS library/framework feature over hand-rolled string checks when one exists [BAW §19].
- Dev-only workarounds (proxy, header-rewriting extensions) must not leak into prod config [BAW §19].
- (beyond the book) `Sec-Fetch-Site` / `Sec-Fetch-Mode` request headers let the server reject cross-site requests to cookie-authenticated endpoints independent of CORS.

## 5. JSONP [BAW §19]

- Script-tag based, non-standard hack: no origin control, any site can read the data, and the `callback` param is an injection point (XSS, CSP bypass).
- ✅ Replace with CORS (or same-origin proxy). ❌ Never add a new JSONP endpoint; if legacy one remains, strict-validate callback (`/^[A-Za-z_$][\w$.]*$/`), no cookies/PII, `Content-Type: application/javascript`, `X-Content-Type-Options: nosniff`.
- Related read leaks: JSON array top-level responses and GET endpoints returning secrets. Return objects, require non-simple headers/POST for sensitive reads.
- CSP `script-src` allowing a host with a JSONP endpoint is a known CSP bypass; don't allowlist such hosts (see the CSP reference).

## 6. postMessage [BAW §19]

- Receiver: ALWAYS check `event.origin` with exact equality against an allowlist (never `indexOf`, `includes`, `endsWith`, regex-by-default), and check `event.source` when you know which window should talk.
- Sender: ALWAYS pass an explicit `targetOrigin`. Never `'*'` when the payload contains tokens, PII or auth state: any page that navigated the target window (or embedded frame) receives it.
- Treat `event.data` as untrusted input: validate type/shape (schema, e.g. zod), never pass it to `innerHTML`, `eval`, `location`, `dangerouslySetInnerHTML`, or unsanitized URLs.
- Prefer structured objects with a `type` discriminator over string parsing. Ignore unknown types.
- In React, register in `useEffect` and remove in cleanup, otherwise duplicate handlers run.
- Don't use messages as a substitute for auth: a check on origin says *which site*, not *which user*.

```ts
// ❌
window.addEventListener('message', e => { el.innerHTML = e.data })
parent.postMessage({ token }, '*')

// ✅
const TRUSTED = 'https://widget.example.com'
const Msg = z.object({ type: z.literal('resize'), height: z.number().int().min(0).max(5000) })
useEffect(() => {
  const h = (e: MessageEvent) => {
    if (e.origin !== TRUSTED || e.source !== frameRef.current?.contentWindow) return
    const m = Msg.safeParse(e.data); if (!m.success) return
    setHeight(m.data.height)
  }
  window.addEventListener('message', h)
  return () => window.removeEventListener('message', h)
}, [])
frameRef.current?.contentWindow?.postMessage({ type: 'init' }, TRUSTED)
```

- Sandboxed iframes have opaque `null` origin: don't "fix" by allowing `'null'`; give the frame `allow-same-origin` only if you accept the trade-off, or identify it via `event.source`.

## 7. window.opener, noopener, isolation

- (beyond the book) `target="_blank"` links to untrusted pages: a page opened this way may get `window.opener` and could navigate the opener (tabnabbing). Modern browsers default `_blank` to `noopener`, but keep `rel="noopener noreferrer"` explicitly for user-supplied/third-party URLs and for `window.open(url, '_blank', 'noopener')`. `noreferrer` also hides the referrer (may leak paths/tokens in URLs).
- (beyond the book) Isolation headers limit cross-origin window/resource interaction and side channels:
  - `Cross-Origin-Opener-Policy: same-origin` severs opener relationships (popups/XS-Leaks, enables cross-origin isolation).
  - `Cross-Origin-Embedder-Policy` (`require-corp`/`credentialless`) + COOP = cross-origin isolated context (needed for `SharedArrayBuffer`); audit third-party embeds before enabling.
  - `Cross-Origin-Resource-Policy: same-site|same-origin` on sensitive/authenticated resources blocks no-cors embedding by other origins (Spectre-class and leak mitigation). (sources: MDN COOP/COEP/CORP pages)
  - `X-Frame-Options`/CSP `frame-ancestors` for clickjacking (see the headers reference).
- (beyond the book) Private Network Access (updated: Chrome is moving from the preflight-based `Access-Control-Request/Allow-Private-Network` to a user-permission prompt for public sites reaching local/private addresses; don't build new designs on the preflight header; devices/dev servers reachable on LAN/localhost must still authenticate every request, as CORS/PNA are not auth. Source: [Chrome LNA](https://developer.chrome.com/blog/local-network-access)).

## 8. WebSocket [BAW §31, §19]

- WebSocket is not covered by SOP or CORS: any page can open `new WebSocket('wss://your-api')` and the browser attaches your cookies for that host. Result: Cross-Site WebSocket Hijacking (CSWSH), the WebSocket form of CSRF, with a read channel.
- ✅ Validate `Origin` on the handshake against an exact allowlist; reject (403) missing/unknown origins for browser-facing sockets. Non-browser clients can forge `Origin`, so this complements, never replaces, auth [BAW §31].
- ✅ Authenticate on connect, and do not rely on cookies alone: use a short-lived, single-use ticket/token obtained via an authenticated HTTPS call, passed in the first message or a subprotocol (not a long-lived JWT in the query string, which gets logged). If cookie auth is used, Origin check (or CSRF-style token in the ticket) is mandatory, and cookies should be `SameSite` Lax/Strict.
- ✅ Authorize per message/action and per resource (channel, room, object ID), not just at connect. Re-check when permissions or sessions change; close sockets on logout/expiry.
- ✅ Treat every frame as untrusted input: parse safely, schema-validate, cap size, reject unknown message types; escape before rendering (never `innerHTML` a received message) [BAW §31].
- ✅ `wss://` only (TLS); never `ws://` outside localhost dev. Don't ship mixed content.
- ✅ Limits: max connections per user/IP, message rate limits, max payload size, idle timeout/heartbeat, backpressure; connections are long-lived, so resource exhaustion is easier than with HTTP [BAW §31].
- ✅ Use a maintained server library (e.g. a well-known socket framework) rather than a custom protocol implementation; firewall the WS port to the intended entry point (proxy) [BAW §31].
- Also restrict `connect-src` in CSP to your own `wss:` endpoints [BAW §31].
- (beyond the book) Socket.IO/other libs have their own CORS/origin options: set them explicitly, never `origin: '*'` or `true` with credentials.

```ts
// ❌ server accepts any origin, trusts cookie, no per-message authz
wss.on('connection', (ws, req) => ws.on('message', m => handle(JSON.parse(m), ws.user)))

// ✅ verify at handshake, then validate every message
const ALLOWED = new Set(['https://app.example.com'])
server.on('upgrade', async (req, socket, head) => {
  if (!ALLOWED.has(req.headers.origin ?? '')) return socket.destroy()
  const user = await consumeTicket(new URL(req.url!, 'http://x').searchParams.get('ticket'))
  if (!user) return socket.destroy()
  wss.handleUpgrade(req, socket, head, ws => wss.emit('connection', ws, req, user))
})
ws.on('message', raw => {
  if (raw.length > 16_384) return ws.close(1009)
  const m = Msg.safeParse(safeJson(raw)); if (!m.success) return
  if (!can(user, m.data.action, m.data.resourceId)) return
})
```

## Review checks

- [ ] Any `Access-Control-Allow-Origin` that reflects `Origin`, uses `*` with non-public data, or is computed via startsWith/endsWith/includes/regex instead of exact-set match.
- [ ] `Access-Control-Allow-Origin: null`, or code that can emit `null`/`undefined`, or allows `localhost`/preview hosts in prod.
- [ ] Dynamic ACAO without `Vary: Origin`.
- [ ] `Allow-Credentials: true` paired with broad/dynamic origins; `credentials: 'include'` toward origins not owned by the team.
- [ ] Preflight handler (`OPTIONS`) missing or returns permissive headers for everything; `Allow-Headers/Methods` reflected from request.
- [ ] State-changing endpoints accept simple requests (form/`text/plain` bodies) without CSRF token or custom-header/JSON-only requirement; GET endpoints with side effects.
- [ ] Next.js route handlers/middleware/`next.config` headers set CORS globally or differ between success and error paths.
- [ ] Generic `?url=` proxy endpoints (SSRF), JSONP endpoints or `script-src` allowlisting JSONP hosts, top-level JSON arrays with secrets.
- [ ] `message` listener without strict `event.origin` equality (and `event.source` where possible); `postMessage(..., '*')` with sensitive data; unvalidated `event.data` reaching DOM sinks.
- [ ] `target="_blank"`/`window.open` with untrusted URLs lacking `noopener`; missing COOP/CORP on sensitive apps where appropriate.
- [ ] WebSocket upgrade handler without `Origin` allowlist; cookie-only auth; token in long-lived query string; authz only at connect; no frame schema/size validation; `ws://` in non-dev; no connection/message rate limits; `innerHTML` of received data.
- [ ] Reliance on CORS/Origin as if it were authentication or CSRF protection for non-browser-reachable endpoints.
