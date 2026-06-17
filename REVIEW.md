# Reviewer's orientation

A guide for a third party reviewing this codebase. For operating rules see `SKILL.md`; for how to
run/deploy and the project's history see `RESUME.md` / `handover.md`. This file points you at what
matters and what to scrutinize.

## What it is

A static editorial calendar for The New Yorker: scrape ~36 cultural sources (film, TV, theatre,
art, music, opera, dance) for *future* openings/premieres through 2026, dedupe, and render one
HTML page. A weekly GitHub Actions job refreshes and republishes it to GitHub Pages. No server,
no database at view time — the deploy artifact is a single `data/toy-calendar.html`.

## Run & verify (offline, ~seconds)

```bash
python3 -m pip install requests pytest
python3 -m pytest                 # 28 offline tests
python3 -c "import cultural_calendar.legacy"   # import sanity
# Full refresh needs network (+ TMDB_API_KEY for film); per-source:
python3 -m cultural_calendar --source tmdb_movies
```

`data/` (calendar.db, toy-calendar.html, raw/) is gitignored build output — regenerated, not
source. The committed `*_capture/*.json` files ARE source (hand-maintained or self-refreshed
caches; see below).

## Architecture in one screen

- **`cultural_calendar/core/config.py`** — paths, the `Source` dataclass, date constants,
  `today()`/`end_date()` (the 2026 horizon).
- **`cultural_calendar/registry.py`** — declarative dispatch: each source id → (tactic, importer,
  health range). Read this first to see the whole source map.
- **`cultural_calendar/legacy.py`** — the engine and every parser/importer (~3k lines, single
  module by design). Where almost all logic lives.
- **`sources.json`** — the source list (id, name, category, url, enabled).
- **`tests/`** — pytest: dates, credits/discipline, captures, registry/health, parsers.

Four fetch **tactics** (`registry.py`): `json_api`, `html`, `embedded_json`, `capture` (committed
fixture). Most sources are `html` → a per-source parser; many are dispatched to dedicated
importers in `_DEDICATED`.

## The non-obvious parts — where to focus review

1. **Resilience / data-integrity rule (the heart of recent work).** Principle: *a blocked or
   truncated fetch is a failed fetch, never an empty result; degrade to stale, never to empty.*
   - `fetch_text` — full browser headers; **on 403 retries with a plainer UA** (a WAF, Tate's,
     blocks the Chrome/125 Client-Hints string) before falling back to curl; retries 429s.
   - `fetch_valid_page(url, must_contain)` — returns `None` on a challenge/redirect/truncated/
     missing-boilerplate page (page-shape check).
   - `import_with_cache(conn, source, cache_path, parser, must_contain)` — validate → parse → on a
     clean fetch refresh the committed cache; on a bad fetch serve the cache and record `stale`.
     Used by V&A, Tate Modern/Britain, FLV. **Scrutinize:** the staleness classification and the
     "never overwrite cache to empty" guarantee.
   - `import_serpentine` — three independent live sources (paginated listing + annual page + press
     pages) merged, then the cache. Built because a blocked listing page once zeroed a real show.
     **Scrutinize:** `merge_by_title` precedence and the "stale only if all sources fail" logic.
   - `import_armory` — Cloudflare-walled; merges new live items onto an authoritative committed
     fixture without clobbering its per-discipline categories.

2. **Editorial correctness filters** (easy to get subtly wrong):
   - Forward-looking only: every dated row needs a future `date_start ≤ 2026-12-31`. "Through…/
     Closes…/Ongoing/Until…" are closing labels and must never become an opening (see
     `extract_exhibition_window`, `tate_opening_date`, `extract_pac_date`, the various parsers).
   - `dedupe_theatre` — same production across sources, keyed on normalized title (strips trailing
     subtitle) + date; Playbill outranks single-venue feeds.
   - `tmdb_screenwriters` — credit the `Screenplay` job, not source authors (Novel/Story) — e.g.
     don't credit Homer as the writer of Nolan's *Odyssey*.
   - `extract_met_opera_credits` — Director (the Met's "Production" label) + Conductor + top-2
     billed singers from the page's embedded cast JSON.

3. **Date parsing** across locales/formats — US "Mon D, YYYY", UK day-first "D Mon YYYY",
   ranges with the year only at the end, European "DD.MM.YYYY" (FLV). Concentrated in the
   `*_date`/`extract_*` helpers and well covered by `tests/test_dates.py`.

4. **Render** (`render_html`) — month→category editorial sheet with a pure-CSS Editorial⇄Calendar
   toggle; albums run-in in the calendar view; "On the horizon" for undated future signals.

## Known limitations / honest gaps (don't flag as surprises)

- **CI can't fetch Cloudflare/Akamai-walled sources** (Armory, Serpentine, partly FLV) from
  datacenter IPs — they serve `stale` from cache in CI by design. Freshness for those depends on
  running the fetch from a non-blocked IP (local, or a future VPS) and committing the artifact.
- **Still fixtures** (no scriptable upcoming surface found yet): NPG, Grand Palais, Centre
  Pompidou, MAM Paris. French-language date parsing would unlock the Paris venues.
- **Single module** (`legacy.py`) is intentional for this project's scale; not a layering bug.
- No secrets in the repo (TMDb token is env-only; Carnegie's Algolia key is a public,
  referer-restricted client key, hardcoded with a comment).

## Suggested review order

`registry.py` → `core/config.py` → in `legacy.py`: `fetch_text`/`fetch_valid_page`/
`import_with_cache` → a couple of parsers (`parse_va`, `import_serpentine`) → `dedupe_theatre`
and `tmdb_screenwriters` → `render_html` → the tests.
