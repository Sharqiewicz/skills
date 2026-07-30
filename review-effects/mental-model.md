# Mental Model: Effects and React's Rendering Model

## Effects are synchronisation, not lifecycle hooks

The key mental shift: **effects run *after* render to sync React with an external system**. They are not "run on mount" hooks.

Wrong mental model:
> "I want to do X when the component mounts" → `useEffect(() => { doX() }, [])`

Right mental model:
> "My component needs to stay in sync with an external system Y. When Y needs to connect, I start the connection. When Y needs to disconnect, I clean up."

If there is no external system to sync with, `useEffect` is almost certainly the wrong tool.

---

## The rendering model

React rendering is **pure**:
- `render` (the component function body) must be a pure function: same inputs → same output, no side effects
- Side effects — things that reach outside React's world (DOM, network, timers, subscriptions) — belong in effects, not in render

The rendering cycle:
1. **Trigger** — state/props change
2. **Render** — React calls your component function (pure, no side effects)
3. **Commit** — React updates the DOM
4. **Effect** — React runs effects after the DOM is painted

Effects are the **escape hatch** for side effects after render. They are not part of rendering.

---

## Effect lifecycle

```
Mount
  └── run effect → return cleanup fn (or nothing)

Re-render (dependency changed)
  └── run cleanup from previous effect
  └── run new effect → return cleanup fn

Unmount
  └── run cleanup from last effect
```

Concrete example:

```typescript
useEffect(() => {
  const connection = createConnection(serverUrl, roomId);
  connection.connect();           // setup
  return () => connection.disconnect(); // cleanup
}, [serverUrl, roomId]);
```

When `roomId` changes:
1. Disconnect from old room (cleanup)
2. Connect to new room (new effect)

---

## Cleanup functions

**Every effect that sets something up should tear it down.**

Common cleanup patterns:

```typescript
// Event listener
useEffect(() => {
  window.addEventListener('resize', handleResize);
  return () => window.removeEventListener('resize', handleResize);
}, []);

// Timer
useEffect(() => {
  const id = setTimeout(() => setSomething(value), 1000);
  return () => clearTimeout(id);
}, [value]);

// Fetch with AbortController
useEffect(() => {
  const controller = new AbortController();
  fetch(url, { signal: controller.signal })
    .then(res => res.json())
    .then(data => setData(data))
    .catch(err => { if (err.name !== 'AbortError') setError(err); });
  return () => controller.abort();
}, [url]);

// WebSocket
useEffect(() => {
  const ws = new WebSocket(url);
  ws.onmessage = (e) => setMessage(e.data);
  return () => ws.close();
}, [url]);
```

Missing cleanup causes:
- Memory leaks (event listeners accumulating)
- Stale state updates on unmounted components
- Race conditions (multiple concurrent fetches)

---

## StrictMode double-invocation

In development with `<StrictMode>`, React intentionally **runs effects twice** (mount → unmount → mount) to surface bugs.

Why: it simulates what will happen when React adds support for preserving state across navigations (e.g., back button). If your effect doesn't have proper cleanup, the double-invocation will reveal it.

**If your effect breaks when run twice, you have a missing cleanup.**

```typescript
// ❌ Breaks in StrictMode (or with React's future features)
useEffect(() => {
  fetchUser(userId).then(setUser); // sets stale data if component unmounts mid-fetch
}, [userId]);

// ✅ Works correctly
useEffect(() => {
  let cancelled = false;
  fetchUser(userId).then(user => {
    if (!cancelled) setUser(user);
  });
  return () => { cancelled = true; };
}, [userId]);
```

StrictMode double-invocation only happens in **development**. Production runs effects once.

---

## Dependency array rules

1. **Every reactive value used inside the effect must be listed** — props, state, context values, variables derived from them
2. **The ESLint rule `react-hooks/exhaustive-deps` enforces this** — never suppress it with `// eslint-disable-line`
3. **If suppressing feels necessary, the effect structure needs rethinking** — usually means the effect is doing too much, or should be an event handler instead
4. **`[]` means "sync with nothing reactive"** — not "run once"; use it only when the effect genuinely has zero reactive dependencies
5. **Stale closure bugs** — omitting a dependency doesn't prevent re-runs, it just gives the effect a stale value from a previous render

```typescript
// ❌ Stale closure — count is always 0
useEffect(() => {
  const id = setInterval(() => {
    setCount(count + 1); // stale count
  }, 1000);
  return () => clearInterval(id);
}, []); // missing count

// ✅ Use functional update to avoid the dependency
useEffect(() => {
  const id = setInterval(() => {
    setCount(c => c + 1); // no stale closure
  }, 1000);
  return () => clearInterval(id);
}, []);

// ✅ Or declare the dependency correctly
useEffect(() => {
  const id = setInterval(() => {
    setCount(count + 1);
  }, 1000);
  return () => clearInterval(id);
}, [count]); // but this resets the interval on every count change
```

When the linter tells you to add a dependency and it feels wrong — that's a signal the logic belongs in an event handler, not an effect.
