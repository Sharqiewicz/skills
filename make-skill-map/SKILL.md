---
name: make-skill-map
description: "Keep the curated skill map current: find installed skills the map does not mention yet, propose a lane and owner for each, drop entries for skills that are no longer installed, show the diff, and only after approval write map.md and regenerate the README skill-map block. The only skill that writes map.md. Depends on find-skill's scan.py. Manual only. Triggers on: update skill map, sync skill map, map my skills, new skill installed, unmapped skills, add skill to map, refresh skill map, regenerate skill map, skill map out of date, find-skill says unmapped, organize skills into lanes."
user-invocable: true
disable-model-invocation: true
argument-hint: [optional: skill names to map, or "readme" to only regenerate the README block]
---

Bring `map.md` back in line with what is actually installed by mapping new skills, removing gone ones, and regenerating the README block, with every write shown and approved first.

## MANDATORY PREPARATION

1. Locate this skill's directory (the harness gives the base directory when the skill loads). This skill lives next to `find-skill` in the same repo, so the shared files are at `<skill-dir>/../find-skill/`:
   - `../find-skill/scan.py` — live scan; also regenerates the README block
   - `../find-skill/map.md` — the skill map, the single source of truth
   If `../find-skill/` does not exist, stop and tell the user: this skill depends on `/sharqiewicz:find-skill` being installed from the same repo.
2. Read `../find-skill/map.md` in full: the lane headings, the row format (`| Skill | Job | Notes |`, first cell is the exact command in backticks), the `<!-- DECIDE: rationale -->` convention, and the Namesakes and Exceptions sections.
3. Run the two checks, read-only:
   - `python3 <skill-dir>/../find-skill/scan.py --unmapped` — installed skills missing from the map
   - `python3 <skill-dir>/../find-skill/scan.py --stale` — map entries that match nothing installed
4. Learn the vocabulary: **Channel**, **Home channel**, **Double**, **Namesake**, **Exception**, **Overlap**, **Owner**, **Lane**, **Skill map**, **Unmapped skill**. Use these exact terms. The lanes are Plan, Design UI, Motion, Code quality, Git & handoff, SEO, Tools.

**CRITICAL**: Nothing is written until the user has seen the full diff of `map.md` and said yes. Writing `map.md` or the README without showing the draft first breaks the user's rule for every file.

---

## Assess What Changed

1. If the argument is `readme`, skip to **Regenerate the README Block**.
2. For each **Unmapped skill**, read its `SKILL.md` description (its path is in `scan.py --json`: match by `invoke`). Decide from the description, not the name.
3. For each **stale** entry, confirm it is really gone: the pattern matches nothing in `scan.py --json`. A wildcard row (`/sentry:sentry-*-sdk`) is stale only if it matches nothing.
4. Classify every Unmapped skill against the map:
   - **Double** — same skill, same author, another Channel: no new row; flag it to the user for removal.
   - **Namesake** — same name as a mapped skill, different skill: new row in its own lane, recorded under Namesakes.
   - **Overlap** — competes with a mapped skill for the same job: needs an Owner decision.
   - **Exception** — lives outside its set's Home channel: row plus an entry under Exceptions.
   - Otherwise a plain new row.

## Plan the Map Changes

For each Unmapped skill decide:

1. **Lane** — the one lane you would look in first. Exactly one.
2. **Job** — a few words, in the existing rows' style.
3. **Notes** — owner, namesake, exception, web or mobile sibling (`-mobile` means React Native + Expo on iOS), and `manual` when its frontmatter has `disable-model-invocation: true`.
4. **Owner** for any Overlap — prefer the user's own `/sharqiewicz:*` skill when it targets the same job (they are opinionated to my React/Next/TypeScript web and React Native + Expo iOS stack). Mark every owner call you make without the user having decided it with `<!-- DECIDE: one-line rationale -->` at the end of the Notes cell, so the user can confirm it.
5. Many near-identical skills (one per SDK, per provider) go in one grouped row or a wildcard pattern, not one row each.

**IMPORTANT**: Only the first column of a table row counts as a mention. A skill named in Notes or in prose is still unmapped. Put every new command in the first cell, in backticks, exact, with its namespace.

## Show the Draft and Ask

Present, in one message:

- **Additions** — each new row, in its lane, in final markdown
- **Removals** — each stale row or pattern, with its line
- **Owner calls** — every `<!-- DECIDE -->` you added, one line each
- The resulting `map.md` diff

Then ask for approval: apply, change something, or skip. Wait for the answer. If the user changes a lane or owner, revise and show the changed part again.

## Write the Map

Only after an explicit yes:

1. Edit `../find-skill/map.md` with exactly the approved rows and removals. Keep table headers, lane order and the Namesakes and Exceptions sections intact.
2. Re-run `scan.py --unmapped` and `scan.py --stale` (Verify below).

## Regenerate the README Block

1. Default target is `~/Programmer/skills/README.md` (`scan.py --readme` with no path). Use another README only if the user names one.
2. If that README has no `<!-- skill-map:start -->` ... `<!-- skill-map:end -->` markers, `scan.py --readme` exits with an error and writes nothing. Do not add markers silently: show where you propose to insert them and ask first.
3. Show what will change: `python3 <skill-dir>/../find-skill/scan.py --readme-out <scratch-file>` writes the block to a scratch file you can display (use a scratch or temp location, never the repo). Get a yes.
4. Then run `python3 <skill-dir>/../find-skill/scan.py --readme` and show `git diff --stat` for the README (read-only git only).

**NEVER:**
- Write `map.md` or the README before showing the diff and getting approval
- Edit the README by hand between the skill-map markers; it is generated, so change `map.md` and regenerate
- Run any git command that mutates the repo (`add`, `commit`, `push`, `stash`, `reset`, `checkout`); committing is the user's separate decision
- Put a skill in two lanes, or map the same command twice
- Choose an Owner for an Overlap silently; every owner call you make is marked `<!-- DECIDE -->` and listed in the draft
- Mention a new skill only in a Notes cell or prose and call it mapped; only the first column counts
- Delete a row because it looks stale without `scan.py --stale` confirming it matches nothing installed
- Remove an entry only because the skill is a Double or Namesake; flag those to the user instead
- Modify anything outside `../find-skill/map.md` and the README block (no plugin.json, no skill files, nothing in `~/.claude` or `~/.agents`)

## Verify the Map

- [ ] `scan.py --unmapped` lists nothing, or only skills the user chose to skip
- [ ] `scan.py --stale` lists nothing, or only entries the user chose to keep
- [ ] Each lane table still has the `| Skill | Job | Notes |` header, and no skill is in two lanes
- [ ] Every new Overlap owner is marked `<!-- DECIDE -->` and was shown to the user
- [ ] The README block was regenerated from `map.md`, and the README diff touches only the block
- [ ] No file other than `map.md` and the README was written, and no mutating git command was run

The map is the user's taste written down; this skill only keeps it current, and never changes it without approval.
