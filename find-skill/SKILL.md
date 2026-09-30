---
name: find-skill
description: "Given a free-text description of what you want to do, name the one installed skill that owns the job, up to two that complement it, and the likely wrong picks to avoid, each with its exact command. Uses a live scan of installed skills plus the curated skill map. Read-only; it recommends, it never runs a skill or changes a file. Manual only. Triggers on: which skill, what skill should I use, find a skill, is there a skill for, which command, what should I run for, skill for this, which skill owns, what's the right skill, I want to animate, best skill for."
user-invocable: true
disable-model-invocation: true
argument-hint: [what you want to do]
---

Turn "what I want to do" into one exact slash command to run, plus the complements and the wrong picks to skip, by matching the request against the skill map and the live list of installed skills.

## MANDATORY PREPARATION

1. Locate this skill's directory. The harness gives the skill's base directory when it loads; `scan.py` and `map.md` sit directly in it. Below, `<skill-dir>` means that directory.
2. Read `<skill-dir>/map.md` in full. It holds the Lanes, the Owner of each overlapping job, the Namesakes and the Exceptions. It is the single source of truth for preferences.
3. Run the scan, read-only, and keep the output:
   - `python3 <skill-dir>/scan.py --unmapped` — installed skills the map does not mention yet (possible fits the map cannot rank)
   - `python3 <skill-dir>/scan.py --search <2-4 keywords from the request>` — live keyword matches with their lane, to catch skills the map's wording missed
4. If the argument is empty, ask in one line what the user wants to do. Do not guess.

**CRITICAL**: This skill is strictly read-only. The `find-` prefix promises no side effects. Never run a recommended skill, never edit `map.md`, never run `scan.py --readme` or `--readme-out`. Changing the map is the job of `/sharqiewicz:make-skill-map`.

---

## Assess the Request

1. **Restate the job in a few words**, not the skill the user named. "Make the sheet feel right on iPhone" is a mobile motion and gesture job, whatever tool they had in mind.
2. **Pick the Lane** (Plan, Design UI, Motion, Code quality, Git & handoff, SEO, Tools) by the first lane you would look in. A job can touch two lanes; choose the one the user's verb points at (think, look, move, hold up, ship, rank, integrate).
3. **Check web versus mobile.** A `-mobile` skill means React Native + Expo on iOS and has a web sibling with the same stem. If the request does not say which platform, read the current project (`package.json`, `app.json`, `expo` or `react-native` dependency) before choosing; if still unclear, name both in the output and mark the unlikely one under `Not:`.
4. **Check the map for an Owner.** A row whose Notes say "Owner of ..." for this job wins. Where the map marks `<!-- DECIDE -->` rationale, treat its stated owner as current.
5. **Check the scan output.** Confirm the Owner is actually installed (it appears in `scan.py --search`). A mapped skill that is not installed cannot be the Use line.

## Plan the Recommendation

Build the answer from these slots, in this order:

| Slot | Rule |
|------|------|
| `Use` | Exactly one: the Owner of the job. Never two. |
| `Also` | At most two. Complements that cover a different part of the job, not alternatives to the Use pick. |
| `Not` | The likely wrong picks: Namesakes, the web or mobile twin, and skills the map says lose an Overlap. Only ones a reasonable person might reach for. |
| `Lane` | The lane name and how many candidates you weighed. |
| `Unmapped` | Only if `scan.py --unmapped` lists an installed skill that could fit. |

If nothing installed fits, skip the slots and use the no-match line below.

**IMPORTANT**: Every command is the exact invocation including namespace: `/sharqiewicz:find-library`, `/interfaces:better-ui`, `/impeccable:impeccable polish` (a plugin skill with sub-commands shows the command the user types). Bare names only for bare installs. Never shorten a namespaced command.

## Write the Answer

Output exactly this shape and nothing else, no preamble:

```
Use:   /animate-expo  — RN + Expo animations; owner of "motion on mobile"
Also:  /gesture-ui    — drag/swipe physics (web-first; principles transfer)
Not:   /animate       — web only; its mobile sibling is animate-expo
Lane:  Motion · 2 candidates considered
```

- One short reason per line, after an em dash, in the map's wording where possible.
- Omit `Also:` and `Not:` lines that have nothing honest to say. Keep `Use:` and `Lane:` always.
- Align the dashes as above. Put each `Also:` and `Not:` on its own line; a second `Also:` gets its own line too.
- Add `Unmapped: /foo — run /sharqiewicz:make-skill-map` when an installed unmapped skill might fit. Do not recommend it as Use: it has no Owner decision yet.
- When a skill is manual-only (the map says `manual`), it still goes on the line; the user types it.
- When nothing installed fits, answer only: `Nothing installed fits → /find-skills <query>` with `<query>` filled in. `/find-skills` (Vercel's, installed via npx) searches skills.sh for new skills to install.

**NEVER:**
- Write, edit or delete any file, including `map.md` and the README, or run `scan.py --readme` / `--readme-out`
- Run, load or "try" the recommended skill; the output is a command for the user to type
- List more than one `Use:` line, or more than two `Also:` lines
- Show a command without its namespace when the skill is namespaced (`/better-ui` instead of `/interfaces:better-ui`)
- Recommend a skill that is not in the live scan, even if `map.md` still lists it
- Put an alternative to the Owner under `Also:`; an alternative belongs under `Not:` with the reason it loses
- Recommend the web skill for a React Native + Expo project, or the `-mobile` skill for a web project, without a `Not:` line naming the twin
- Invent a skill, an owner or a rationale the map and the scan do not support
- Pad the answer with explanation, a menu of options, or a lane tour

## Verify the Answer

- [ ] `map.md` was read in full and `scan.py` was run; nothing was written
- [ ] Exactly one `Use:`; at most two `Also:`
- [ ] Every command is exact, with namespace, and appears in the live scan
- [ ] Platform (web or mobile) matches the project, and any twin is under `Not:`
- [ ] Namesakes and lost Overlaps the user could confuse are under `Not:`
- [ ] `Unmapped:` present only when an installed unmapped skill could fit
- [ ] If nothing fit, the answer is only the `/find-skills` line

One skill owns each job; the answer's only job is to say which one, exactly as the user should type it.
