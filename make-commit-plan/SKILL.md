---
name: make-commit-plan
description: "Inspect the working tree and propose how to stage and commit it — logical commit groups, exact git add commands, and Conventional Commits messages — without ever running git add, git commit, or any other mutating git command. Triggers on: commit this, what should I commit, suggest a commit, commit message, write a commit message, how should I split this, stage these changes, git add, group my changes, commit plan, prepare a commit, ready to commit, what changed."
user-invocable: true
args:
  - name: scope
    description: "Optional: a path, glob, or hint (e.g. 'src/auth', 'only staged', 'one commit') to narrow which changes the plan covers."
    required: false
---

Turn an uncommitted working tree into a proposed sequence of clean, atomic commits — exact `git add` commands and messages the user can copy — while leaving the repository untouched.

## MANDATORY PREPARATION

1. Confirm you are in a git repository and note the branch: `git rev-parse --is-inside-work-tree && git branch --show-current`. If on `main`/`master`, flag it in the plan's header (see `rules-git`: all work belongs on a feature branch).
2. Capture the full state, read-only:
   - `git status --porcelain=v1 -uall` — every modified, staged, and untracked path
   - `git diff` — unstaged changes
   - `git diff --cached` — anything already staged
   - `git diff --stat` — size per file, to spot generated or bulk changes
3. Learn the repo's message conventions from the last 20 commits: `git log --oneline -20`. If a `commitlint`/`.commitlintrc`, `CONTRIBUTING.md`, or `.gitmessage` exists, read it — it overrides the defaults below.
4. If the `scope` argument narrows the request, restrict the diff commands to that path and say so in the plan.

**CRITICAL**: Every command in this skill is read-only. The skill ends with a proposal; the user runs it.

---

## Assess the Changes

Read the diffs, not just the file list. For each changed path, determine:

- **Intent** — what behaviour or structure it changes (feature, fix, refactor, docs, test, chore, style, build, ci, perf)
- **Coupling** — which other files must ship in the same commit for the tree to build and tests to pass
- **Risk** — does it touch anything that should never be committed?

Run the risk scan on every path before grouping:

| Signal | Action |
|--------|--------|
| `.env`, `*.pem`, `*.key`, `id_rsa`, credentials, tokens, API keys inside a diff | Exclude from every group; list under **Do not commit** with the reason |
| `node_modules/`, `dist/`, `build/`, `.next/`, coverage, `*.log`, OS files (`.DS_Store`) | Exclude; suggest a `.gitignore` entry if none covers it |
| Binary or file > 1 MB | Exclude by default; ask whether it is intentional |
| Lockfile changed without a matching manifest change (or vice versa) | Flag as a likely mistake |
| Debug leftovers (`console.log`, `debugger`, `TODO REMOVE`, commented-out blocks) | Flag; suggest reverting the hunk before staging |
| Unrelated whitespace/format-only churn mixed into a logic file | Suggest splitting with `git add -p` or a separate `style:` commit |

## Plan the Commits

Group changes into the smallest set of commits where each one:

1. Has a single purpose that fits one Conventional Commits type
2. Leaves the tree building and tests passing on its own
3. Could be reverted independently without breaking the others

Ordering rules:

- Preparatory refactors and renames come **before** the feature that needed them
- Dependency/manifest changes come **before** the code that uses them
- Tests ship **with** the code they cover, not in a trailing commit
- Docs for a change ship **with** that change unless they are large enough to obscure the diff

**IMPORTANT**: When one file contains hunks belonging to two different commits, do not force them into one. Prescribe `git add -p <file>` and describe which hunks to accept (by function name or line range) for each commit.

## Write the Plan

Message rules (default; repo conventions from preparation step 3 win):

- Format: `type(scope): summary` — type from `feat | fix | refactor | docs | test | chore | style | build | ci | perf`
- Summary: imperative mood, lowercase after the colon, no trailing period, ≤ 72 characters
- Body (optional): wrapped at 72, explains **why**, not what — the diff already shows what
- Footer: `BREAKING CHANGE:` or issue references only when true

Output this exact structure:

```
## Commit plan — <branch> (<N> files changed, <M> commits proposed)

[⚠️ On main — create a feature branch first: git checkout -b <suggested-name>]

### Do not commit
- `<path>` — <reason: secret / artifact / debug leftover / oversized>

### Commit 1/<M> — <type(scope): summary>
Why this group: <one sentence>

    git add <path> <path>
    git add -p <path>   # accept hunks: <function or line range>; reject the rest
    git commit -m "<type(scope): summary>" -m "<body>"

### Commit 2/<M> — ...

### Copy-paste block
    <all commands for every commit, in order, one per line>

### Before you run it
- [ ] Review each `git add -p` hunk — the plan names them, you confirm them
- [ ] `git diff --cached` after each add shows only that commit's intent
- [ ] <any open question the plan could not resolve>
```

Keep the **Copy-paste block** literal and in execution order. Keep the `git commit -m` lines fully quoted so they run as-is in zsh.

**NEVER:**
- Run `git add`, `git commit`, `git commit --amend`, `git stash`, `git reset`, `git checkout -- <file>`, `git restore`, `git clean`, or `git push` — the skill proposes, the user executes
- Propose `git add .`, `git add -A`, or `git add -u` — always list paths explicitly, or use `git add -p` for partial files
- Put a secret, credential file, or build artifact into any commit group, even if the user says "commit everything"
- Write a message that describes the diff ("update file.ts", "changes") instead of the intent
- Mix two Conventional Commits types into one commit to reduce the commit count
- Invent a scope, ticket number, or `BREAKING CHANGE:` footer the diff does not justify
- Skip the risk-scan table because the change set looks small
- Draft the plan from `git status` alone without reading the diffs

## Verify Plan

- [ ] No mutating git command was executed during the skill run
- [ ] Every changed path appears exactly once: in one commit group or under **Do not commit**
- [ ] Each commit has one type, an imperative ≤ 72-char summary, and builds on its own
- [ ] `git add -p` is prescribed wherever one file spans two commits, with the hunks named
- [ ] Message style matches the repo's history or its commitlint config
- [ ] Branch warning shown if on `main`/`master`
- [ ] Copy-paste block is complete and in dependency order

A commit is the smallest unit of reviewable intent — the plan's job is to find those units and hand them over, never to press the button.
