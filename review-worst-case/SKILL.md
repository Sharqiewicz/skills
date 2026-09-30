---
name: review-worst-case
description: "Try to break what you just built by running worst-case inputs and volumes against the local app (web, React Native + Expo, data layer), then report what broke with evidence. Triggers on: try to break, break my app, break this, worst case, edge cases, stress test the UI, long names, weird emails, unusual input, lots of data, seed extreme data, what breaks, torture test, chaos data, adversarial input, does this survive, empty state, 10k rows."
user-invocable: true
argument-hint: "[TARGET=<screen, form, feature or route>]"
---

Attack a feature you just built with the inputs real users will eventually send it — very long names, odd emails, emoji, RTL text, 10k rows, zero rows, double submits — and return a ranked report of what broke, with evidence.

## MANDATORY PREPARATION

1. Read `./payloads.md` in full. It is the attack catalog. Do not make up payloads from memory when the catalog has one.
2. Pin down the target. If `TARGET` is missing, check `git diff --name-only main...HEAD` and propose the feature the diff touches. Confirm it before going further.
3. Identify the environment and confirm it is **local or dev**. Get the URL, the simulator/device, and the database connection. Ask: **"Is this database disposable, or do seeded rows need to be cleaned up afterwards?"**
4. Read the target's code: form schemas and validators (zod, react-hook-form), DB schema and constraints (column lengths, unique indexes, nullability), API handlers, and the components that render the data (lists, tables, cards, labels, headers).
5. Pick the runners that fit the stack:
   - **Web UI**: claude-in-chrome, or the project's Playwright if it has one
   - **Mobile**: iOS Simulator via `xcrun simctl` (Dynamic Type, appearance, screenshots), plus Maestro if the project has it. Put data in through the API or a seed script rather than typing into the simulator
   - **Data layer**: the project's seed script, ORM client, or API. Never raw SQL against a DB whose owner you haven't confirmed

**CRITICAL**: If the environment's URL or connection string looks like production (a real domain, `prod`, `production`, a managed host with no `dev`/`staging`/`localhost`), stop and ask. Never assume.

---

## Diagnostic Scan

### 1. Map the attack surface

List every place where user-controlled data **enters** the target (inputs, imports, API fields, seed rows) and every place it is **displayed** (list rows, table cells, avatars, labels, badges, page titles, toasts, emails, push notifications, share sheets). Most breaks happen at display sites, far from the input that caused them.

Look for mismatches between layers. These are the cheapest breaks to find:
- The UI allows 500 characters but the DB column is `varchar(255)`
- The client validator accepts `a+b@x.com` but the server regex rejects it
- The unique index is case-sensitive but the app treats emails as case-insensitive

### 2. Plan the attacks

For each entry point, pick attacks from `payloads.md` across these categories: **Length**, **Unicode**, **Identity** (names, emails), **Numbers & dates**, **Volume**, **Escaping**, **Behavior**, and **Mobile** or **Data layer** where relevant. Rank them by how likely a real user is to send the input times how much damage it would do. Show the plan (target, attack, exact payload, where it will be observed) and run it only after the user confirms.

**IMPORTANT**: Pair every attack with the display sites where it will be observed. Typing a 300-character name into a form and seeing it saved is not a test. The test is checking every list, header and card that shows that name afterwards.

### 3. Run the attacks

- Run one attack at a time and observe every display site mapped for it before moving on
- Record evidence for each break: a screenshot, the console error, the network response, or a DB row
- Tag every seeded record so it can be found again (e.g. names prefixed `wc_`, emails at `@example.test`)
- For volume attacks, grow the size step by step (1 → 100 → 1,000 → 10,000) and write down where it first degrades
- On mobile, re-run the visual attacks at Dynamic Type `accessibility-extra-extra-extra-large`, on the smallest supported device, in dark mode, and with the keyboard open

Severity scale:

| Sev | Meaning |
|-----|---------|
| **S0** | Crash, data loss, data corruption, or a silent save of wrong data |
| **S1** | Feature unusable: can't submit, can't read, can't reach an action |
| **S2** | Degraded: layout broken, content clipped with no way to see it, very slow |
| **S3** | Cosmetic: ugly but fully usable |

---

## Generate Report

```
## Worst-case report: <target>

Environment: <url / simulator + device / db>  ·  Attacks run: N  ·  Broke: N  ·  Survived: N

### Broke
| # | Sev | Attack | Payload | What happened | Likely cause (file:line) | Suggested fix |
|---|-----|--------|---------|---------------|--------------------------|---------------|

### Layer mismatches
- <field>: UI allows X, validator allows Y, DB allows Z

### Survived
- <attack> — <display sites checked>

### Not tested
- <attack> — <why: no runner, would need prod, out of scope>

### Cleanup
- <exact command or query that removes every seeded `wc_` record>
```

Sort **Broke** by severity, then by how likely the input is. Every row needs evidence you actually observed. For fixes, point to `/harden` (UI resilience) or name the specific change: the validator, the column, `min-w-0`/`truncate`, virtualization, and so on.

**NEVER:**
- Run any attack against a production URL, a production database, or a shared staging DB before the user explicitly confirms that target
- Use real-looking email domains in payloads. Use `example.com`, `example.test` or `*.invalid` (reserved by RFC 2606), because signup flows send real email
- Edit source code to fix a break during the review. The output is the report, and fixing is a separate step
- Report a break you didn't observe. "This would probably overflow" goes under **Not tested** or gets run
- Stop at the input. A payload that saves without error but was never checked at its display sites counts as untested, not survived
- Seed data without a tag and a cleanup command
- Jump straight to 10,000 rows. Grow in steps, or you won't know whether 200 or 9,000 was the breaking point
- Use escaping payloads (`<script>`, `'; DROP TABLE`) against anything other than the user's own local app. They check that output is escaped, and they are not for probing third-party systems

## Verify Report

- Every attack in the confirmed plan appears under Broke, Survived or Not tested
- Every Broke row has evidence and a file:line cause, or says "cause not located"
- Layer mismatches were checked for every entry point
- Mobile attacks, if in scope, ran at the largest Dynamic Type and on the smallest device
- The Cleanup section's command was tested, or you say it wasn't

Your happy path is the one case you already tested. This skill exists to send the other ones.
