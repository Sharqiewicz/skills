# Contested calls

The picks in `SKILL.md` are defaults, not laws. These are the ones where the runner-up is genuinely defensible — the tradeoff, and the condition under which you should deviate. If a section here doesn't apply, the default in `SKILL.md` stands and you shouldn't relitigate it.

React Native's ecosystem moves faster than the web's. Anything here that reads as settled should be re-checked against current docs before a greenfield decision.

---

## Styling: Unistyles 3 vs. NativeWind

The most contested call in this list, and the one where team composition beats benchmarks.

**Unistyles 3** is a superset of `StyleSheet` — same API you already know, implemented in C++ over Nitro modules. Themes, variants, and breakpoints are applied natively without re-rendering the React tree. On the published style-library benchmarks it lands around 66ms on iOS and 80ms on Android against NativeWind's ~197ms and ~227ms. It's the default here because it costs nothing at runtime and requires learning almost nothing new.

**NativeWind** brings Tailwind's utility classes to RN with ahead-of-time compilation. It is meaningfully slower, and the mapping from CSS semantics onto RN's layout model leaks in ways that surprise people who expect web behaviour.

**Deviate to NativeWind when:** the team writes Tailwind daily and the context-switch cost is real, or components are genuinely shared with a web codebase where the class strings carry over. Both are legitimate — developer velocity is a real currency, and the perf gap only becomes user-visible in style-heavy, frequently re-rendering trees.

**Deviate to neither when:** the app is small. Plain `StyleSheet.create` has zero dependencies and zero upgrade risk.

Tamagui exists and benchmarks well, but it's a full component system with its own compiler and opinions, not a styling layer. Only worth it if you're adopting its components too.

---

## Lists: FlashList v2 vs. Legend List

**FlashList v2** is a ground-up rewrite from Shopify. The headline change is that it no longer wants size estimates — it measures items and computes positions before anything paints, which removes the whole category of "tune `estimatedItemSize` until the blanking stops" work that v1 required. It runs in Shopify's own apps at scale. It requires the New Architecture.

**Legend List** is built directly on Fabric and Reanimated and targets the same problem more aggressively. Community benchmarks show it holding 60fps on mid-range Android through 10,000-item lists with complex nested rows, where FlashList occasionally drops frames.

**Default to FlashList** — proven, better documented, more answers when it goes wrong. **Deviate to Legend List** when rows are genuinely heavy and interactive (nested lists, live-updating cells, per-row gestures) *and* you've measured FlashList dropping frames on that specific screen. Don't switch on the benchmark alone; Legend List is younger and less battle-tested in production, and that's a real cost on a shipping app.

Both are wrong for short lists. Under ~50 static items, `ScrollView` wins — virtualization overhead is not free.

---

## Navigation: Expo Router vs. hand-written React Navigation

Not really a choice between libraries — Expo Router *is* React Navigation with file-based routing, typed routes, and automatic deep linking layered on. You're choosing whether to hand-write the navigator tree.

**Default to Expo Router.** Deep linking and universal links stop being a configuration project. New screens are new files, which is much easier to onboard someone into. Route params are typed.

**Deviate when:** you're integrating into an existing native app (brownfield), you need custom transitions that don't fit the file-based model, or the project deliberately isn't on Expo. React Navigation directly is still fully supported and not a legacy path.

Either way, screen presentation comes from **native-stack** options. Expo Router doesn't replace that — you still set `headerLargeTitle`, `presentation: 'formSheet'`, and `sheetAllowedDetents` on screens, and you should.

---

## Expo vs. bare React Native CLI

The old objection — "we need custom native modules, so we can't use Expo" — hasn't been true for years. `expo prebuild` generates the `ios/` and `android/` projects, config plugins modify native config declaratively, and you can commit the native directories and edit them if you must.

What you give up by going bare: EAS Build, EAS Update, config plugins, versioned SDK modules that upgrade together, and the Expo Go / dev-client workflow. What you gain: nothing that prebuild doesn't cover for the overwhelming majority of apps.

**Deviate when** React Native is being embedded into an existing native app that owns the build, or a hard requirement conflicts with the Expo module set in a way prebuild can't reach. Both are rare and should be stated explicitly, not assumed.

---

## Storage: the four-way split

Getting this wrong causes security bugs, so it's worth stating as a rule rather than a preference.

| Data | Store |
| --- | --- |
| Auth tokens, refresh tokens, API keys, PII | `expo-secure-store` (Keychain) |
| Preferences, feature flags, small caches, zustand persistence | `react-native-mmkv` |
| Anything with queries, relations, or hundreds of rows | `expo-sqlite` (+ Drizzle) |
| Legacy code, or Expo Go compatibility | `AsyncStorage` |

MMKV is synchronous C++ with JSI/Nitro bindings — no promises, no bridge — and publishes roughly 30× faster than AsyncStorage. It supports encryption, but **encrypted MMKV is not a substitute for the Keychain**: the key has to live somewhere, and on iOS that somewhere should be SecureStore.

The failure to actually watch for is serializing a growing collection to JSON and putting it in a KV store. Once there are relations, filters, or pagination, that's a database — move to expo-sqlite before it becomes a rewrite.

---

## Deliberately not on the list

Not omissions — judgment calls, revisit as they mature.

- **Local-first sync engines** (PowerSync, Legend State + sync, WatermelonDB, ElectricSQL). The right shape for offline-first and collaborative apps, and mobile is where they matter most. Still moving fast enough that picking one is a bet on the vendor. Recommend only when offline or realtime multiplayer is a stated requirement, and say plainly that it's an early call. WatermelonDB is the most conservative of them if you need one today.
- **Full component kits** (Tamagui UI, React Native Paper, NativeBase, gluestack). Paper is Material Design and will make an iOS app look wrong. The others are large adoptions that constrain everything downstream. `rules-apple-mobile` plus native components gets a better iOS result.
- **`sonner-native`.** Good library, and the obvious pick if you want visual parity with a Sonner-based web app. `burnt` is preferred here because it renders the actual iOS system toast, which is the whole point on this platform. Switch if cross-platform visual consistency matters more than native feel.
- **Detox.** Still works, still widely deployed. Left off because Maestro needs no build instrumentation and doesn't break on every RN upgrade. Don't migrate a working Detox suite just to satisfy this list.
- **CodePush.** Microsoft retired it; `expo-updates` / EAS Update is the path.
- **Redux Toolkit.** Only if the team already runs it. Don't introduce it — zustand plus TanStack Query covers what it was reached for, with far less ceremony.
