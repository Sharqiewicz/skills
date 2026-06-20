# When to Use useEffect

Effects are correct when you need to **synchronise a React component with an external system**. External means: something that lives outside React's control.

---

## The core test: is there an external system?

Ask: **"Is there something outside React that needs to stay in sync with my component's state or lifecycle?"**

External systems include:
- DOM nodes (direct manipulation, measurement, focus)
- Browser APIs (timers, geolocation, online/offline, window resize)
- Network connections (WebSocket, EventSource, chat rooms)
- Third-party libraries that manage their own state (GSAP, Leaflet, Google Maps, jQuery plugins)
- `localStorage` / `sessionStorage` (with care — consider if you need a hook abstraction)
- Analytics/tracking systems

If none of these apply, you almost certainly don't need `useEffect`.

---

## Legitimate use 1: DOM manipulation

When you need to call imperative DOM APIs after render:

```typescript
// Focus management
function SearchInput({ autoFocus }: { autoFocus: boolean }) {
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (autoFocus) {
      inputRef.current?.focus();
    }
  }, [autoFocus]);

  return <input ref={inputRef} />;
}
```

```typescript
// Measuring layout
function Tooltip({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);
  const [height, setHeight] = useState(0);

  useEffect(() => {
    if (ref.current) {
      setHeight(ref.current.getBoundingClientRect().height);
    }
  }, []); // measure after mount

  return <div ref={ref}>{children}</div>;
}
```

```typescript
// Integrating a non-React library (e.g., a chart library)
function Chart({ data }: { data: number[] }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const chart = new MyChartLib(canvasRef.current!, { data });
    return () => chart.destroy(); // cleanup
  }, [data]);

  return <canvas ref={canvasRef} />;
}
```

---

## Legitimate use 2: Setting up connections

WebSocket, EventSource, or any persistent connection that should mirror component lifecycle:

```typescript
function ChatRoom({ roomId }: { roomId: string }) {
  const [messages, setMessages] = useState<Message[]>([]);

  useEffect(() => {
    const socket = new WebSocket(`wss://chat.example.com/room/${roomId}`);

    socket.onmessage = (event) => {
      setMessages(prev => [...prev, JSON.parse(event.data)]);
    };

    return () => socket.close(); // disconnect when roomId changes or component unmounts
  }, [roomId]);

  // ...
}
```

```typescript
// Server-sent events
function LiveFeed({ feedId }: { feedId: string }) {
  const [events, setEvents] = useState<FeedEvent[]>([]);

  useEffect(() => {
    const source = new EventSource(`/api/feed/${feedId}`);
    source.onmessage = (e) => setEvents(prev => [...prev, JSON.parse(e.data)]);
    source.onerror = () => source.close();
    return () => source.close();
  }, [feedId]);

  // ...
}
```

---

## Legitimate use 3: Browser API subscriptions

`addEventListener`/`removeEventListener` for global browser events:

```typescript
function useWindowSize() {
  const [size, setSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });

  useEffect(() => {
    function handleResize() {
      setSize({ width: window.innerWidth, height: window.innerHeight });
    }
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return size;
}
```

```typescript
// Keyboard shortcuts
function useKeyPress(key: string, handler: () => void) {
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === key) handler();
    }
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [key, handler]);
}
```

> Note: For subscribing to external stores (browser APIs that have a snapshot), prefer `useSyncExternalStore` — see below.

---

## Legitimate use 4: Imperative animation libraries

When animation libraries need imperative control (GSAP, Anime.js, etc.):

```typescript
function AnimatedCard({ visible }: { visible: boolean }) {
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!cardRef.current) return;
    const animation = gsap.to(cardRef.current, {
      opacity: visible ? 1 : 0,
      y: visible ? 0 : 20,
      duration: 0.3,
    });
    return () => animation.kill(); // cleanup
  }, [visible]);

  return <div ref={cardRef}>...</div>;
}
```

---

## Legitimate use 5: Analytics on route change

Page view tracking when routes change:

```typescript
function usePageTracking() {
  const location = useLocation();

  useEffect(() => {
    analytics.page(location.pathname);
  }, [location.pathname]);
}
```

Note: in StrictMode (dev), this fires twice. If that's a problem, use a ref guard or move tracking to the router's navigation event.

---

## `useSyncExternalStore` vs `useEffect` for subscriptions

When subscribing to an external store (any data source outside React), prefer `useSyncExternalStore` over `useEffect` + `useState`.

`useSyncExternalStore` is:
- Concurrent-mode safe (no tearing)
- SSR-safe (accepts a server snapshot)
- More explicit about the subscribe/snapshot contract

```typescript
// ✅ useSyncExternalStore for browser APIs with a snapshot
function useOnlineStatus(): boolean {
  return useSyncExternalStore(
    (callback) => {
      window.addEventListener('online', callback);
      window.addEventListener('offline', callback);
      return () => {
        window.removeEventListener('online', callback);
        window.removeEventListener('offline', callback);
      };
    },
    () => navigator.onLine,  // getSnapshot (client)
    () => true               // getServerSnapshot (SSR)
  );
}
```

Use `useEffect` for subscriptions that are one-way (you push into state but don't need a snapshot), or for integrations where you're not reading store data directly (e.g., logging, analytics, opening/closing connections).

---

## Summary: Effect vs alternatives

| Scenario | Use |
|----------|-----|
| External system (DOM, WebSocket, browser API, non-React lib) | `useEffect` with cleanup |
| Reading from external store | `useSyncExternalStore` |
| Derived/transformed data | Compute during render |
| Expensive computation | `useMemo` |
| User-triggered mutation/POST | Event handler |
| Data fetching | React Query |
| State reset on prop change | `key` prop |
| External store subscription | `useSyncExternalStore` |
