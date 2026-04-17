# Anti-Patterns: You Might Not Need an Effect

Source: React docs — "You Might Not Need an Effect"

---

## 1. Transforming data for rendering

**Problem:** Using `useEffect` + `setState` to compute derived values.

```typescript
// ❌ Unnecessary effect
const [firstName, setFirstName] = useState('Taylor');
const [lastName, setLastName] = useState('Swift');
const [fullName, setFullName] = useState('');

useEffect(() => {
  setFullName(firstName + ' ' + lastName);
}, [firstName, lastName]);
```

**Why it's wrong:** causes an extra render cycle; the value is entirely derivable from existing state.

```typescript
// ✅ Derive at render time
const [firstName, setFirstName] = useState('Taylor');
const [lastName, setLastName] = useState('Swift');
const fullName = firstName + ' ' + lastName; // computed during render
```

**Rule:** If a value can be computed from props or state, compute it during render. No effect, no extra state.

---

## 2. Caching expensive computations

**Problem:** Using `useEffect` + `setState` to cache a filtered/sorted list.

```typescript
// ❌ Unnecessary effect
const [todos, setTodos] = useState(initialTodos);
const [filter, setFilter] = useState('all');
const [visibleTodos, setVisibleTodos] = useState([]);

useEffect(() => {
  setVisibleTodos(getFilteredTodos(todos, filter));
}, [todos, filter]);
```

**Why it's wrong:** extra state, extra render, and `useMemo` is the right tool.

```typescript
// ✅ useMemo for expensive computations
const [todos, setTodos] = useState(initialTodos);
const [filter, setFilter] = useState('all');
const visibleTodos = useMemo(
  () => getFilteredTodos(todos, filter),
  [todos, filter]
);
```

`useMemo` re-runs only when dependencies change and doesn't cause a re-render.

Only use `useMemo` if the computation is genuinely expensive (e.g., filtering thousands of items). For simple derivations, compute inline.

---

## 3. Resetting all state when a prop changes

**Problem:** Using `useEffect` to reset state when a key prop (like `userId`) changes.

```typescript
// ❌ Resets state reactively, causes extra render
export function ProfilePage({ userId }: { userId: string }) {
  const [comment, setComment] = useState('');

  useEffect(() => {
    setComment('');
  }, [userId]);

  // ...
}
```

**Why it's wrong:** React renders with stale state first, then re-renders after the effect clears it. Two renders instead of one.

```typescript
// ✅ Use key prop to force full remount
export function ProfilePage({ userId }: { userId: string }) {
  return <Profile userId={userId} key={userId} />;
}

function Profile({ userId }: { userId: string }) {
  const [comment, setComment] = useState('');
  // When key changes, React unmounts and remounts — state resets automatically
}
```

**Rule:** When a component's entire state should reset when a prop changes, pass that prop as `key`.

---

## 4. Adjusting some state when a prop changes

**Problem:** Using `useEffect` to sync a subset of state with a prop change.

```typescript
// ❌ Effect for partial state adjustment
function List({ items }: { items: Item[] }) {
  const [selection, setSelection] = useState<Item | null>(null);

  useEffect(() => {
    setSelection(null);
  }, [items]);

  // ...
}
```

**Why it's wrong:** causes a stale render followed by an immediate re-render.

```typescript
// ✅ Set state during render (render-time setState pattern)
function List({ items }: { items: Item[] }) {
  const [selection, setSelection] = useState<Item | null>(null);
  const [prevItems, setPrevItems] = useState(items);

  if (items !== prevItems) {
    setPrevItems(items);
    setSelection(null); // React re-renders immediately, skipping the stale render
  }

  // ...
}
```

React handles `setState` called during render specially: it re-renders the component immediately after, discarding the current render output. This avoids the extra DOM update.

Even better: reconsider whether selection should be an index/ID (derivable) rather than a full object.

---

## 5. Sharing logic between event handlers

**Problem:** Using an effect to run shared logic when state changes, because multiple events lead to the same state.

```typescript
// ❌ Effect triggered by state that multiple handlers set
function ProductPage({ product }: { product: Product }) {
  const [quantity, setQuantity] = useState(1);

  useEffect(() => {
    // runs whenever quantity changes — but we only want this on purchase
    showNotification(`Added ${quantity} to cart`);
  }, [quantity]);

  function handleBuyClick() { setQuantity(q => q + 1); }
  function handleCheckoutClick() { setQuantity(q => q + 1); }
}
```

**Why it's wrong:** effects respond to *state*, not *user intent*. If `quantity` changes for any other reason (e.g., loaded from a cart), the notification fires incorrectly.

```typescript
// ✅ Extract shared logic, call from event handlers
function ProductPage({ product }: { product: Product }) {
  const [quantity, setQuantity] = useState(1);

  function addToCart() {
    setQuantity(q => q + 1);
    showNotification(`Added to cart`);
  }

  function handleBuyClick() { addToCart(); }
  function handleCheckoutClick() { addToCart(); }
}
```

**Rule:** If code should run *because the user did something*, put it in an event handler.

---

## 6. Sending a POST request on user action

**Problem:** Triggering a POST/mutation in an effect that watches state set by an event handler.

```typescript
// ❌ POST via effect
function Form() {
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    if (submitted) {
      post('/api/register', formData);
    }
  }, [submitted]);

  function handleSubmit() {
    setSubmitted(true);
  }
}
```

**Why it's wrong:** effects may re-run (e.g., in StrictMode, or if dependencies change). Non-idempotent operations don't belong in effects.

```typescript
// ✅ POST directly in the event handler
function Form() {
  function handleSubmit() {
    post('/api/register', formData);
  }
}
```

**Rule:** Mutations, POSTs, and any non-idempotent operation that responds to a user gesture belong in event handlers.

---

## 7. Notifying parent about state change

**Problem:** Child uses `useEffect` to call a parent callback when its state changes.

```typescript
// ❌ Effect to notify parent
function Toggle({ onChange }: { onChange: (value: boolean) => void }) {
  const [isOn, setIsOn] = useState(false);

  useEffect(() => {
    onChange(isOn);
  }, [isOn, onChange]);

  function handleClick() {
    setIsOn(v => !v);
  }
}
```

**Why it's wrong:** two renders (child renders with new state, then effect fires, potentially causing parent to re-render).

```typescript
// ✅ Call parent callback directly in the event handler
function Toggle({ onChange }: { onChange: (value: boolean) => void }) {
  const [isOn, setIsOn] = useState(false);

  function handleClick() {
    const newValue = !isOn;
    setIsOn(newValue);
    onChange(newValue); // called in the same event
  }
}
```

React batches state updates from the same event handler, so parent and child state updates happen in a single re-render pass.

---

## 8. Passing data to parent

**Problem:** Child fetches/computes data and passes it up to parent via `useEffect` + parent callback.

```typescript
// ❌ Data flows upward through effects
function Child({ onData }: { onData: (data: Data) => void }) {
  const [data, setData] = useState<Data | null>(null);

  useEffect(() => {
    fetchData().then(setData);
  }, []);

  useEffect(() => {
    if (data !== null) onData(data);
  }, [data, onData]);
}
```

**Why it's wrong:** data should flow *down* in React (props). Pushing data up via effects inverts the data flow and makes the component hard to reason about.

```typescript
// ✅ Lift state up — fetch in parent, pass data down as props
function Parent() {
  const [data, setData] = useState<Data | null>(null);

  useEffect(() => {
    fetchData().then(setData);
  }, []);

  return <Child data={data} />;
}

function Child({ data }: { data: Data | null }) {
  // receives data as a prop
}
```

Or use React Query and share the query key — both components use the same cache entry.

---

## 9. Subscribing to external stores

**Problem:** Manually subscribing to an external store with `useEffect` + `useState`.

```typescript
// ❌ Manual subscription is error-prone
function useOnlineStatus() {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    function handleOnline() { setIsOnline(true); }
    function handleOffline() { setIsOnline(false); }
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
}
```

**Why it's wrong:** tearing issues (different components see different snapshots), doesn't handle server rendering correctly.

```typescript
// ✅ useSyncExternalStore
function useOnlineStatus() {
  return useSyncExternalStore(
    (callback) => {
      window.addEventListener('online', callback);
      window.addEventListener('offline', callback);
      return () => {
        window.removeEventListener('online', callback);
        window.removeEventListener('offline', callback);
      };
    },
    () => navigator.onLine,  // client snapshot
    () => true               // server snapshot
  );
}
```

`useSyncExternalStore` handles tearing, concurrent rendering, and SSR correctly.

---

## 10. Fetching data

**Problem:** Using `useEffect` + `useState` to fetch data.

```typescript
// ❌ useEffect fetching — race conditions, no loading state, no caching
function SearchResults({ query }: { query: string }) {
  const [results, setResults] = useState<Result[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setIsLoading(true);
    fetchResults(query).then(data => {
      setResults(data); // race condition: old fetch may resolve after new one
      setIsLoading(false);
    });
  }, [query]);
}
```

**Why it's wrong:**
- Race conditions when `query` changes rapidly
- No request deduplication
- No caching (re-fetches on every mount)
- No background revalidation
- Lots of boilerplate for loading/error states

```typescript
// ✅ React Query
import { useQuery } from '@tanstack/react-query';

function SearchResults({ query }: { query: string }) {
  const { data: results = [], isLoading } = useQuery({
    queryKey: ['results', query],
    queryFn: () => fetchResults(query),
  });
}
```

React Query handles caching, deduplication, background refetching, loading/error states, and race conditions automatically.

See [`state-management-sharqiewicz`](../../state-management-sharqiewicz/SKILL.md) for full React Query patterns.

If you must use `useEffect` for fetching (e.g., no React Query available), always use an AbortController:

```typescript
useEffect(() => {
  const controller = new AbortController();
  fetch(`/api/search?q=${query}`, { signal: controller.signal })
    .then(r => r.json())
    .then(setResults)
    .catch(err => { if (err.name !== 'AbortError') setError(err); });
  return () => controller.abort();
}, [query]);
```

---

## 11. Initialising something once on app load

**Problem:** Using `useEffect` with `[]` to run one-time app initialisation.

```typescript
// ❌ Runs in effects (twice in StrictMode, once per mount in normal mode)
function App() {
  useEffect(() => {
    loadDataStore();
    checkAuthToken();
  }, []);
}
```

**Why it's wrong:** if the `App` component ever unmounts and remounts, initialisation runs again. In StrictMode, it runs twice.

```typescript
// ✅ Module-level code — runs once when the module is loaded
loadDataStore();
checkAuthToken();

function App() {
  // initialisation already done
}
```

Module-level code runs exactly once when the JS module is first imported, regardless of renders.

Alternatively, use a ref guard if the code must be inside a component:

```typescript
const initialised = { current: false };

function App() {
  useEffect(() => {
    if (initialised.current) return;
    initialised.current = true;
    loadDataStore();
  }, []);
}
```

---

## 12. Buying a product / non-idempotent actions triggered by effect

**Problem:** Running non-idempotent side effects (purchases, email sends, irreversible actions) inside an effect.

```typescript
// ❌ Non-idempotent action in an effect
function Checkout({ productId }: { productId: string }) {
  useEffect(() => {
    // This will run TWICE in StrictMode in development
    // and may run again if deps change
    buyProduct(productId);
  }, [productId]);
}
```

**Why it's wrong:** effects can run multiple times. `buyProduct` will fire twice in StrictMode (dev), and again if `productId` changes. You cannot make `buyProduct` idempotent easily.

```typescript
// ✅ Non-idempotent action in the event handler that triggered it
function Checkout({ productId }: { productId: string }) {
  function handleBuyClick() {
    buyProduct(productId);
  }

  return <button onClick={handleBuyClick}>Buy</button>;
}
```

**Rule:** If an action cannot safely be repeated (purchase, send email, delete record), it belongs in an event handler responding to a specific user gesture — never in an effect.
