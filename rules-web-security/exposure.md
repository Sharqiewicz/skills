# What the browser (and the server) gives away

Sources: [BAW §13] DevTools and static JS analysis, [BAW §16] hidden files and directories. Corrections and additions are marked inline.

Mental model: anything delivered to the browser is public and editable by the user. Anything deployed under the web root is public too. Design as if an attacker already holds a formatted copy of your JS and a list of your files. [BAW §13, §16]

## 1. The client bundle is public

- No secrets in client code: API keys with write or billing power, DB URLs, private keys, signing secrets, admin endpoints, feature-flag "backdoors". Minification is not protection; one click in DevTools pretty-prints it, and global search spans every loaded file. [BAW §13]
- In Next.js, `NEXT_PUBLIC_*` values are inlined into the JS at build time, so they are public by definition. Unprefixed vars stay on the server. [docs](https://nextjs.org/docs/app/guides/environment-variables) (beyond the book)
  ```ts
  // ❌ secret shipped to every visitor
  NEXT_PUBLIC_STRIPE_SECRET_KEY=sk_live_...
  // ✅ public identifier only in NEXT_PUBLIC_, secret read on the server
  NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!) // server only
  ```
  The same holds for Vite (`VITE_*`), CRA (`REACT_APP_*`), and anything in a `define` block.
- "Public" third-party keys (maps, analytics, Firebase config) are acceptable only when restricted on the provider side (allowed origins, quotas, scoped rules). An unrestricted key in the bundle is a finding.
- Keep server-only code out of client bundles: `import "server-only"` in modules that touch secrets or DB, and read `process.env` only in a data-access layer. (beyond the book, [Next.js data security](https://nextjs.org/docs/app/guides/data-security))
- Props from Server to Client Components are serialized into the page. Pass minimal DTOs, never whole DB rows. Same for Server Action return values. (beyond the book)
  ```tsx
  // ❌ whole record, including passwordHash, reaches the browser
  <Profile user={userRow} />
  // ✅
  <Profile user={{ name: userRow.name }} />
  ```
- Comments, `console.log` debug output, hidden `iframe`s, internal URLs and TODO notes in shipped code are all readable. Strip logs and comments from production builds, never leave credentials "for testing". [BAW §13]
- Hidden UI is not access control: CSS-hidden or never-rendered elements, admin routes that only the menu hides, and "unlisted" URLs are all visible in source or the DOM. The Elements panel shows the live DOM (including JS-generated nodes), the Sources panel shows what was delivered. [BAW §13]

## 2. Source maps in production

- Source maps reverse a minified bundle into your original files and names, and make static analysis trivial. [BAW §13]
- Next.js does not emit browser source maps in production unless `productionBrowserSourceMaps: true`. Leave it off. [docs](https://nextjs.org/docs/app/api-reference/config/next-config-js/productionBrowserSourceMaps) (updated: a framework default the book could not assume)
  ```js
  // ❌ next.config.js
  module.exports = { productionBrowserSourceMaps: true }
  ```
- Need maps for error tracking (Sentry etc.): upload them to the vendor in CI, then delete `*.map` from the deploy artifact, or serve them only behind auth. Check for a `sourceMappingURL` comment at the end of shipped JS. (beyond the book)
- Verify after build: `find .next/static -name "*.map"` and `curl -I https://site/_next/static/.../x.js.map` must be empty or 404.

## 3. Files that must not be reachable on the web server

Attackers run wordlist scanners for these; a 403 instead of a 404 already confirms they exist. [BAW §16]

- `.git/`: lets an attacker rebuild the whole source tree and history (including deleted secrets) even without directory listing, because object and log paths are predictable. `.svn/` (metadata DB plus stored pristine copies) works the same way. Source access usually means DB credentials and new bugs to find. [BAW §16]
- IDE and tooling dirs: `.idea/` (JetBrains workspace files list project structure, history, sometimes DB connections), `.vscode/`, `nbproject/`; node ecosystem rc/config files (`.npmrc`, `.eslintrc`, `.bowerrc`). [BAW §16]
- `package.json`, `package-lock.json`, `bower.json`: reveals exact dependencies, so an attacker can run an audit against you. [BAW §16]
- CI config: `.gitlab-ci.yml`, workflow files, Dockerfiles, `docker-compose.yml` often hold tokens, hostnames, deploy details. [BAW §16]
- `.env*`, `config/database.yml`-style files, backups (`*.bak`, `*.old`, `*.sql`, `*.zip`), editor swap files. (beyond the book)
- `.DS_Store`: macOS metadata that lists names of files in a directory, including ones not linked anywhere. Gets committed by accident. [BAW §16]

How to block (defense in depth; the best fix is not deploying them):
- Deploy only build output: Next.js `standalone`/`.next`, Vite `dist/`, a container image built from a clean context with `.dockerignore`. Never `git clone` into the web root or rsync the repo folder.
- Put these in `.gitignore` and `.dockerignore`: `.env*`, `.DS_Store`, `.idea/`, `*.map` (if not needed), `*.pem`.
- Anything in Next.js `public/` is served verbatim. Keep it to intentionally public assets.
  ```nginx
  # ✅ deny dotfiles and common leftovers, allow ACME/.well-known
  location ~ /\.(?!well-known) { deny all; return 404; }
  location ~* \.(env|bak|old|sql|swp|map)$ { deny all; return 404; }
  ```
  ```nginx
  # ❌ static root that is the repo checkout, autoindex on
  root /var/www/app; autoindex on;
  ```
- Turn off directory listing; return 404 (not 403) for denied paths so presence is not confirmed.
- Scan your own deployment with a dotfile wordlist (dirb, ffuf, nuclei) as part of release checks. [BAW §16]

## 4. Errors, debug modes, verbose output

- Production must not show stack traces, SQL errors, file paths, framework versions, or request dumps. Log in detail server-side, send the user a generic message and an ID. [BAW §29]
- Debug toggles (`?debug=true`, dev mode, GraphQL introspection/playground, Swagger UI, `/actuator`, `/phpinfo`) must be off or authenticated in production. [BAW §29] (beyond the book for GraphQL/Swagger)
  ```ts
  // ❌ leaks internals
  return Response.json({ error: err.stack, query: sql }, { status: 500 })
  // ✅
  logger.error({ err, reqId }); return Response.json({ error: "Internal error", reqId }, { status: 500 })
  ```
- Next.js: error details are hidden from the client in production builds; do not re-add them in custom error handlers or Route Handlers. Remove `X-Powered-By` (`poweredByHeader: false`). (beyond the book)

## 5. Client-side checks are not security

- Everything the user's browser enforces (disabled buttons, regex validation, `maxLength`, role checks in React, hidden fields, price in a hidden input, `if (isAdmin)` in JS) can be changed in DevTools, by editing JS, or by sending the request by hand. [BAW §13]
- Re-check on the server, per request: authentication, authorization (this user, this resource), validation, prices and totals, rate limits. Next.js Server Actions and Route Handlers are public POST endpoints; re-authorize inside each one, and never trust `searchParams` or headers for trust decisions. [docs](https://nextjs.org/docs/app/guides/data-security)
  ```ts
  // ❌ client says who it is
  if (searchParams.isAdmin === "true") return <AdminPanel />
  // ✅ server derives it from the session
  const s = await auth(); if (!s?.user.isAdmin) redirect("/login")
  ```
- Client validation is UX only; the rule is "validate in both, trust one".
- Client-side route guards (middleware-less redirects, `useEffect` auth redirect) only hide UI. The data endpoint must refuse.

## 6. Storage is user-visible and user-editable

- Cookies, localStorage, sessionStorage, IndexedDB and service workers can be read and modified in the Application panel. Swapping a cookie value to impersonate a session is the standard first test. [BAW §13]
- So: store no secrets or PII there; never store role/price/"isAdmin" and trust it on the way back; session IDs must be unguessable and bound to server state; cookies carry `HttpOnly`, `Secure`, `SameSite`. See `tokens-and-oauth.md` for token storage.
  ```ts
  // ❌ trusted on return
  localStorage.setItem("role", "admin")
  // ✅ UI hint only; server re-derives role from the session each request
  ```
- Clear user data in storage on logout and on shared-device flows.

## 7. Dependencies and supply chain

- A leaked manifest turns into a precise vulnerability list, and even without a leak the bundle shows library names and versions. Keep dependencies patched. [BAW §16]
- Run `npm audit` (or pnpm/yarn equivalent) in CI and fail on high/critical in production dependencies; review before `audit fix --force`. [BAW §16] (beyond the book: also Dependabot/Renovate.)
- Commit the lockfile; install with `npm ci` (or frozen-lockfile) in CI and deploys so builds are reproducible.
- Review new packages (maintainers, download history, install scripts, typosquats); minimize count. Prefer `--ignore-scripts` where feasible. (beyond the book)
- Third-party scripts run with full page power: pin versions, self-host where possible, use Subresource Integrity on CDN tags and a CSP. (beyond the book)
- Remove unused packages and dead routes; they widen attack surface without value.

## Review checks

- [ ] No secret, private key, or unrestricted API key in client code, `NEXT_PUBLIC_*`/`VITE_*` vars, or the bundle (grep the build output).
- [ ] `productionBrowserSourceMaps` off; no `.map` files or `sourceMappingURL` in the deployed output (or maps uploaded to error tracker and removed).
- [ ] Secret-touching modules use `server-only`; props and action results are minimal DTOs.
- [ ] Deploy artifact is build output only; `.git`, `.env*`, `.idea`, `.DS_Store`, CI files, backups, `package.json` are not reachable (probe them on staging).
- [ ] Web server denies dotfiles, disables directory listing, returns 404 for blocked paths.
- [ ] `.gitignore` and `.dockerignore` cover env files, OS/IDE files, keys.
- [ ] Production errors are generic with a correlation ID; no debug toggles, introspection, or Swagger open; `X-Powered-By` off.
- [ ] Every client-side check (validation, role gate, hidden field, price) has a server-side equivalent; Server Actions and Route Handlers authenticate and authorize themselves.
- [ ] Nothing trusted from cookies, localStorage, hidden inputs or query strings without server verification.
- [ ] Shipped JS has no debug logs, credential comments, or internal hostnames.
- [ ] Lockfile committed, `npm ci` in CI, `npm audit` gate, automated dependency updates; third-party scripts pinned with SRI/CSP.
