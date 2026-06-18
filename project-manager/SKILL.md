---
name: project-manager
description: "Turn ideas, conversations, and plans into structured, testable work on the issue tracker. Three flows: (A) draft a single GitHub Issue in User Story format with Definition of Ready/Done; (B) synthesize the current conversation into a PRD; (C) break a plan or PRD into independently-grabbable tracer-bullet issues. Triggers on: github issue, create issue, new issue, user story, feature request, bug report, task, backlog item, DoR, DoD, acceptance criteria, write a PRD, turn this into a PRD, break this into issues, slice into tickets, vertical slices, tracer bullets."
user-invocable: true
args:
  - name: context
    description: "Optional free-text: a feature idea, bug description, task title, an instruction like 'write a PRD' or 'break this into issues', or an issue reference (number, URL, or path) to slice."
    required: false
---

Turn ideas, conversations, and plans into clear, testable, immediately-actionable work on the project issue tracker — anchored in user value and team agreements.

This skill has **three flows**. The PRD and slicing flows are adapted from Matt Pocock's `to-prd` and `to-issues` skills; the single-issue flow is the original.

## Pick the flow

- **Flow A — Single Issue**: the user wants one well-formed ticket for a feature, bug, or chore. Default when in doubt.
- **Flow B — Conversation → PRD** (`to-prd`): the user wants the current conversation turned into a PRD and published. No interview — synthesize what's already been discussed.
- **Flow C — Plan/PRD → Issues** (`to-issues`): the user wants a plan, spec, or PRD broken into independently-grabbable tracer-bullet issues.

If the request is ambiguous, ask which flow once, then proceed.

## MANDATORY PREPARATION (all flows)

1. **Read the domain context.** Look for `CONTEXT.md`, `CLAUDE.md`, and `docs/adr/` — read the relevant section so every title and description uses the project's domain glossary vocabulary and respects any ADRs in the area you're touching.
2. **For Flows B and C, confirm the issue tracker and triage label vocabulary are available.** These should have been provided earlier in the session. If not, stop and run `/setup-matt-pocock-skills`, then resume.

---

# Flow A — Single Issue

## A1 — Gather Issue Context

Ask the user these questions **one at a time** (skip any already answered in the invocation):

1. **Type** — Is this a Feature, Bug, or Chore/Task?
2. **Who is affected?** — Which user role or persona experiences this?
3. **What do they want?** — The specific capability or fix they need.
4. **Why does it matter?** — The outcome or value delivered.
5. **Acceptance criteria** — What must be true for this to be done? (3–5 bullet points)
6. **Scope / constraints** — Any technical, design, or platform constraints?
7. **Size estimate** — Has the team sized this? (XS / S / M / L / XL or story points)

**CRITICAL**: Do not draft the issue until all questions are answered. An issue without clear acceptance criteria cannot pass Definition of Ready.

## A2 — Validate Against Definition of Ready

Verify the collected information satisfies all DoR criteria below. If any item is unchecked, ask the user to clarify before proceeding.

## A3 — Draft the GitHub Issue

Compose the issue body using this exact structure:

```
## User Story

**As a** [user role / persona]
**I want** [capability or action]
**So that** [outcome or value]

---

## Acceptance Criteria

- [ ] [Criterion 1 — specific, testable]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

---

## Definition of Ready

- [ ] User Story is clear
- [ ] User Story is testable
- [ ] User Story is feasible
- [ ] User Story is defined
- [ ] User Story acceptance criteria are defined
- [ ] User Story sized by the Development Team
- [ ] Team has a good idea what it means to demo the User Story

## Definition of Done

- [ ] Code Produced (all todos completed)
- [ ] Code Documented
- [ ] Builds without errors
- [ ] Unit Tests written and passing
- [ ] Deployed to TEST environment and passed system tests
- [ ] Remaining hours for tasks set to 0 and all tasks are closed

---

## Additional Context

[Technical notes, constraints, links to designs, related issues, or affected domain surfaces]
```

**IMPORTANT**: The title must be a single, action-oriented sentence under 72 characters. Format: `[Type] <verb> <object>` — e.g. `[Feature] Allow users to select a payout method`.

Show the full draft to the user and ask for explicit approval before writing the file.

## A4 — Save Issue to File

Once approved, save as Markdown for easy copy-paste into GitHub:

- **File path:** `~/github-issues/<YYYY-MM-DD>-<kebab-title>.md`
- Create the folder if needed: `mkdir -p ~/github-issues`
- Write the title as an H1, then the full body. Print the absolute path.

---

# Flow B — Conversation → PRD (`to-prd`)

Take the current conversation and codebase understanding and produce a PRD, then publish it. **Do NOT interview the user** — synthesize what you already know. If the conversation is genuinely too thin to write a PRD, say so plainly and stop; do not start a Q&A.

## B1 — Explore the codebase

Understand the current state of the code in the area this feature touches. Establish the modules and surfaces involved, the exact domain entity names (use them verbatim), and any ADRs that constrain decisions here.

## B2 — Sketch the test seams

Sketch the seams at which you'll test the feature. **Prefer existing seams** to new ones. **Use the highest seam possible.** If new seams are needed, propose them at the highest point you can. **The fewer seams, the better — the ideal is one.**

## B3 — Check the seams with the user

Present the proposed seams and confirm they match expectations **before** writing the PRD. This is the only check-in — it is about seams, not a requirements interview. Wait for confirmation, adjust if needed, then proceed.

## B4 — Write the PRD

Use this exact template, drawing entirely from the conversation, the exploration, and the agreed seams:

```
## Problem Statement
The problem the user is facing, from the user's perspective.

## Solution
The solution to the problem, from the user's perspective.

## User Stories
A LONG, numbered list. Each: "As a <role>, I want a <capability>, so that <outcome>".
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
2. ...
This list must be extremely extensive and cover all aspects of the feature.

## Implementation Decisions
- Modules built/modified, and the interfaces of those modules that change
- Technical clarifications from the developer
- Architectural decisions, schema changes, API contracts, specific interactions
Do NOT include specific file paths or code snippets.
Exception: a prototype snippet that encodes a decision more precisely than prose
(state machine, reducer, schema, type shape) — inline only the decision-rich part
and note it came from a prototype.

## Testing Decisions
- What makes a good test here (test external behaviour, not implementation details)
- Which modules will be tested
- The seams agreed in B3
- Prior art for the tests (similar tests already in the codebase)

## Out of Scope
What is explicitly out of scope for this PRD.

## Further Notes
Any further notes about the feature.
```

Write the **User Stories list LONG** — cover every role, surface, and edge. A thin list is the most common failure of this flow. Every Testing Decision must be externally observable at the agreed seam.

## B5 — Publish to the issue tracker

The PRD body **is** the issue body. Use a single action-oriented title under 72 characters. Apply the **`ready-for-agent`** triage label — no additional triage. Print the issue URL.

---

# Flow C — Plan/PRD → Issues (`to-issues`)

Break a plan, spec, or PRD into independently-grabbable issues using vertical slices (tracer bullets), and publish them.

## C1 — Gather context

Work from whatever is already in the conversation. If the user passes an issue reference (number, URL, or path), fetch it and read its **full body and comments**.

## C2 — Explore the codebase (optional)

If not already explored, understand the current state of the code. Look for opportunities to **prefactor**: *"Make the change easy, then make the easy change."* Prefactoring becomes its own slice, sequenced first.

## C3 — Draft vertical slices

Break the plan into tracer-bullet issues. Each is a **thin vertical slice that cuts through ALL integration layers end-to-end** (schema, API, UI, tests) — NOT a horizontal slice of one layer.

- Each slice delivers a narrow but **COMPLETE** path through every layer.
- A completed slice is **demoable or verifiable on its own**.

## C4 — Quiz the user

Present the breakdown as a numbered list. For each slice show **Title**, **Blocked by**, and **User stories covered**. Then ask: Does the granularity feel right? Are the dependencies correct? Should any slices be merged or split? **Iterate until the user approves.**

## C5 — Publish the issues

For each approved slice, publish an issue using the template below, with the **`ready-for-agent`** label (unless instructed otherwise). Publish in **dependency order (blockers first)** so "Blocked by" references real identifiers. Print every URL. **Do NOT close or modify any parent issue.**

```
## Parent
A reference to the parent issue (omit if the source was not an existing issue).

## What to build
A concise description of this vertical slice — the end-to-end behaviour, not a
layer-by-layer implementation. Avoid file paths and code snippets (same prototype
exception as Flow B applies).

## Acceptance criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Blocked by
A reference to the blocking ticket, or "None — can start immediately".
```

---

## NEVER (all flows)

- Skip the domain-model / ADR check — titles and descriptions must use correct entity names and surface terminology.
- Use vague acceptance criteria like "works correctly" or "looks good" — every criterion must be independently verifiable and externally observable.
- Invent technical details, requirements, or constraints the user never mentioned or that aren't grounded in the code.
- Include specific file paths or full code snippets in a PRD or issue (the prototype-snippet exception is the only allowance, trimmed to the decision).
- **Flow A**: draft before acceptance criteria are provided; mark DoR fully checked unless the user confirmed each item; write a title over 72 chars or without the `[Type]` prefix; write the file without showing the draft and getting explicit approval.
- **Flow B**: interview the user (the only check-in is the seams); ship a short user-story list; publish without the `ready-for-agent` label or with extra triage.
- **Flow C**: produce horizontal slices; publish before approval; publish out of dependency order; reference a "Blocked by" issue not yet published; close or modify any parent issue.

---

## Verify Result

**Flow A**
- [ ] Title under 72 chars, starts with `[Feature]`/`[Bug]`/`[Chore]`
- [ ] User Story in "As a / I want / So that" format; AC specific and testable
- [ ] Definition of Ready and Definition of Done both present and complete
- [ ] Draft shown and approved before the file was written; file saved and path printed

**Flow B**
- [ ] Codebase explored; domain vocabulary used; ADRs respected
- [ ] Seams sketched at the highest point, minimised toward one, and confirmed with the user
- [ ] PRD has all sections: Problem Statement, Solution, User Stories, Implementation Decisions, Testing Decisions, Out of Scope, Further Notes
- [ ] User Stories list is long, numbered, "As a / I want / So that"; no file paths/snippets; tests externally observable
- [ ] Published with the `ready-for-agent` label and URL printed

**Flow C**
- [ ] Source gathered; any referenced issue fetched in full; prefactoring sequenced first
- [ ] Every slice is a complete vertical tracer bullet, demoable on its own
- [ ] Breakdown presented (Title / Blocked by / User stories) and approved
- [ ] Each issue uses the template; AC externally observable
- [ ] Published in dependency order with `ready-for-agent`; real identifiers in "Blocked by"; URLs printed; no parent issue touched

A unit of work — issue or PRD — is a contract between the team and the work. Every ambiguity left in it becomes a disagreement once someone (or an agent) picks it up.
