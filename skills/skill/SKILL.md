---
name: new-skill
description: "Scaffold a new Claude Code skill from scratch, or audit and improve an existing one. Enforces the canonical SKILL.md structure derived from high-quality reference skills. Triggers on: create skill, new skill, write skill, add skill, build skill, define skill, scaffold skill, make slash command, add command, codify knowledge, teach claude, audit skill, review skill, improve skill, fix skill structure."
user-invocable: true
argument-hint: [skill-name]
---

Scaffold a new Claude Code skill at `~/.claude/skills/<name>/SKILL.md`, or audit an existing skill for structural gaps and fix them.

## MANDATORY PREPARATION

1. Check whether `~/.claude/skills/<argument>/` already exists:
   - **Exists** → audit mode: read `SKILL.md` in full, then go to **Audit an Existing Skill**
   - **Does not exist** → create mode: go to **Create a New Skill**
2. Read two or three existing skills from `~/.claude/skills/` closest in archetype to the one being created or audited — look at how they structure mandatory preparation, assessment, NEVER blocks, and closing sentences.

---

## Create a New Skill

### Step 1: Gather Intent

Ask the user in a single message — all at once. Skip any question already answered in the invocation:

1. **Name** — What should the slash command be called? (e.g. `code-review` → `/code-review`)
2. **Purpose** — What does this skill do? One sentence.
3. **Triggers** — What keywords or situations should cause Claude to auto-apply this? List phrases.
4. **Archetype** — Which pattern fits?
   - **Reference** — a ruleset Claude applies while coding (animation principles, a11y rules)
   - **Workflow** — a step-by-step process with a defined output (gather → ask → write)
   - **Audit/Report** — scan code and produce a structured report (SEO audit, a11y review)
5. **Scope** — Single-file, multi-file, or with scripts?
6. **Output** — Does the skill produce structured output? If yes, what does it look like?

**CRITICAL**: Do not begin drafting until all questions are answered. A skill written without clear intent will need to be rewritten.

### Step 2: Draft the Skill

Compose the full `SKILL.md` using the **Canonical Structure** below. Show the full draft and ask for explicit approval before writing.

### Step 3: Write the File

Once approved:

1. Create `~/.claude/skills/<name>/` if it doesn't exist
2. Write `SKILL.md` with the approved content
3. If multi-file: create sub-files with `# <Topic>` placeholder headings and note which sections need filling in

---

## Audit an Existing Skill

1. **Assess** — evaluate the skill against every item in the Review Checklist
2. **Report** — list every gap with a specific description of what's missing and why it matters
3. **Propose** — show the complete revised `SKILL.md` (not diffs — the full file) and ask for approval
4. **Fix** — write the approved revision

**CRITICAL**: Every gap must include a concrete proposed fix. Do not report a gap without showing exactly how to close it.

---

## Canonical SKILL.md Structure

Every skill — regardless of archetype — must follow this layout in this order:

```
---
[frontmatter]
---

[Opening summary sentence — one sentence describing what and why]

## MANDATORY PREPARATION

[What Claude must do before starting: read references, gather context, check dependencies]

---

## [Core sections by archetype]

[**CRITICAL**: and **IMPORTANT**: callouts inline where needed]

**NEVER:**
[Specific, actionable constraints]

## Verify [Result]

[Confirmation checklist after the skill completes]

[Closing reminder sentence — anchors the skill's philosophy]
```

### Frontmatter Fields

- `name`: kebab-case slug
- `description`: one sentence of purpose + `Triggers on: keyword1, keyword2, ...` — max 1024 chars total
- `user-invocable: true` always
- Use structured `args` (with `name`, `description`, `required`) when argument semantics are worth documenting; use `argument-hint` for simple positional hints

### Core Sections by Archetype

| Archetype | Section Order |
|-----------|--------------|
| **Reference** | Quick Reference table → Core Principles → Decision Flowcharts → Common Mistakes → Review Checklist |
| **Workflow** | Assess [Subject] → Plan [Approach] → [Do the Work] Systematically → NEVER → Verify |
| **Audit/Report** | Diagnostic Scan → Generate Report → NEVER |

### Inline Callouts

Place these where a constraint is critical but doesn't belong in the NEVER block:
- `**CRITICAL**:` — a mistake here breaks the skill's output
- `**IMPORTANT**:` — a constraint easy to forget mid-flow

### NEVER Block Rules

Every skill must have one. Each constraint must be:
- **Specific** — name the exact mistake, not a vague category
- **Actionable** — a reader knows immediately what not to do
- **Grounded** — tied to real failure modes, not hypothetical ones

---

## Review Checklist

- [ ] Description includes `Triggers on:` and is under 1024 chars
- [ ] Opening summary sentence present after frontmatter
- [ ] `## MANDATORY PREPARATION` section exists and is specific (not generic boilerplate)
- [ ] Core sections follow the archetype pattern
- [ ] At least one `**CRITICAL**:` or `**IMPORTANT**:` callout present
- [ ] `**NEVER**:` block present with specific, actionable constraints
- [ ] `## Verify` section present
- [ ] Closing reminder sentence present
- [ ] No time-sensitive info (dates, version numbers, transient URLs)
- [ ] Consistent terminology throughout
- [ ] References one level deep — no chains

---

## Verify Creation / Revision

- Confirm the file exists at `~/.claude/skills/<name>/SKILL.md`
- Confirm description is under 1024 chars
- Confirm all Review Checklist items pass

```
Created/Updated: ~/.claude/skills/<name>/SKILL.md
Invoke with: /<name>
```

Remember: A skill is only as good as its structure. Every section exists to prevent Claude from drifting — make each constraint explicit, each step numbered, each failure mode named.

**NEVER:**
- Write or overwrite a file without showing the full draft and getting explicit approval
- Skip `## MANDATORY PREPARATION` — it prevents context-blind execution
- Omit `Triggers on:` from the description
- Use vague NEVER constraints ("don't do bad things") — every constraint must name a specific mistake
- Skip the `## Verify` step after writing
- Omit the closing reminder sentence — it anchors the skill's purpose
- Invent archetype structures — use only Reference, Workflow, or Audit/Report
- Include time-sensitive content (dates, version numbers, transient URLs)
- Report an audit gap without a concrete proposed fix
