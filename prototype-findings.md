# Toy Prototype Findings

Run date: 2026-06-12

## What Was Built

The first toy prototype lives in:

- `toy_calendar.py`
- `sources.json`
- `data/calendar.db`
- `data/raw/`
- `data/toy-calendar.html`

It tests a small public-source ingestion loop:

1. Fetch source.
2. Store raw snapshot.
3. Parse into rough normalized calendar rows.
4. Store rows in SQLite.
5. Render a simple HTML calendar table.

## Current Run Results

| Source | Result |
|---|---:|
| TMDb Movies | 100 film rows after API token was provided |
| TVmaze Full Future Schedule | wide aperture by default; conservative mode previously produced 189 filtered TV start-like items |
| Broadway.org Shows | 43 candidate theatre rows |
| Playbill Broadway | 80 candidate theatre rows |
| The Met Exhibitions | blocked/rate-limited with HTTP 429 |
| MoMA Exhibitions | blocked with HTTP 403 |
| Met Opera 2026-27 | 31 candidate opera rows |
| New York City Ballet Seasons | 69 candidate ballet rows |

## Important Lessons

### TMDb needs a user-provided token

TMDb requires a user-provided API bearer token. The script handles this gracefully by skipping TMDb when `TMDB_API_KEY` is missing.

The first successful run showed that `release_date.gte/lte` can admit old titles with a future U.S. re-release or alternate release date while displaying the old primary date. For the toy prototype, the importer now uses `primary_release_date.gte/lte` to keep the first-pass film calendar focused on genuinely upcoming primary releases.

### TVmaze is usable but too broad without editorial filtering

The raw full future schedule returned thousands of episodes. The toy now defaults to a wider aperture: U.S. items and major global streamers in English. It also supports a conservative mode that keeps season/series starts.

After review, the useful unit is not "all episodes" but show-level start signals: new series, season premieres, limited-series launches, major streamer drops, and likely TV-feature events. The importer now assigns a rough `importance_score` using platform, show type, season/episode number, genre, and whether the episode date matches the show premiere date. Wide mode keeps broad start signals; conservative mode applies a higher score threshold.

Remaining issue: the system still needs a better "importance" layer for TV. A show premiere on a major streamer is not automatically New Yorker-relevant.

### Broadway.org and Playbill fetch cleanly

Both theatre sources can be accessed publicly. The current parser is intentionally crude, so it captures some navigation and ticketing noise. This is a parsing problem, not an access problem.

Next step: source-specific parsers for show cards and show detail pages.

### The Met and MoMA have different access problems

The Met returned HTTP 429 to the toy's original lightweight user agent, but returned HTTP 200 with normal browser-like headers. The importer now uses browser-like public headers and can fetch The Met exhibitions page. The current Met parser still needs improvement because it captures exhibition links but not dates reliably.

MoMA returned HTTP 403 "Just a moment..." protection pages to:

- the exhibitions index
- a direct exhibition detail URL
- `sitemap.xml`
- `.json` and `format=json` variants

That means MoMA likely requires browser-session capture, another public endpoint discovered from a real browser session, or an alternate source for MoMA exhibitions.

Browser-session capture was tested successfully. A real browser context loaded `https://www.moma.org/calendar/exhibitions` and exposed rendered exhibition links and date labels in the DOM. The capture was saved to:

- `moma_capture/moma-exhibitions.html`
- `moma_capture/moma-exhibitions-text.txt`
- `moma_capture/moma-exhibition-links.json`

The toy importer now falls back to `moma_capture/moma-exhibition-links.json` when direct MoMA fetching is blocked. This currently imports 26 MoMA exhibition rows, including current, upcoming, installation/project, ongoing, and 2027 preview items. The next version should decide whether to keep all MoMA rows or filter to current/upcoming exhibitions only.

Possible responses:

- For The Met: keep direct fetching with browser-like headers, then write a source-specific parser.
- For MoMA: browser-based capture works as a fallback; still search for a sanctioned endpoint or feed before treating the browser capture as permanent infrastructure.
- For both: keep raw captured HTML snapshots as fixtures while writing parsers.

### Met Opera and NYCB are promising

Both fetched publicly and yielded candidate rows. The current parser is link-text based, so it gets useful data plus noise. The pages contain enough structure for better source-specific parsing.

After the source-specific parser pass:

- Met Opera now produces 21 real 2026-27 season/special-presentation rows, with date labels and `New Production` stored in the description field.
- NYCB now produces 23 season-program rows across Fall 2026, Winter 2027, and Spring 2027, instead of mixed navigation/support links.
- Broadway.org now produces a clean Broadway show list.
- Playbill now produces Broadway production-card rows rather than navigation links.
- The Met now produces exhibition-card rows and can be fetched with browser-like public headers. Dates are partially captured, but the parser still needs a better exhibition-card date extractor.

The toy remains intentionally rough, but it now demonstrates the right architecture: generic fetching plus source-specific parser functions.

## 2026-06-12 Enrichment Pass

The prototype now has separate tables for scraped detail pages and future model-written enrichment:

- `item_details`: detail-page title, meta description, raw path, and extracted text.
- `item_model_enrichment`: placeholder fields for future summaries, people, editorial tags, "why it matters," profile potential, confidence, and model name.

This keeps model output separate from scraped facts.

Broadway filtering now excludes obvious carried-over long-running shows such as `Wicked`, `Hamilton`, `The Lion King`, `Chicago`, `Aladdin`, and similar currently-running inventory. The theatre lane now emphasizes new or horizon items, while still keeping the source record auditable.

TVMaze still functions as a signal feed, but rows now read as planning signals rather than episode listings. Season starts are preserved, including new seasons of major-streamer shows, while mid-season episodes are excluded. Example: a future `House of the Dragon: Season 3 premiere` row is kept; an ordinary episode four would not be.

Detail-page enrichment currently fetches the first batch of detail pages for Broadway.org, Playbill, The Met, Met Opera, and NYCB. Broadway.org and The Met already provide useful meta descriptions. Met Opera detail pages need a more source-specific extractor because their generic text includes page chrome.

### Date parsing is central

The toy currently preserves date labels but does not fully normalize all human-readable dates. That is the correct first behavior. The next pass should improve parsing while always preserving original labels.

## Recommended Next Engineering Step

Do not build the final calendar UI yet. The next step should be to replace the generic link parser with source-specific parser modules for:

1. TVmaze
2. Broadway.org
3. Playbill
4. Met Opera
5. NYCB

Then solve museum access separately, because The Met and MoMA are not failing for the same reason as the other sources.
