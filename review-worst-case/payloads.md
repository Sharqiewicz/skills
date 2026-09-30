# Worst-case payloads

Copy these exactly. They are chosen for known failure modes, not for variety.

## Length
- `""` (empty), `" "` (whitespace only), `"a"` (1 char)
- A value at the limit, limit − 1 and limit + 1 for every declared max (e.g. 254, 255, 256)
- 10,000 characters of lorem ipsum, pasted in one go
- One long word with no spaces: `Wolfeschlegelsteinhausenbergerdorffvoralternwarengewissenhaftschaferswessenschafewarenwohlgepflegeundsorgfaltigkeitbeschutzenvonangreifendurchihrraubgierigfeinde`
- A long URL with no break opportunities: `https://example.com/` followed by 300 characters and no `/` or `-`
- Leading and trailing whitespace: `"  Anna  "`

## Unicode
- Polish diacritics: `Zażółć gęślą jaźń`
- ZWJ emoji family: `👨‍👩‍👧‍👦` (a single glyph made of 7 code points, so length checks disagree)
- Flag emoji: `🇵🇱🇺🇦`
- Combining marks (Zalgo): `Z̷̢̛͖a̶̡͓l̸̨̛g̴̢̛o̵̧͝`
- RTL: `مرحبا بالعالم`, `שלום עולם`
- Mixed bidi: `Order #123 للعميل`
- RTL override: `abc‮dcba` (flips the rest of the line)
- CJK: `東京都渋谷区神宮前一丁目`
- Zero-width space: `Anna​` (looks the same as `Anna`, so it breaks uniqueness and search)
- Non-breaking space: `Anna Kowalska`
- Full-width: `ＡＢＣ１２３`

## Identity: names
- `O'Brien`, `D'Angelo` (apostrophes break naive quoting)
- `Null`, `undefined`, `None`, `true`, `NaN`
- A single name (mononym): `Prince`
- `X Æ A-12`
- Hyphenated and very long: `Maria-Magdalena Wolfeschlegelsteinhausenbergerdorff-Kowalska`
- An emoji in a name: `Anna 🌸`
- An all-caps initials name: `J. R. R.`

## Identity: emails (all on reserved domains)
- Plus addressing: `anna+tag@example.com`
- Subaddress plus dots: `a.n.n.a+x.y@example.com`
- Apostrophe: `o'brien@example.com`
- Quoted local part: `"anna kowalska"@example.com`
- Uppercase duplicate: `Anna@Example.com` vs `anna@example.com`
- IDN domain: `anna@münchen.example`
- Long subdomain: `anna@a.very.deeply.nested.subdomain.example.com`
- Max length: a 64-character local part + `@` + a domain padded to 254 characters in total
- Trailing whitespace: `"anna@example.com "`

## Numbers & dates
- `0`, `-0`, `-1`, `0.1 + 0.2`, `999999999999`, `9007199254740993` (MAX_SAFE_INTEGER + 2)
- `1e21` (JS prints it in scientific notation)
- Locale formats: `1.000,50` vs `1,000.50`
- Currency with no decimals: JPY `¥1000`
- Dates: `2024-02-29`, `1970-01-01`, `9999-12-31`, the day DST starts, the day DST ends
- Time zones: `UTC+14` (Kiribati), `UTC−12`, `UTC+5:45` (Nepal)

## Volume
- 0 items (empty state), 1 item, 2 items (singular/plural labels)
- 100, 1,000 and 10,000 items in a list or table
- 500 labels or tags on a single entity
- 50 options in a select or dropdown
- Deep nesting: comments or folders 20 levels deep
- 10 MB of text in a textarea, and a 50 MB file upload

## Escaping (own local app only)
- `<script>alert(1)</script>` and `<img src=x onerror=alert(1)>`: must render as text
- `'; DROP TABLE users; --`: must be stored literally
- Markdown: `**bold** [link](javascript:alert(1))`
- Template syntax: `{{name}}`, `${name}`, `%s`, `%d`
- Path-like: `../../etc/passwd`, `CON`, `name.pdf.exe`

## Behavior
- Double-click submit and press Enter repeatedly
- Submit, then press browser Back and submit again
- The same record open in two tabs, edited in both
- Offline in the middle of a submit; a slow 3G profile
- Paste into a field that has `maxLength`
- Toggle one control on and off 20 times quickly

## Mobile (React Native + Expo, iOS)
- Dynamic Type: `xcrun simctl ui booted content_size accessibility-extra-extra-extra-large`
- Smallest supported device (e.g. iPhone SE) and landscape orientation
- Dark mode: `xcrun simctl ui booted appearance dark`
- Keyboard open over the lowest input on the screen
- A long German translation string in every button and tab label
- Reduce Motion on; Bold Text on
- App backgrounded in the middle of a form, then restored

## Data layer
- Case-insensitive duplicates against a case-sensitive unique index
- `NULL` in every optional column, including optional foreign keys
- An orphaned child whose parent was deleted
- A value longer than the column, where the DB truncates silently
- 100,000 rows, then sort, filter, paginate and search
- Two concurrent inserts with the same unique key
