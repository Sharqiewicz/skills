---
name: git
description: "Reference for team git workflow — branching strategy, commit discipline, rebase/merge rules, tag management, and configuration. Triggers on: git, commit, branch, feature branch, rebase, merge, push, stash, tag, squash, fixup, rerere, git config, remote branch, gitignore, git log, conflict resolution, git cleanup, PR, pull request, git workflow."
user-invocable: true
---

Apply this skill whenever making git decisions — branching, committing, rebasing, tagging, or cleaning up — to enforce consistent, history-clean workflow.

## MANDATORY PREPARATION

1. Identify the current operation: branching, committing, integrating, tagging, or cleanup.
2. Check the current branch with `git branch --show-current` — never operate on main without confirming intent.
3. If rebasing interactively, run `git log --oneline -10` first to understand history shape.

---

## Core Workflow

### 0. Never commit to main

All work happens on feature branches. Main is integration-only.

### 1. Feature Branch

```bash
git checkout -b <feature-branch>
```

Push early so the team sees work in progress and can code review:

```bash
git push origin -u <feature-branch>
```

### 2. Commit Discipline

```bash
git add -p          # stage interactively — review every hunk
git commit          # write a meaningful message
git push            # push regularly (backup + visibility)
```

**CRITICAL**: Use `git add -p` (patch mode), never `git add .` or `git add -A` — blind staging risks committing secrets, build artifacts, or unintended changes.

### 3. Keep History Clean

Before integration, reorder and tighten commits:

```bash
git rebase -i main  # squash / edit / fixup / reword
git push --force-with-lease
```

**IMPORTANT**: Use `--force-with-lease`, never `--force`. It refuses if someone else pushed to the branch since your last fetch.

### 4. Stay in Sync with Main

Integrate often to avoid large conflicts:

```bash
git checkout main && git pull
git checkout -
git rebase main -p
```

### 5. Merge to Main

```bash
git checkout main
git merge --no-ff --edit <feature-branch>
```

Always `--no-ff` to preserve branch topology. Always `--edit` to write a full task explanation in the merge commit.

### 6. Cleanup After Merge

```bash
git push origin <feature-branch>     # final push
git branch -d <feature-branch>       # delete local
git remote update --prune            # prune stale remote refs
```

---

## Configuration

### rerere — Reuse Recorded Resolutions

```bash
git config rerere.enabled true
```

Resolve a rebase conflict once; every subsequent rebase replays it automatically. Essential for long-lived branches rebased onto a moving main.

### push.followTags

```bash
git config push.followTags true
```

Automatically pushes annotated tags when pushing commits.

---

## Tag Management

Always use **annotated** tags for public commits:

```bash
git tag <name> <id> -a -m "message"   # annotated — always use for releases
git tag <name> <id>                   # lightweight — local notes only, never push
```

```bash
git push --follow-tags                # push commits + annotated tags only
git fetch --prune --prune-tags        # remove local tags no longer on remote
git show <tag-id>                     # inspect tag content
```

---

## Useful Commands

### Navigation

| Expression | Meaning |
|------------|---------|
| `<commit>~3` | 3 commits before the commit |
| `<commit>^^^^` | 4 commits before the commit |
| `<commit1>..<commit2>` | range from commit1 to commit2 |

### Inspection

```bash
git diff --cached               # see staged changes before committing
git log --oneline --graph       # compact visual history
git stash list
git stash save -u               # stash including untracked files
git stash pop
```

### Remote Cleanup

```bash
git fetch --prune               # remove stale remote-tracking refs
git push origin :<branch-name>  # delete a remote branch
git fetch --prune --prune-tags  # remove local tags absent from remote
```

---

## Decision Flowchart

```
What am I about to do?

├── Start new work
│   └── Create feature branch — never work on main
│
├── Save work in progress
│   └── git add -p → git commit → git push
│
├── Need to incorporate main changes
│   └── git rebase main -p  (never git merge main into feature)
│
├── Ready to integrate into main
│   ├── Clean up history first → git rebase -i main
│   └── Merge → git checkout main && git merge --no-ff --edit
│
├── Need to mark a release
│   └── Annotated tag → git tag -a -m "..."
│       never lightweight for public refs
│
└── After merge
    └── Delete feature branch locally + remotely, prune refs
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `git add .` or `git add -A` | `git add -p` — review every hunk |
| `git push --force` | `git push --force-with-lease` |
| Committing directly to main | Always use a feature branch |
| `git merge main` on a feature branch | `git rebase main -p` to stay in sync |
| Fast-forward merge to main | Always `--no-ff` to preserve branch topology |
| Lightweight tags pushed to remote | Annotated tags only, pushed with `--follow-tags` |
| Resolving the same rebase conflict repeatedly | Enable `rerere.enabled true` |
| Leaving stale remote branches | `git remote update --prune` after merge |

**NEVER:**
- Commit directly to main — all changes go through feature branches
- Use `git push --force` — only `git push --force-with-lease`
- Use `git add .` or `git add -A` — only `git add -p`
- Push lightweight tags — only annotated tags via `--follow-tags`
- Merge main into a feature branch — rebase instead (`git rebase main -p`)
- Merge a feature branch to main with fast-forward — always `--no-ff --edit`
- Leave a feature branch alive after it merges — delete local + remote, then prune

---

## Verify Result

- [ ] On a feature branch, not on main
- [ ] `git diff --cached` shows only intended changes — no secrets, no artifacts
- [ ] Commit history is clean: `git log --oneline --graph`
- [ ] Force-pushed with `--force-with-lease`, never `--force`
- [ ] `rerere.enabled true` is set in git config
- [ ] If tagging: annotated tag used, not lightweight
- [ ] After merge: local and remote branch deleted, refs pruned

A clean history is a gift to your future self and every reviewer — invest in it at every commit.
