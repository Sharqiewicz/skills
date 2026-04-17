---
name: cognitive-load
description: "Review code for excessive cognitive load — identifies extraneous complexity and suggests concrete simplifications. Triggers on: cognitive load, extraneous complexity, hard to read, too many abstractions, too many files, shallow modules, deep modules, nested ifs, early returns, inheritance chain, composition, premature DRY, tight coupling, framework coupling, layered architecture, hexagonal architecture, onion architecture, ports and adapters, microservices, distributed monolith, DDD, domain-driven design, familiarity bias, design sacrifice, over-engineered, boring architecture, simplify, refactor, code review, mental load, working memory."
user-invocable: true
argument-hint: [FILE=<path> | AREA=<description>]
---

Review code for extraneous cognitive load — the kind caused by how code is written, not by the inherent difficulty of the problem it solves.

## WHAT THIS SKILL IS ABOUT

Cognitive load is how much a developer needs to think in order to complete a task. There are two kinds:

- **Intrinsic** — caused by the inherent difficulty of the task. Cannot be reduced.
- **Extraneous** — caused by the way the code is written. Can and should be eliminated.

This review targets **extraneous cognitive load only**. Do not flag things that are inherently hard. Flag things that are hard because of how they were expressed.

The average person can hold roughly **four chunks** in working memory at once. Once that threshold is crossed, it becomes much harder to understand things — and the primary limit to development speed stops being how many lines to write, and starts being how much information must be collected in mind before knowing what those lines are.

Use this notation when describing load:
- `🧠` — fresh working memory, no extra facts held
- `🧠+` / `🧠++` / `🧠+++` — accumulating cognitive burden
- `🤯` — overloaded, four or more chunks held simultaneously

**CRITICAL**: The intrinsic/extraneous distinction is the entire basis of this review. If you are not certain which type a finding is, do not flag it.

---

## MANDATORY PREPARATION

1. Read the file(s) or area indicated by the user argument. If none given, read the most recently changed files in the current branch (`git diff --name-only HEAD~1`).
2. Understand what the code is supposed to do before judging how it does it.
3. Assess from the perspective of **a developer seeing this code for the first time**.

---

## REVIEW CHECKLIST

Work through each section. For every finding, note:
- **Where** (file + line range)
- **What** the pattern is
- **Why** it raises cognitive load
- **Concrete fix** — show the improved version or describe it precisely

---

### 1. Complex Conditionals

Look for compound `if` conditions with more than two clauses, especially with mixed `&&`/`||` and negation.

**Bad:**
```
if val > limit && (cond2 || cond3) && (cond4 && !cond5) {  // 🤯
```

**Good:** Extract to named booleans first, then combine:
```
isValid   = val > limit
isAllowed = cond2 || cond3
isSecure  = cond4 && !cond5
if isValid && isAllowed && isSecure {  // 🧠
```

---

### 2. Nested Ifs (Missing Early Returns)

Deeply nested `if` blocks force the reader to track all outer conditions in working memory. Each nesting level costs `🧠+`.

**Bad:** Three levels of nesting = `🧠+++` before reaching the logic.

**Good:** Invert each guard into an early return. Once past the guards, the reader can forget them:
```
if !isValid { return }
if !isSecure { return }
// 🧠 — we're here only if both passed
```

---

### 3. Inheritance Chains

Flag any inheritance chain with more than two levels. Each level forces the reader to load the parent into memory before understanding the child.

`AdminController → UserController → GuestController → BaseController` = `🤯` before writing a single line.

Also check **downward**: if there's a `SuperuserController extends AdminController`, modifying `AdminController` to fix a bug can silently break the subclass. The reader must load the entire subtree before touching anything. `🤯`

**Fix:** Prefer composition. Shared behaviour should be an injected collaborator, not a base class.

---

### 4. Too Many Shallow Modules

Count the number of classes/functions/modules in the area under review. Ask: are these **deep** (simple interface, rich behaviour) or **shallow** (trivial body behind a verbose name)?

Signs of shallow modules:
- A function whose name is longer than its body
- Classes named `*Factory`, `*Provider`, `*Manager`, `*Helper`, `*Util` with only 1–3 methods
- A wrapper that adds no logic — only delegates

The hidden cost: **not only must a reader hold each module's responsibility in mind, but also all the interactions between them.** Twenty shallow modules means twenty responsibilities plus their cross-product of possible interactions. Information hiding is the remedy — complexity hidden inside a module doesn't load the reader's working memory.

Jumping between shallow components is mentally exhausting. Linear code flow is more natural to the human brain — when forced to jump, the reader must context-switch repeatedly, each jump costing working memory.

**Fix:** Collapse shallow modules into their callers or into a deeper sibling. The goal is fewer interfaces to memorise, not fewer lines of code.

Also flag the inverse: **artificially splitting large functions to satisfy a "functions should be short" rule.** Important "crux" functions are allowed to be large — their size is a signal that they're the core of the system. If you break them up into many small pieces, the crux disappears into the noise and becomes harder to find.

A concrete form of this: **single-use helper functions extracted from otherwise linear code.** Linear code reads top-to-bottom — the reader follows one thread of execution without context-switching. When you extract a one-shot helper, you introduce indirection: the reader must jump to the helper, hold the calling context in memory, read it, and jump back. They also lose visibility into hidden questions — Is this function idempotent? What state does it assume? — that linear code answers automatically as you read. Replace single-use extraction with an explanatory comment instead: you get the documentation benefit without the indirection cost.

> Do not extract small functions from linear code, especially if you only use them once. None of the benefits offsets the loss in linearity.

> The best components are those that provide powerful functionality yet have a simple interface. — John Ousterhout

---

### 5. Misapplied "Responsible for One Thing"

Flag over-granular decomposition justified by "single responsibility". The real SRP is: **a module should be responsible to one user or stakeholder** — not that it should do only one narrow operation.

Signs of the misapplication:
- Names like `MetricsProviderFactoryFactory`, `UserCreationHandlerService` — the name is more cognitively taxing than the entire implementation
- Classes split so finely that understanding any one of them requires reading four others first
- Abstractions that exist for aesthetic reasons ("it felt cleaner") rather than a concrete stakeholder boundary

**Test:** If a bug here causes two *different* business stakeholders to complain, the boundary is wrong. If the class name requires more mental effort than reading the body, the split is too fine.

---

### 6. Too Many Shallow Microservices

The shallow/deep module principle scales to services. A distributed system of many tiny services that must be changed together for every feature is a **distributed monolith** — all the operational complexity of microservices with none of the independence benefits.

Warning signs:
- A single user-facing feature requires changes in 4+ services
- New requirements consistently touch the same cluster of services
- Services were split upfront, before the domain boundaries were understood

Flag the justification: **"The FAANG companies proved microservices architecture to be effective"** is not a valid reason for a startup or small team to adopt them upfront. FAANG split services to scale *development teams*, not to make code cleaner.

> Real example: a team of 5 developers introduced 17 microservices. They were 10 months behind schedule. Every new requirement required changes across 4+ services. Reproducing and debugging an issue meant jumping across a distributed system. `🤯`

The industry is heading toward **macroservices** — services that are not so shallow, i.e. deeper. The lesson from overly granular separation is filtering back in.

> The Tanenbaum-Torvalds debate argued Linux's monolithic design was theoretically flawed and a microkernel was superior. Three decades later, monolithic Linux is everywhere — your smart teapot runs it. Microkernel-based GNU Hurd is still in development. Practical simplicity beat theoretical elegance.

**Fix:** Make decisions as late as responsibly possible — that's when you have the most information. A well-structured monolith with truly isolated modules is often more flexible than premature microservices, and far cheaper to reason about. Extract a service only when the need for independent deployment is concrete, not hypothetical.

---

### 7. Premature / Abused DRY

Flag abstractions that couple unrelated things in the name of eliminating duplication.

Ask: **if one of the duplicated sites needs to change independently, does this abstraction survive?** If not, the coupling costs more than the repetition.

Also flag **within-module premature extraction**: common functionality pulled into a shared helper based on *perceived* similarity that may not hold in the long run. The abstraction feels clean at the time but becomes difficult to modify when the two use-cases diverge.

> A little copying is better than a little dependency. — Rob Pike

Also flag: importing a large library to use one small function that could be written inline. All your dependencies are your code — debugging 10+ levels of an imported library's stack trace is painful.

---

### 8. Opaque Numeric / String Constants

Any magic number, status code, or enum value that requires a lookup to understand.

```
return 418  // 🧠+, what does this mean?
```

**Fix:** Use self-describing values at the boundary:
```json
{ "code": "user_is_banned" }
```

This applies to database status columns, flag bitmasks, and HTTP status codes repurposed as business codes. We are not in the era of 640K computers — don't optimise for memory at the cost of readability.

Also flag confusing terminology pairs. "Authentication" vs "authorization" is a well-known example — developers, QA, and stakeholders routinely mix them up. Simpler terms like **"login"** and **"permissions"** carry the same meaning with less mental overhead.

---

### 9. Tight Framework Coupling

Flag business logic that lives inside framework lifecycle hooks, decorators, or base classes where the framework controls the call.

**Symptom:** You cannot test the business rule without booting the framework.

**Fix:** Push framework glue to the edges. Core logic should call framework utilities, not inherit from them. This lets new contributors add value from day one without first learning the framework's "magic".

**Escalation risk:** When a new requirement doesn't fit the framework's model, teams sometimes fork the framework. A custom fork means every newcomer must learn your proprietary variant before contributing anything. `🤯` Flag any evidence of in-house framework modifications as a severe long-term load hazard.

---

### 10. Unnecessary Layered Architecture

Flag files that exist only to satisfy a layered architecture pattern (ports, adapters, repositories, DTOs, mappers) when no practical extension point justifies them.

Each layer = one more file to open, one more mental hop, one more place a bug can hide.

**Test:** If removing this layer required changing only one file instead of five, the layer is probably not earning its keep.

**On the "easy to swap the database" argument:** Changing storage causes problems in data model incompatibilities, communication protocols, and distributed systems challenges. Abstractions save ~10% of migration time at best. The real cost is elsewhere. Don't pay the cognitive price of layering for a benefit that rarely materialises.

Also: the abstraction boundary doesn't protect you from *observed behaviour* dependencies. Hyrum's Law:

> With a sufficient number of users of an API, it does not matter what you promise in the contract: all observable behaviours of your system will be depended on by somebody.

Callers depend on undocumented ordering, timing, and side effects — not just the declared interface. No abstraction layer prevents this.

> Layers of abstraction aren't free — they must be held in working memory.

The better approach: follow dependency inversion directly. Business logic should not depend on low-level modules. You should be able to test core logic without infrastructure. That's it — no port/adapter vocabulary required.

---

### 11. Feature-Rich Language / Overused Language Features

Flag code that uses advanced or obscure language features where a simpler construct would do.

The problem: **you not only have to understand the program, you have to reconstruct why the author chose this feature from all the features available.** `🤯`

Signs:
- Non-obvious operator overloads, exotic syntax, or rarely-used standard library tricks
- Code that requires knowing a specific language version's behaviour to understand correctly
- Clever one-liners that save two lines but take ten minutes to parse

> Concrete example: a C++ engineer with 20 years of experience describes how the token `||` has *different meaning* in `requires ((!P<T> || !Q<T>))` vs `requires (!(P<T> || Q<T>))` — constraint disjunction vs logical OR, behaving differently. Even after two decades, they need to mentally reconstruct what the standard says for each edge case. And once something is fixed in a new language version, cognitive load doesn't decrease — you now have to know what it was *before*, what changed, *when*, and whether the legacy version might appear in the code. `🤯` This is extraneous cognitive load with no business value — caused purely by language complexity, not the problem at hand.

**Fix:** Prefer the obvious construct. Limit feature usage to orthogonal, well-understood features. Reduce the number of choices a reader must evaluate.

> Reduce cognitive load by limiting the number of choices.

---

### 12. Domain-Driven Design Misapplication

DDD has valuable *problem-space* concepts: ubiquitous language, bounded contexts, aggregates, event storming. These help teams learn domain insights and communicate with stakeholders.

The problem: teams implement DDD as *solution-space* folder structures — repositories, value objects, domain services, application services — based on their own subjective interpretation. Each developer reads DDD differently. The result is a unique mental model that every newcomer must learn from scratch before contributing anything. `🤯`

Flag:
- Folder structures named after DDD patterns (`/domain`, `/application`, `/infrastructure`, `/ports`) when the team can't articulate a concrete stakeholder or deployment boundary they enforce
- Concepts like "aggregate root" or "value object" used in code but not explained anywhere accessible
- Architecture debates framed as DDD interpretation disagreements

**Better alternative:** Focus on the fundamental rules directly — dependency inversion, single source of truth, information hiding, low cognitive load. These produce the same good outcomes without the subjective interpretation layer.

**Team Topologies** is a more useful framework in practice: it helps split cognitive load *across teams* using consistent mental models that engineers converge on rather than diverge from. DDD tends to produce 10 different mental models for 10 different readers.

---

### 13. Familiarity Bias

Flag patterns that are complex but feel normal because the team is used to them.

> Familiarity is not the same as simplicity. They feel the same — that ease of moving through a space without much mental effort — but for very different reasons. — Dan North

Common examples:
- A project-specific "architecture" with no external documentation — typically a blend of Clean Architecture, Event-Driven Architecture, and DDD filtered through one developer's preferences
- Non-idiomatic use of a standard tool that new contributors would have to be taught
- Abbreviations, domain jargon, or internal codenames used without a glossary
- Complexity accumulated one small step at a time — no single addition felt wrong, but the total is `🤯`

**Key insight:** There is no simplifying force acting on a codebase other than deliberate choices. Simplicity doesn't emerge naturally — it erodes. Each small addition seems harmless in isolation ("when there are only 2–3 conditionals, adding one more doesn't make any difference"). The person who added each piece never saw the total. You are the first person who has to make sense of it all at once.

**Test:** Would a competent developer joining today be confused for more than 40 minutes in a row? If yes, there is something to improve.

**Practical techniques:**
- Ask someone new to critique the code *before* they get too institutionalised. Once they've internalised the mental models, they stop seeing the complexity. The window is short.
- Measure confusion during onboarding via pair programming. If a new developer is confused for more than 40 minutes in a row, that is a signal — not about the developer, about the code.

---

### 14. Missed Opportunity for "Design Sacrifice"

Flag architectures that carry unnecessary features or constraints because the team was unwilling to deliberately drop them for simplicity.

> "Sometimes you sacrifice something and get back simplicity, or performance, or both." — antirez (Redis)

A design sacrifice is a *deliberate* choice to drop a feature or capability in exchange for a simpler, more maintainable design. The mistake is treating every requirement as non-negotiable when a small capability cut can dramatically reduce complexity.

Signs:
- A feature that accounts for 5% of use cases but drives 50% of the architectural complexity
- Constraints carried over from earlier system designs that no longer apply
- "We need to support X" where X was assumed, not verified with stakeholders

**Fix:** Identify features that create disproportionate complexity. Present the trade-off to stakeholders — they often prefer the simpler version once the cost is visible.

---

### 15. Over-Engineered Boring Problems

Flag sophisticated solutions to problems that have well-understood, boring answers.

The architectures with the best long-term track records are often the most boring: CRUD monoliths, flat module structures, single-threaded event loops. Systems like Instagram (3 engineers, 14M users), Python monolith on Postgres, Redis (one function that wires everything up) — none of them won on cleverness.

The most complex software systems in the world that have stood the test of time — Unix, Kubernetes, Chrome, Redis — have nothing fancy in them. It's boring for the most part, and that's the point.

Signs:
- A greenfield service that immediately introduces microservices, event sourcing, or hexagonal architecture before the domain is understood
- "We'll need it later" as justification for architectural decisions that increase complexity today
- A solution that impresses in a code review but confuses the on-call engineer at 3am

**Test:** Can a competent developer reproduce and debug an issue in this area without jumping across more than 2–3 call stacks or distributed components?

> Debugging is twice as hard as writing the code in the first place. If you write it as cleverly as possible, you are, by definition, not smart enough to debug it. — Brian Kernighan

---

## OUTPUT FORMAT

**CRITICAL**: Every finding must include a concrete before/after or a precise description of the fix. A finding without a fix is noise, not a review.

Structure the review as follows:

### Summary
One paragraph: overall cognitive load level of the area reviewed. Use `🧠` / `🤯` notation. Be direct.

### Findings

For each issue:

**[PATTERN NAME]** — `<file>:<lines>`
> Brief description of what you found and why it raises cognitive load.

```
// BEFORE (annotated with 🧠 load markers)
```
```
// AFTER (concrete fix)
```

---

### Priority

Rank findings by impact:
1. **High** — new developers will be blocked or confused; bugs are likely to occur here
2. **Medium** — slows down understanding but doesn't block; refactor when nearby
3. **Low** — cosmetic; fix opportunistically

---

## LONG-TERM DIAGNOSTIC QUESTIONS

When assessing the overall health of the area, apply these three questions from the article's author. They are harder to answer than static code checks but more revealing:

1. **Debuggability** — Is it easy to reproduce and debug an issue here? Or does someone have to jump across call stacks or distributed components, holding everything in their head at once?
2. **Changeability** — Can changes be made quickly, or are there unknown unknowns? Are developers afraid to touch things?
3. **Onboardability** — Can new people add features quickly? Are there unique mental models they must learn first — things that exist nowhere outside this codebase?

The mindset "this architecture feels good" is a point-in-time subjective feeling and says nothing about reality. These three questions measure the actual consequences.

---

## Verify Review

- Every finding has a concrete before/after or a precise description of the fix
- No findings flag intrinsic complexity — only extraneous
- `🧠` / `🤯` load notation is used in at least one finding
- Priority ranking is applied — not everything is ranked High
- Summary paragraph is present and uses load notation

**NEVER:**
- Flag intrinsic complexity — hard problems are allowed to look hard; only flag how they are expressed
- Produce a finding without a concrete fix — every issue must include an actionable before/after or precise description of the change
- Treat familiarity as evidence of quality — something feeling obvious to you is not a pass
- Rank everything High — not all cognitive load is equal; triage deliberately
- Suggest features, refactors, or improvements beyond what directly reduces cognitive load
- Apply this skill to things that are inherently hard (distributed systems fundamentals, complex algorithms) unless the expression of that complexity is the problem
- Omit the 🧠 / 🤯 load notation from findings — it makes the severity concrete and scannable

Remember: The goal is not to make code shorter — it's to reduce the number of facts a reader must hold in mind at once. One well-placed simplification is worth ten cosmetic cleanups.
