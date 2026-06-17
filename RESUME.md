# Resume here — Cultural Calendar handoff

A standalone guide to pick this project up on another machine. The whole project is a git
repo, so "moving machines" is mostly a clone plus credentials.

## What this is

An editorial planning tool for The New Yorker tracking culturally significant upcoming items
through end of 2026 across film, TV, theatre, art, music, opera, and dance/ballet — now with
major **London/Paris art institutions** alongside the NY core.

- **Live:** https://culture-calendar.github.io
- **Repo:** `culture-calendar/culture-calendar.github.io` (public)
- **This machine's clone:** `~/Documents/Cultural Calendar 2/`
- **Refreshes itself:** a weekly GitHub Actions cron rebuilds and redeploys the page.

Read `SKILL.md` for the operating rules (authoritative) and `handover.md` for session history.

## Get it running on a new machine

```bash
git clone https://github.com/culture-calendar/culture-calendar.github.io.git
cd culture-calendar.github.io
python3 -m pip install requests          # only runtime dep; add pytest for tests
export TMDB_API_KEY=<your TMDb v4 read token>   # or put it in ~/.zshrc
python3 -m cultural_calendar             # full refresh → data/toy-calendar.html
python3 -m pytest                        # 28 tests, all offline
```

Preview: `python3 -m http.server 8765 --bind 127.0.0.1` →
`http://127.0.0.1:8765/data/toy-calendar.html`.

### Credentials (the two things that don't come with the clone)

1. **`TMDB_API_KEY`** — TMDb v4 read token in the env / `~/.zshrc`. Without it, film shows 0 and
   everything else still works. Never write it into project files. The repo's Actions secret is
   already set, so CI is unaffected.
2. **`gh` auth for push/deploy** — `brew install gh && gh auth login` (GitHub.com, HTTPS,
   browser). **Gotcha learned the hard way:** the SSH keys on Henry's iMac are *deploy keys for a
   different repo (`hdfinder-tech/frontlist`)* and CANNOT push here — use `gh` over HTTPS, which
   wires up the macOS keychain. `gh` is authenticated as account **`hdfinder-tech`** (token has
   `repo` + `workflow`). On Henry's old-bash shell, **type commands, don't paste** (bracketed-paste
   markers `00~`/`01~` corrupt pasted lines).

## How a refresh / deploy works

- Local: `python3 -m cultural_calendar [--source ID]` regenerates `data/calendar.db` +
  `data/toy-calendar.html` (both gitignored).
- Deploy: pushing code does **not** auto-deploy. Trigger with
  `gh workflow run weekly-refresh.yml --ref main`, then `gh run watch <id>`. It runs tests →
  refreshes every source → publishes to Pages. The weekly cron does this automatically.
- Health: each run prints a drift warning for any source whose row count leaves its
  `EXPECTED_ROWS` range (`registry.py`). The rendered page's "Source runs" `<details>` lists the
  latest run per source (status + message), e.g. `stale — … from last-good cache`.

## Source roster (36 sources)

- **Film** — TMDb (US theatrical/limited, top ~50 by popularity, all credited). Screenwriter =
  the `Screenplay` job (falls back to `Writer`); source authors (Novel/Story) are NOT credited as
  writers (`tmdb_screenwriters`).
- **TV** — TVMaze (premieres/launches only).
- **Theatre** — Broadway.org (canonical) + IBDB deduped; Playbill Off-Broadway + BAM + the NYC
  venues below. `dedupe_theatre` collapses the same show across sources by normalized title (now
  strips trailing subtitles) + date; Playbill outranks the single-venue feeds (BAM, PAC, Shed,
  Armory).
- **Art (NY)** — Met, MoMA, Whitney, Brooklyn, MOCA, LACMA, Pace, Gagosian, Guggenheim, New
  Museum, Frick.
- **Art (London/Paris)** — see "International art" below.
- **Music** — Metacritic albums; NY Phil (CloudFront API) + Carnegie (Algolia) concerts. NYC
  venues (PAC, Shed, Armory) route their concert rows into the Concerts lane via
  `CONCERT_MUSIC_SOURCES`. Rendered as Music · Concerts and Music · Albums.
- **Opera/Ballet** — Metropolitan Opera (named in full; per-production credits = Director +
  Conductor + two lead singers via `extract_met_opera_credits`), NYCB.
- **NYC performing-arts venues** — PAC NYC (Perelman, scriptable), The Shed (scriptable), Park
  Avenue Armory (Cloudflare-walled → live-with-cache).

## Live-vs-fixture & the integrity rule (important architecture)

The hard-won rule: **a blocked/truncated fetch is a FAILED fetch, never an empty programme.** A
failed scrape makes data *stale*, never empty.

- `fetch_text` sends full browser headers, **retries a 403 with a plainer UA** (Tate's WAF blocks
  the Chrome/125 Client-Hints string) before a curl fallback, and retries 429s.
- `fetch_valid_page(url, must_contain=…)` returns `None` on a challenge/redirect/truncated/
  missing-boilerplate page (page-shape check), so callers keep last-good data.
- `import_with_cache(conn, source, cache_path, parser, must_contain)` is the shared pattern for
  scriptable-but-occasionally-blocked sources: validate fetch → parse → **on a clean fetch refresh
  the committed cache; on a bad fetch serve the cache and record `stale`** (never empty).
  - **Live via `import_with_cache`:** V&A (schema.org microdata), Tate Modern & Tate Britain
    (whats-on cards, UK day-first dates), Fondation Louis Vuitton (the `/en/programme/a-venir`
    page is server-rendered even though the rest of FLV is an Akamai-gated SPA). Their
    `*_capture/*.json` files are the last-good caches.
- **Serpentine** (`import_serpentine`) — three independent live sources merged, then the cache:
  (1) paginated `/whats-on/` crawl, (2) annual `2026-at-serpentine` page, (3) per-exhibition
  press pages. Any one/two blocked can't hide a show; cache only when all three fail. This was
  built because a blocked page 2 once zeroed a real exhibition.
- **Park Avenue Armory** (`import_armory`) — one request to the current-season page; merges any
  new live items onto the authoritative committed fixture (which carries per-discipline
  categories the page's section markup provides), never clobbering it.
- **Self-refreshing fixtures (live in CI from a non-blocked path, else cache):** Met museum
  (`metmuseum.org` 429s CI), Met Opera (`metopera.org` serves CI a 0-link shell).
- **Pure committed fixtures (hand-refresh seasonally):** MoMA, Frick (Claude-in-Chrome capture,
  see `cultural_calendar/capture/README.md`); NPG London, Centre Pompidou (off-site
  "Constellation"), Grand Palais, Musée d'Art Moderne de Paris — these have no server-rendered
  upcoming surface I could find (JS apps / current-only listings / French prose dates).

### CI reality (the off-CI decision)

GitHub Actions' datacenter IPs are scored badly by Cloudflare/Akamai, so the Cloudflare-walled
sources (Armory, Serpentine, FLV in part) usually show **`stale` from cache in CI** — correct and
clearly labelled, never empty. To keep them *fresh*, the live fetch should run from a non-blocked
endpoint (a local run, or a stable **VPS/newsroom box**) that commits the refreshed `*_capture`
artifact; CI then just consumes it. This is an **infra decision, not a code change** — the code is
already shaped for it. Local runs are adequate for manual operation.

## Presentation

`render_html` is month → category on a parchment editorial sheet, with a **pure-CSS Editorial ⇄
Calendar toggle**:
- **Editorial view** — month → category; Music split into Concerts/Albums (two-column lists).
- **Calendar view** — day-by-day; each opening/premiere day lists all categories beneath it.
  Album releases are run into one comma-separated "Albums" line (low-signal, high-volume).
- Undated future signals go to **"On the horizon"** (ballet seasons render two-column).
- Role-aware credit line per entry (`format_credits`).

## Adding / refreshing the hand-maintained venues (no Claude Code needed, in principle)

Turning prose into rows needs a model, so a bare spreadsheet isn't self-service. Options discussed
(none built yet — your call):
1. **GitHub issue → Claude Action → PR-preview** (recommended): paste prose into an issue, an
   Action parses it to fixture JSON and opens a PR you glance-merge. Needs an `ANTHROPIC_API_KEY`
   secret. True paste-and-forget with an editorial check.
2. **ChatGPT emits the JSON**, you paste it into the fixture via GitHub's web editor. No build.
3. Status quo: paste prose to Claude Code; it updates the fixture.

Repeatable skill for any new JS/anti-bot venue: find the **smallest server-rendered surface** (an
"upcoming"/"à venir" page, later pagination, a press page, or schema.org microdata/ld+json) before
concluding it needs a fixture. FLV and Serpentine were cracked this way; don't fight the bot wall.

## Open threads / deferred

- **Still fixtures (could go live with more work):** NPG (no structured data; scriptable with a
  parser), MAM Paris (its site lists only *current* shows — upcoming aren't published yet), Grand
  Palais / Centre Pompidou (JS apps). French-language date parsing would help the Paris venues.
- **Source diversity** beyond Serpentine: extend only if another venue shows the same
  pagination/blocking/reordering symptoms.
- **Off-CI refresh host** for the Cloudflare-walled venues (see above) — infra decision.
- **Not yet wired (NY galleries):** Zwirner, Hauser & Wirth (Next.js RSC), Marian Goodman.
- **Music tours / podcasts** — deferred (API-key-gated / no clean dated feed).

## Context for a Claude session on the new machine

- Load `SKILL.md` first (authoritative rules). Verify before working:
  `python3 -m pytest` (28 tests) and a quick `python3 -c "import cultural_calendar.legacy"`.
- Security discipline: TMDb token stays in the env, never in files (`[ -n "$TMDB_API_KEY" ]`,
  never echo). Carnegie's Algolia key is a public referer-restricted client key (fine hardcoded).
- Henry has granted standing autonomy for relevant runs/commits/deploys/inspections — act, then
  report; don't ask permission per action.
