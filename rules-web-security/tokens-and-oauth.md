# Tokens, JWT & OAuth

Sources: [BAW §29] JWT dangers, [BAW §30] OAuth 2.0 security. Corrections and additions are marked inline.

## 1. JWT: decide first whether to use it

- Prefer a server-side session (opaque random ID in an httpOnly cookie) for a normal first-party web app. Why: instant logout/revocation, nothing to forge, no crypto choices. [BAW §29]
  (updated: OWASP says JWT sessions need their own invalidation solution, which is the main cost of "stateless" — [OWASP JWT cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_Cheat_Sheet.html))
- Use JWT where it earns its complexity: short-lived access tokens between services, tokens issued by an IdP (OIDC ID tokens), cross-domain API calls. Never use it "because everyone does".
- The standard is large (signing, encryption, key sets, many algorithms); most real bugs come from library behavior and misuse, not from the core idea. [BAW §29]

## 2. JWT pitfalls (server-side verification rules)

Payload is not secret. Base64url is encoding, not encryption. [BAW §29]
- No PII, secrets, or internal flags in claims. Need confidentiality: use server-side data behind an opaque ID (JWE only if unavoidable, and only with a maintained library).
```ts
// ❌ payload readable by anyone holding the token
sign({ sub: id, email, phone, isAdmin: true, dbPassword })
// ✅ minimal claims, look up the rest server-side
sign({ sub: id }, key, { expiresIn: "10m", issuer, audience })
```

`alg: none` and missing signatures. The spec defines unsigned tokens; some libraries accepted them, or accepted a token whose signature part was simply removed. [BAW §29]
- Whitelist the exact algorithm(s) on the verifier. Never let the token header choose.
- Test: strip the signature, set `alg` to none, flip a claim. All three must give 401.
```ts
// ❌ algorithm taken from token / library default
jwt.verify(token, key)
// ✅ pinned algorithm, issuer, audience
jwt.verify(token, key, { algorithms: ["RS256"], issuer: ISS, audience: AUD })
```

Algorithm confusion (RS256 key reused as an HMAC secret). If the verifier accepts both asymmetric and HMAC, an attacker signs with HS256 using your public key. [BAW §29]
- Pin one algorithm per key; one key = one algorithm. Also reject tokens that embed their own key (`jwk`/`jku`/`x5u` headers) and never fetch keys from a URL the token names. [BAW §29]
  (updated: [RFC 8725](https://datatracker.ietf.org/doc/html/rfc8725) and OWASP both require hard-coded algorithms.)

Weak HMAC secret. HS256 secrets can be brute-forced offline from any single token, and the server never sees it happen. [BAW §29]
- Secret: random, at least as long as the hash output, from a CSPRNG. Not a word, not an env-var default like `secret`.
- Prefer asymmetric signing (RS256/ES256/EdDSA) when more than one service verifies: verifiers hold only the public key.
- Have a key-rotation plan (`kid`, JWKS) before the first incident.
```ts
// ❌
const SECRET = process.env.JWT_SECRET ?? "dev-secret"
// ✅ fail closed, enough entropy (openssl rand -base64 32)
const SECRET = must(process.env.JWT_SECRET)
```

Decode is not verify. Many libraries expose a cheap `decode()` that skips the signature. [BAW §29]
- In any auth decision use only the verify call. `jwt-decode` in the browser is fine for reading display claims (name, expiry), never for trust or authorization.
```ts
// ❌ trusts unsigned content
const { role } = jwt.decode(token) as Claims
// ✅
const { role } = jwt.verify(token, key, opts) as Claims
```

Audience / issuer / scope confusion. A token minted for one API must not be accepted by another. [BAW §29]
- Always validate `iss`, `aud`, `exp`, `nbf`; (beyond the book) check an explicit token type (`typ`, e.g. access vs ID token) so an ID token cannot be replayed as an access token. [RFC 8725](https://datatracker.ietf.org/doc/html/rfc8725)

Expiry, replay, revocation. A stolen bearer token is full access until `exp`; the format has no built-in revocation. [BAW §29]
- Short access-token lifetime (minutes), refresh tokens handled per section 4.
- Need logout-everywhere or kill-on-compromise: keep a server-side denylist keyed by `jti`, or a per-user "tokens valid after" timestamp. (beyond the book) Do not denylist by raw token hash.
- One-time-use tokens (email verify, password reset): store `jti` server-side and consume it.

Other
- Compare signatures in constant time (library does this; do not hand-roll `===` on signatures). [BAW §29]
- Never send tokens in URLs (logs, Referer, history). Use the `Authorization` header or a cookie. [BAW §29, §30]
- Do not return the expected signature or stack traces on verify failure; return a generic 401 and turn debug off in production. [BAW §29]
- Library sprawl: use one maintained library (e.g. `jose`), pin it, watch its advisories, and do not write your own parser. A small or abandoned JWT package is a finding. [BAW §29]
  (beyond the book) Alternatives such as PASETO exist but have a far smaller ecosystem; the book called it too young to recommend.

## 3. Where a browser keeps the token

No option is safe against XSS; choose what limits the damage. [BAW §30]

| Storage | XSS | CSRF | Verdict |
|---|---|---|---|
| httpOnly + Secure + SameSite cookie | Script cannot read it, but can still make authenticated requests from the page | Needs SameSite and/or CSRF token | Default choice |
| localStorage / sessionStorage | Any injected script reads and exfiltrates it, it works from anywhere | Not affected | Avoid for long-lived or refresh tokens |
| In-memory variable | Harder to steal persistently, still reachable by running script | Not affected | Acceptable for short access tokens, lost on reload |

- ✅ Session or token in a cookie: `HttpOnly; Secure; SameSite=Lax` (or Strict), narrow `Path`, `__Host-` prefix when possible.
  ```ts
  cookies().set("__Host-session", id, { httpOnly: true, secure: true, sameSite: "lax", path: "/", maxAge: 3600 })
  ```
- Cookies + state-changing requests need CSRF defense: SameSite, plus an Origin check or token for non-GET. (Next.js Server Actions already compare Origin and Host, [docs](https://nextjs.org/docs/app/guides/data-security).)
- (updated) The current browser-app guidance ranks architectures: a backend-for-frontend (BFF) that holds tokens server-side and gives the browser only a session cookie is strongest; a token-mediating backend next; tokens fully in the browser last. Injected script can act with the user's privileges in every case, so architecture decides what can be stolen and for how long. [OAuth for browser-based apps](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps)
- ❌ `localStorage.setItem("token", jwt)` for something long-lived. XSS elimination (CSP, sanitization) is a precondition for any browser-held token.
- Clear tokens and call the revoke endpoint on logout; do not just drop the UI state.

## 4. OAuth 2.0 / OIDC in an SPA or Next.js app

Login is OIDC, not plain OAuth. OAuth delegates access; holding an access token does not prove who the user is. Use OpenID Connect (ID token, `nonce`) for sign-in. [BAW §30]

- ✅ Authorization Code flow with PKCE, for public clients (SPA, mobile) and confidential ones alike. [BAW §30]
  (updated: the book lists implicit grant as the choice for in-browser JS. Current Security BCP says not to use implicit or any response type that returns tokens in the authorization response; PKCE is mandatory for public clients and recommended for confidential. [RFC 9700](https://datatracker.ietf.org/doc/html/rfc9700))
- ❌ `response_type=token`. ❌ Resource-owner password grant (client collects the user's password; the BCP forbids it). [BAW §30]
- Exact `redirect_uri` match against a pre-registered list. No wildcards, no prefix or pattern matching, no open redirects on any registered host, since redirect-URI flaws plus open redirects were behind several major account-takeover chains. [BAW §30]
  (updated: RFC 9700 requires exact string comparison, with only the loopback port allowed to vary for native apps.)
- `state` (unguessable, bound to the user's session, one-time, compared strictly) or PKCE/`nonce` as CSRF protection for the login callback. A missing or null `state` must fail, not skip the check. [BAW §30]
- Validate the ID token like any JWT (section 2): issuer, audience = your client ID, expiry, `nonce`.
- Request least-privilege scopes, split by resource and by read/write, and let the API enforce scopes on every call, not only at consent. [BAW §30]
- Code is single-use and short-lived; tokens bound to a client; never keep the client secret in a SPA, bundle, or mobile app. [BAW §30]
- Tokens never in URLs except the one-time `code`; strip it from history after exchange (`history.replaceState`). Set `Referrer-Policy` so the callback URL does not leak. [BAW §30]
- Refresh tokens for public clients: rotate on use or bind to the sender, cap total lifetime. (updated: RFC 9700, browser-based-apps draft)
- (beyond the book) Multiple identity providers: check the `iss` response parameter ([RFC 9207](https://www.rfc-editor.org/rfc/rfc9207)) to stop mix-up attacks. Sender-constraining (DPoP / mTLS) makes stolen tokens less useful.
- Consent phishing: attackers register lookalike app names and ask users for broad mail/drive scopes. In your own IdP/consent UI show the client name clearly, verify publishers, restrict who can register apps, and let users review and revoke grants. In org tenants, limit user consent to verified apps. [BAW §30]
- Use a vetted library; do not hand-write the protocol or token validation. [BAW §30]
  ```ts
  // ✅ Auth.js / NextAuth: server-side sessions, httpOnly cookie, PKCE+state handled
  export const { auth, handlers } = NextAuth({ providers: [Google] })
  // ❌ hand-built: fetch(`${idp}/authorize?response_type=token&...`) + parse location.hash
  ```
  Browser-only SPA: a maintained client such as `oidc-client-ts` with code+PKCE. Keep the library patched; OAuth modules have had RCE and SSRF bugs. [BAW §30]
- The authorization server is itself a web app: injection, headers, brute-force protection, hashed token storage, per-client token binding, revocation endpoint, user-visible grant management. Relevant only if you run one. [BAW §30]

## 5. Mobile / native (brief)

- System browser (ASWebAuthenticationSession, Custom Tabs), not an embedded WebView: WebView shows no address bar, breeds credential-phishing habits, and the host app can read what the user types. [BAW §30]
- Code flow with PKCE, custom scheme or (better) verified app/universal links as redirect. [BAW §30]
- A client secret shipped in a mobile app is public; treat the client as public. [BAW §30]
- Store tokens in Keychain / Keystore, not plain preferences. (beyond the book)

## Review checks

- [ ] Is JWT actually needed here, or would a server session do? Logout/revocation story exists?
- [ ] Verifier pins `algorithms`; rejects `none`, missing signature, and header-supplied keys.
- [ ] `verify` (not `decode`) on every trust decision; `iss`, `aud`, `exp` validated.
- [ ] HMAC secret is random, long, from a secret store, never a default in code; rotation possible.
- [ ] No sensitive data in payload; tokens not in URLs or logs; verify errors generic.
- [ ] Access tokens short-lived; refresh tokens rotated or sender-bound; revocation path exists.
- [ ] Browser token storage is cookie (httpOnly/Secure/SameSite) or memory; no long-lived token in localStorage.
- [ ] Cookie-authenticated mutations have CSRF protection (SameSite + Origin/token).
- [ ] OAuth uses code + PKCE; no implicit, no password grant; exact redirect URI; `state`/`nonce` enforced.
- [ ] OIDC (not bare OAuth) for login; ID token validated; scopes minimal and enforced on the API.
- [ ] Maintained library (Auth.js, `jose`, `oidc-client-ts`) and up to date; no client secret in client code.
- [ ] Mobile: system browser + PKCE, no WebView login, Keychain/Keystore storage.
