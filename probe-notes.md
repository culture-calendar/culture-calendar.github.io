# Cultural Calendar: Initial Source Probe Notes

These notes record what the first public-source checks suggest about automation.

## TMDb

TMDb's movie discovery endpoint is suitable for deterministic film pulls. It supports release-date windows, U.S. region filtering, release-type filtering, sorting, watch-region/provider fields, people filters, genre filters, company filters, and popularity sorting.

Likely procedure:

- Pull movies from today through 2026-12-31 using release-date bounds and `region=US`.
- Use release type to separate theatrical, digital, physical, and TV where possible.
- Enrich promising items with credits, external IDs, videos, providers, and keywords.

Difficulty:

- Requires an API key.
- TMDb popularity is a helpful triage signal but not an editorial score.
- Release-date semantics will need testing: primary release, regional release, and platform availability can diverge.

## TVmaze

TVmaze is highly suitable for deterministic TV schedule pulls. It offers a free public JSON API, daily network schedules, web/streaming schedules, and a full future schedule endpoint.

Likely procedure:

- Pull `/schedule/full` weekly.
- Pull `/schedule?country=US&date=...` for rolling exact-date checks.
- Pull `/schedule/web` with both U.S. and global streaming settings.
- Use show endpoints for cast, crew, network, and web-channel enrichment.

Difficulty:

- The full schedule response is large and cached for 24 hours.
- Global streamers and country-specific web channels need separate treatment.
- Episode schedules are good; vague "coming this fall" TV announcements will still need trade/editorial sources.

## Broadway.org

Broadway.org is useful as an official Broadway League source for Broadway in New York. The public page exposes a list of current and scheduled NYC shows, with filters for musical/play/special event and now-playing/upcoming status.

Likely procedure:

- Weekly scrape the Broadway in NYC show list.
- Follow show links for theatre, status, ticket links, advisory, and special information.
- Use it as a canonical "is this Broadway?" source.

Difficulty:

- The listing is good, but previews, official opening, closing, and cast/creative details may need Playbill, IBDB, or show pages.
- It includes touring and international navigation; parser should focus only on the Broadway in NYC section.

## Playbill

Playbill is a strong theatre source because it exposes current Broadway, upcoming Broadway, Off-Broadway, London, touring, schedules, current/future theatre bookings, grosses, and cast-recording pages.

Likely procedure:

- Weekly scrape Broadway, upcoming Broadway, Off-Broadway, and current/future theatre bookings.
- Use Playbill news/search for announcements, extensions, closings, and major casting.
- Treat the listings as a discovery and enrichment source rather than the sole canonical source.

Difficulty:

- It mixes listings, ticketing, editorial, and industry resources.
- Some detail pages will be more useful than list cards.
- Need dedupe against Broadway.org and IBDB.

## The Met

The Met exhibitions page is a very promising official source. It exposes current, recently opened, closing soon, more temporary exhibitions, ongoing exhibitions, and upcoming exhibitions, with public date labels and exhibition links.

Likely procedure:

- Weekly scrape the exhibitions page.
- Parse upcoming/current sections separately.
- Follow individual exhibition pages for curators, artists, descriptions, and press links when editorially useful.

Difficulty:

- Some dates omit the year when the year is obvious to a reader; parser needs page-date context.
- "Ongoing" and "temporarily unavailable" should be valid date labels, not failures.

## MoMA

MoMA's exhibition page is highly useful and includes current exhibitions, upcoming exhibitions, installations/projects, performance programs, and film series. It also includes vague dates such as "Fall 2026," which is exactly the kind of planning signal we want to preserve.

Likely procedure:

- Weekly scrape current/upcoming exhibitions and installation/project sections.
- Preserve member preview dates separately from public opening dates when listed.
- Send film series and performance programs into separate subcategories.

Difficulty:

- The page includes exhibitions, installations, projects, film, performances, and events, so category filtering matters.
- Some entries use date labels rather than exact ranges.

## Met Opera

The Met Opera 2026-27 season page is compact but highly useful. It exposes production titles, composers, date ranges, and "New Production" flags.

Likely procedure:

- Weekly scrape 2025-26 and 2026-27 season pages.
- Extract title, composer, date range, new-production flag, and detail link.
- Follow detail links for cast, conductor, creative team, synopsis, and ticket dates.

Difficulty:

- The season listing is dense HTML; the parser should rely on links and known text markers, not visual layout.
- Date ranges do not include years in every visible label, so the season context must be applied.

## New York City Ballet

NYCB's season page is a good ballet source for the narrowed NYC scope. It exposes season blocks, date ranges, program links, galas, farewells, and specific program dates.

Likely procedure:

- Weekly scrape season blocks.
- Extract season name, season date range, program title, program date range, and detail link.
- Follow detail pages for repertory and choreographer data.

Difficulty:

- Some program dates are ranges without explicit years in the visible label.
- Casting/repertory detail may require deeper pages and later updates.

## Immediate Engineering Implication

The first scraper should store raw snapshots and parsed rows separately. We will need this because errors will often come from date-label parsing and section categorization, not from page access itself.

Recommended first local files:

- `sources.yml`: source definitions, categories, URLs, cadence, parser type.
- `schema.sql`: raw snapshots, normalized items, source records, people, item_people, and checks.
- `scrapers/`: one parser per source family.
- `data/raw/`: timestamped source snapshots.
- `data/calendar.db`: local SQLite database.
