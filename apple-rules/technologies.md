# Technologies (web-relevant only)

Most HIG Technologies are native-only (CarPlay, HomeKit, HealthKit, iCloud, Siri, NFC, App Clips, Live Activities, Widgets…) and out of scope for the web. Only these three carry documented web applicability. Rules read as build guidance and as review checks.

## Sign in with Apple

Cross-platform — offered on any website via the JS SDK, including non-Apple platforms.

- **Ask for sign-in only in exchange for value**, and **delay it as long as possible** — let people use the site first (see patterns.md → Managing accounts).
- **Never ask for a password** — the whole point is delegated auth.
- **Respect Apple's private-relay email addresses** — don't reject or try to unmask them; they're valid, deliverable addresses.
- Present it alongside your other real sign-in options (don't fake the button); follow Apple's button styling/wording rules for the official mark.
- Web: `AppleID.auth` JS SDK; treat it as one SSO option in a labeled list ("Continue with Apple").

## Apple Pay on the Web

Has a dedicated web API (`ApplePaySession`), distinct from the native in-app flow.

- **Offer it only on devices/browsers that actually support it** — feature-detect (`ApplePaySession.canMakePayments()`) and conditionally render the button.
- Make it a **primary but not sole** payment option when a card is on file — never the only path to checkout.
- **Never label a custom button "Apple Pay"** without the official mark/button; use Apple's provided button styles.
- Signal acceptance to search engines via appropriate semantic markup.
- Web: `ApplePaySession` + a merchant-validation server endpoint; branch API refs by "(web)" vs native.

## Machine Learning / Generative AI (methodology)

No unique web API, but the design methodology is platform-agnostic and reusable for any web AI feature.

- **Define the model's role** — critical (the feature fails without it) vs. complementary (an enhancement) — and design the fallback for when it's wrong or unavailable accordingly.
- **Classify data sensitivity** (private vs. public); **process on-device where feasible** (WebAssembly / on-device inference) for privacy and latency.
- **Plan input and output feedback** — show confidence/uncertainty where it matters; make it obvious the content is AI-generated.
- **Handle mistakes and corrections gracefully** — easy ways to undo, correct, regenerate, or report; never present an unverifiable AI output as authoritative fact.
- **Responsibility applies (principle 3):** anticipate misuse and harm — an allergy-aware recipe assistant must not suggest a harmful ingredient. Add previews, confirmations, disclaimers; cut a feature whose risk outweighs its value.
