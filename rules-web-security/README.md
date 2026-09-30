# rules-web-security

Claude Code skill for frontend and full-stack web security in React, Next.js and TypeScript. It's distilled from Securitum's *Bezpieczeństwo aplikacji webowych* (paraphrased and cited as `[BAW §N]`) and checked against current OWASP and MDN guidance.

## What it covers

- **XSS**: dangerous sinks, `javascript:` URLs, DOMPurify, and safe SSR state serialization → `xss.md`
- **CSP and security headers**: nonce + `strict-dynamic`, HSTS, `nosniff`, `Referrer-Policy`, `Permissions-Policy`, and clickjacking → `csp-and-headers.md`
- **Cross-origin**: SOP, CORS allowlists, `postMessage`, and WebSocket origin checks → `cross-origin.md`
- **CSRF and sessions**: `__Host-` cookies, SameSite, Origin/`Sec-Fetch-Site` checks, and authorization in Server Actions → `csrf-and-sessions.md`
- **Tokens and OAuth**: JWT verification, token storage, and authorization code + PKCE → `tokens-and-oauth.md`
- **Exposure**: `NEXT_PUBLIC_*` secrets, source maps, and `.git`/`.env` in the web root → `exposure.md`

Each reference file ends with a grep-able **Review checks** list.

## Activation

The skill activates automatically when you mention terms such as `XSS`, `dangerouslySetInnerHTML`, `CSP`, `CORS`, `postMessage`, `CSRF`, `SameSite`, `JWT`, `OAuth`, `PKCE`, `localStorage token` or `NEXT_PUBLIC`. You can also invoke it directly with `/sharqiewicz:rules-web-security`.
