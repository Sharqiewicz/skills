---
name: project-manager
description: "Create descriptive, structured GitHub Issues using User Story format with Definition of Ready and Done checklists. Triggers on: github issue, create issue, new issue, user story, feature request, bug report, task, backlog item, DoR, DoD, acceptance criteria, issue template."
user-invocable: true
args:
  - name: context
    description: "Optional free-text description of what the issue is about. Can be a feature idea, bug description, or task title."
    required: false
---

Create well-structured GitHub Issues that are clear, testable, and immediately actionable — anchored in user value and team agreements.

## MANDATORY PREPARATION

1. Check if a domain model or CONTEXT.md exists in the repo: look for `CONTEXT.md`, `CLAUDE.md`, or `docs/` — read the relevant section to understand entities and surfaces.
2. Identify the issue type: **Feature**, **Bug**, or **Chore/Task** — this determines which template sections apply.
3. If no context was provided, ask the user: "What should this issue be about?" before proceeding.

---

## Step 1 — Gather Issue Context

Ask the user these questions **one at a time** (skip any already answered in the invocation):

1. **Type** — Is this a Feature, Bug, or Chore/Task?
2. **Who is affected?** — Which user role or persona experiences this? (for the User Story)
3. **What do they want?** — The specific capability or fix they need.
4. **Why does it matter?** — The outcome or value delivered.
5. **Acceptance criteria** — What must be true for this to be considered done? (list 3–5 bullet points)
6. **Scope / constraints** — Are there technical, design, or platform constraints to note?
7. **Size estimate** — Has the team sized this? (XS / S / M / L / XL or story points)

**CRITICAL**: Do not draft the issue until all questions are answered. An issue without clear acceptance criteria cannot pass Definition of Ready.

---

## Step 2 — Validate Against Definition of Ready

Before drafting, verify the collected information satisfies all DoR criteria:

**Definition of READY**
- [ ] User Story is clear
- [ ] User Story is testable
- [ ] User Story is feasible
- [ ] User Story is defined
- [ ] User Story acceptance criteria are defined
- [ ] User Story sized by the Development Team
- [ ] Team has a good idea what it means to demo the User Story

If any item is unchecked, ask the user to clarify before proceeding.

---

## Step 3 — Draft the GitHub Issue

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

**IMPORTANT**: The title must be a single, action-oriented sentence under 72 characters. Format: `[Type] <verb> <object>` — e.g. `[Feature] Allow users to select a payout method` or `[Bug] Fix fee comparison crash on mobile`.

Show the full draft to the user and ask for explicit approval before writing the file.

---

## Step 4 — Save Issue to File

Once approved, save the issue as a Markdown file for easy copy-paste into GitHub:

**File path:** `~/github-issues/<YYYY-MM-DD>-<kebab-title>.md`
**Example:** `~/github-issues/2026-04-22-allow-users-to-select-payout-method.md`

Create the folder if it doesn't exist:

```bash
mkdir -p ~/github-issues
```

Write the file with the issue title as an H1 at the top, followed by the full issue body below it. After writing, print the absolute file path so the user can open it directly.

**NEVER:**
- Draft or write an issue before the user has provided acceptance criteria — an issue without AC cannot be demoed or tested
- Mark the Definition of Ready as fully checked unless the user has confirmed each item
- Use vague acceptance criteria like "works correctly" or "looks good" — every criterion must be independently verifiable
- Write a title longer than 72 characters or without the `[Type]` prefix
- Write the file without showing the full draft and getting explicit user approval first
- Invent technical details or constraints the user didn't mention
- Skip the domain model check — issues must use correct entity names and surface terminology from the codebase

---

## Verify Result

- [ ] Issue title is under 72 characters and starts with `[Feature]`, `[Bug]`, or `[Chore]`
- [ ] User Story follows "As a / I want / So that" format
- [ ] All acceptance criteria are specific and independently testable
- [ ] Definition of Ready is present with all items listed
- [ ] Definition of Done is present with all items listed
- [ ] Draft was shown to the user and approved before the file was written
- [ ] File exists at `~/github-issues/<date>-<kebab-title>.md` and path was printed

A GitHub Issue is a contract between the team and the work — every ambiguity left in the issue becomes a disagreement during review.
