#!/usr/bin/env python3
"""Enumerate every installed Claude Code skill and compare it with the curated skill map.

Read-only, stdlib-only. The only file it can ever write is the README block (--readme)
or the path given to --readme-out.

Usage:
  scan.py                      human listing of installed skills (with lane, when mapped)
  scan.py --json               the same data as JSON
  scan.py --unmapped           installed skills that map.md does not mention yet
  scan.py --stale              map.md entries that match no installed skill
  scan.py --search <words>     installed skills ranked by keyword hits (name, description, map job)
  scan.py --readme [PATH]      rewrite the block between <!-- skill-map:start --> and
                               <!-- skill-map:end --> in PATH (default ~/Programmer/skills/README.md)
  scan.py --readme-out FILE    write that block (markers included) to FILE instead; touches nothing else
  --map PATH                   use another map.md (default: map.md next to this script)

Channels:
  npx-skills  ~/.claude/skills/<name> symlinks into ~/.agents/skills (tracked in ~/.agents/.skill-lock.json)
  own-repo    ~/.claude/skills/<name> symlinks to a repo you own
  folder      ~/.claude/skills/<name> is a real folder
  skills-dir  ~/.claude/skills/<dir> is a whole plugin (has .claude-plugin/plugin.json); invoked <plugin>:<skill>
  plugin      shipped inside an installed plugin; invoked <plugin>:<skill>
  command     ~/.claude/commands/<name>.md (or <name>/SKILL.md)
"""
import fnmatch, glob, json, os, re, sys

HOME = os.path.expanduser("~")
SKILLS = f"{HOME}/.claude/skills"
COMMANDS = f"{HOME}/.claude/commands"
LOCK = f"{HOME}/.agents/.skill-lock.json"
PLUGINS = f"{HOME}/.claude/plugins/installed_plugins.json"
DEFAULT_MAP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "map.md")
DEFAULT_README = f"{HOME}/Programmer/skills/README.md"
START, END = "<!-- skill-map:start -->", "<!-- skill-map:end -->"


def frontmatter(path):
    try:
        text = open(path, encoding="utf-8", errors="ignore").read()
    except OSError:
        return {}
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    out, key = {}, None
    for line in (m.group(1).splitlines() if m else []):
        kv = re.match(r"^([\w-]+):\s*(.*)$", line)
        if kv:
            key = kv.group(1)
            out[key] = kv.group(2).strip().strip("\"'>").strip()
        elif key and line[:1] in (" ", "\t"):
            out[key] = (out[key] + " " + line.strip()).strip()
    return out


def row(name, invoke, channel, source, fm):
    return dict(name=name, invoke=invoke, channel=channel, source=source,
                manual=fm.get("disable-model-invocation") == "true",
                description=fm.get("description", ""))


def is_plugin_dir(path):
    return os.path.isfile(os.path.join(path, ".claude-plugin", "plugin.json"))


def installed():
    lock = {}
    if os.path.exists(LOCK):
        try:
            lock = json.load(open(LOCK)).get("skills", {})
        except (OSError, ValueError):
            pass

    # 1. ~/.claude/skills: plain skills, and whole plugins loaded as <dir>@skills-dir
    for name in sorted(os.listdir(SKILLS)) if os.path.isdir(SKILLS) else []:
        path = os.path.join(SKILLS, name)
        if is_plugin_dir(path):
            try:
                manifest = json.load(open(os.path.join(path, ".claude-plugin", "plugin.json")))
            except (OSError, ValueError):
                continue
            plugin = manifest.get("name", name)
            entries = manifest.get("skills") or [os.path.dirname(p) for p in
                                                  glob.glob(path + "/skills/*/SKILL.md")]
            for rel in entries:
                d = os.path.join(path, rel)
                md = d if d.endswith("SKILL.md") else os.path.join(d, "SKILL.md")
                if not os.path.isfile(md):
                    continue
                fm = frontmatter(md)
                sname = fm.get("name") or os.path.basename(os.path.dirname(md))
                yield row(sname, f"/{plugin}:{sname}", "skills-dir", f"{name}@skills-dir", fm)
            continue  # never treat a plugin dir as a plain skill
        skill_md = os.path.join(path, "SKILL.md")
        if not os.path.isfile(skill_md):
            continue
        target = os.path.realpath(path)
        if os.path.islink(path) and "/.agents/skills/" in target:
            channel, source = "npx-skills", lock.get(name, {}).get("source", "?")
        elif os.path.islink(path):
            channel, source = "own-repo", target
        else:
            channel, source = "folder", "?"
        yield row(name, f"/{name}", channel, source, frontmatter(skill_md))

    # 2. installed marketplace plugins
    plugins = {}
    if os.path.exists(PLUGINS):
        try:
            plugins = json.load(open(PLUGINS))
        except (OSError, ValueError):
            pass
    plugins = plugins.get("plugins", plugins)
    seen = set()
    for key, installs in plugins.items():
        install = installs[0] if isinstance(installs, list) else installs
        plugin = key.split("@")[0]
        for md in sorted(glob.glob(install.get("installPath", "") + "/**/SKILL.md", recursive=True)):
            fm = frontmatter(md)
            name = fm.get("name") or os.path.basename(os.path.dirname(md))
            if (plugin, name) in seen:
                continue
            seen.add((plugin, name))
            yield row(name, f"/{plugin}:{name}", "plugin", key, fm)

    # 3. user commands (~/.claude/commands/<name>.md, or <name>/SKILL.md)
    for p in sorted(glob.glob(COMMANDS + "/*")):
        base = os.path.basename(p)
        if os.path.isdir(p) and os.path.isfile(os.path.join(p, "SKILL.md")):
            yield row(base, f"/{base}", "command", "~/.claude/commands", frontmatter(os.path.join(p, "SKILL.md")))
        elif p.endswith(".md"):
            yield row(base[:-3], f"/{base[:-3]}", "command", "~/.claude/commands", frontmatter(p))


# ---------- skill map ----------

def parse_map(path):
    """Rows of every table whose header cell is 'Skill'. Only the first column counts as a mention."""
    entries, heading, in_table = [], "", False
    try:
        lines = open(path, encoding="utf-8").read().splitlines()
    except OSError:
        return entries
    for i, line in enumerate(lines, 1):
        if line.startswith("## "):
            heading, in_table = re.split(r"\s+[—-]\s+", line[3:].strip())[0], False
            continue
        if not line.startswith("|"):
            in_table = in_table and False
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and cells[0].lower() == "skill":
            in_table = True
            continue
        if not in_table or set(cells[0]) <= set("-: "):
            continue
        cmds = re.findall(r"`(/[^`\s]+)`", cells[0])
        if cmds:
            entries.append(dict(patterns=cmds, lane=heading, job=cells[1] if len(cells) > 1 else "",
                                notes=cells[2] if len(cells) > 2 else "", line=i))
    return entries


def map_lookup(entries):
    def find(invoke):
        for e in entries:
            if any(fnmatch.fnmatchcase(invoke, p) for p in e["patterns"]):
                return e
        return None
    return find


def readme_block(map_path):
    text = open(map_path, encoding="utf-8").read()
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"(?m)^[ \t]+$", "", text)
    text = re.sub(r"(?m)[ \t]+\|$", " |", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"(?m)^# .*\n", "## Skill map\n", text, count=1)  # title -> README section
    text = re.sub(r"(?m)^## (?!Skill map)", "### ", text)          # lanes one level down
    note = "<!-- generated from find-skill/map.md by find-skill/scan.py --readme; edit the map, not this block -->"
    return f"{START}\n{note}\n{text.strip()}\n{END}\n"


def write_readme(map_path, readme_path):
    block = readme_block(map_path)
    text = open(readme_path, encoding="utf-8").read()
    pat = re.compile(re.escape(START) + r".*?" + re.escape(END) + r"\n?", re.S)
    if not pat.search(text):
        sys.exit(f"error: {readme_path} has no {START} ... {END} block; add the two markers where "
                 "the skill map should go, then rerun")
    open(readme_path, "w", encoding="utf-8").write(pat.sub(lambda _: block, text, count=1))
    print(f"rewrote skill-map block in {readme_path}")


# ---------- cli ----------

def short(s, n=88):
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def arg_after(flag, default=None):
    if flag in sys.argv:
        i = sys.argv.index(flag)
        if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("--"):
            return sys.argv[i + 1]
    return default


def main():
    argv = sys.argv[1:]
    map_path = arg_after("--map", DEFAULT_MAP)
    if "--readme-out" in argv:
        out = arg_after("--readme-out")
        if not out:
            sys.exit("error: --readme-out needs a file path")
        open(out, "w", encoding="utf-8").write(readme_block(map_path))
        print(f"wrote skill-map block to {out}")
        return
    if "--readme" in argv:
        write_readme(map_path, os.path.expanduser(arg_after("--readme", DEFAULT_README)))
        return

    data = list(installed())
    entries = parse_map(map_path)
    find = map_lookup(entries)
    for r in data:
        e = find(r["invoke"])
        r["lane"] = e["lane"] if e else None
        r["mapped"] = e is not None

    if "--json" in argv:
        print(json.dumps(data, indent=1, ensure_ascii=False))
    elif "--unmapped" in argv:
        rest = [r for r in data if not r["mapped"]]
        print(f"{len(rest)} unmapped of {len(data)} installed")
        for r in rest:
            print(f"{r['invoke']:<40} {r['channel']:<10} {short(r['description'], 70)}")
    elif "--stale" in argv:
        invokes = [r["invoke"] for r in data]
        stale = [(e, p) for e in entries for p in e["patterns"]
                 if not any(fnmatch.fnmatchcase(i, p) for i in invokes)]
        print(f"{len(stale)} map entries match no installed skill")
        for e, p in stale:
            print(f"{p:<40} map.md:{e['line']}  lane {e['lane']}")
    elif "--search" in argv:
        words = [w.lower() for w in argv[argv.index("--search") + 1:] if not w.startswith("--")]
        scored = []
        for r in data:
            e = find(r["invoke"])
            hay = f"{r['name']} {r['description']} {e['job'] if e else ''} {e['notes'] if e else ''}".lower()
            score = sum(hay.count(w) + (3 if w in r["name"].lower() else 0) for w in words)
            if score:
                scored.append((score, r))
        for score, r in sorted(scored, key=lambda t: -t[0])[:15]:
            print(f"{score:>3}  {r['invoke']:<40} {r['lane'] or 'UNMAPPED':<14} {short(r['description'], 60)}")
    else:
        print(f"{len(data)} installed skills, {sum(not r['mapped'] for r in data)} unmapped\n")
        for r in data:
            flag = "manual" if r["manual"] else "auto"
            print(f"{r['invoke']:<40} {r['channel']:<10} {flag:<6} {r['lane'] or 'UNMAPPED':<14} "
                  f"{short(r['description'], 60)}")


if __name__ == "__main__":
    main()
