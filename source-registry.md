# Cultural Calendar: Source Registry

This registry turns the broad source strategy into determinate procedures: where to look, how to collect data, what fields we expect, and what is likely to break.

## Source Tiers

- Tier 1: canonical or near-canonical source with stable API or stable public page.
- Tier 2: reliable public page, but with source-specific scraping and normalization.
- Tier 3: discovery or editorial-signal source; useful for importance, incomplete as canonical data.
- Tier 4: subscription or session-based source; defer until public sources prove insufficient.

## Registry

| Category | Source | Tier | Determinate Procedure | Expected Fields | Main Difficulty | First-Pass Priority |
|---|---:|---:|---|---|---|---:|
| Film | TMDb Discover Movie API | 1 | Weekly API query for `release_date.gte`, `release_date.lte`, `region=US`, and release type filters through 2026; enrich selected items with credits and external IDs. | title, release date, region, release type, cast, crew, companies, popularity, genres, TMDb ID | Requires API key; popularity is useful but not editorial judgment; exact theatrical/streaming distinction needs care. | 1 |
| TV | TVmaze full schedule and web schedule APIs | 1 | Weekly pull of `/schedule/full`, plus date-window pulls for `/schedule` and `/schedule/web` for U.S. and global streaming; dedupe by show/episode IDs. | show, episode, air date, network/web channel, country, runtime, show links, cast/crew via show endpoints | Full schedule is large and cached daily; global streamers are handled differently from country-tied networks. | 1 |
| Film/TV | IMDb non-commercial datasets | 2 | Download periodic TSV snapshots; use for ID matching, people, title disambiguation, and credit enrichment. | titles, people, title IDs, name IDs, known-for, principals | Licensing and bulk update flow; not primarily a future-release calendar. | 2 |
| Film | The Numbers release schedule | 2 | Weekly scrape release calendar pages for 2026; normalize title/date/distributor/release type; cross-check against TMDb. | title, release date, distributor, release scale when present | HTML structure and pagination may change; limited/streaming distinction may be incomplete. | 2 |
| Film/TV | Metacritic | 2/3 | Weekly search/pull for movies and TV using upcoming/current-release keywords, then match results against TMDb/TVmaze titles. Use Metascore and "must see" status as editorial signal after release. | title, type, Metascore, release date, year, genres, rating, description, URL | Search-based, not a canonical future calendar; scores appear only after enough reviews; needs dedupe and title matching. | 2 |
| Film/TV | Apify Metacritic Scraper | 2/3 | If direct Metacritic access is unreliable, run the Apify actor with controlled keyword sets such as "2026 movie", "Netflix 2026", "HBO 2026", and known candidate titles; import JSON/CSV results. | Metacritic ID, title, type, Metascore, release date, year, genres, rating, description, image URL, URL, scraped timestamp | Requires Apify token and pay-per-result cost; actor is community-maintained; search API returns relevance order, not date order; detail-page data and user scores are out of scope. | 2 |
| Film/TV | Variety, Deadline, Hollywood Reporter, The Ankler | 3/4 | Public RSS/search first for release-date announcements and casting; use subscriptions only if public feeds miss high-value items. | announcement text, people, dates, studios/platforms | Articles are prose; extraction needs NLP and manual confidence flags. | 3 |
| Broadway | Broadway.org show list | 1 | Weekly scrape official Broadway League show list; capture current and upcoming NYC shows; follow show detail pages for theatre and status. | title, theatre, now/upcoming status, type, ticket links, special info | Good canonical list, but may not expose previews/opening/closing in one clean field. | 1 |
| Broadway/Off-Broadway | Playbill show listings | 1/2 | Weekly scrape Broadway, upcoming Broadway, Off-Broadway, London, and current/future theatre bookings pages. | title, theatre, opening date, category, links, sometimes trend/status | Useful pages may be partly templated; list counts and cards are easy, detail fields vary. | 1 |
| Broadway | IBDB | 2 | Weekly lookup for known Broadway titles from Broadway.org/Playbill; enrich with production IDs and credits. | production ID, opening/closing, theatre, cast/creative credits | Better for canonical history than discovery; future data may lag announcements. | 2 |
| Off-Broadway | Institution calendars | 2 | Weekly scrape known priority institutions: Public, NYTW, BAM, Lincoln Center Theater, Roundabout, MTC, Second Stage, Atlantic, Signature, Playwrights Horizons, MCC, Vineyard, Soho Rep, St. Ann's, Classic Stage, Irish Rep, TFANA, La MaMa, Ars Nova. | title, venue, run dates, opening/previews if available, artists, description | Many different site structures; some announce seasons as prose pages or PDFs. | 1 |
| London Theatre | Official London Theatre / London Theatre / WhatsOnStage | 2/3 | Monthly scrape upcoming West End lists and news; only keep major debut productions and high-profile transfers not already NYC-originated. | title, theatre, opening, cast, creative team, source note | Need editorial filter to avoid routine London listings. | 3 |
| Art NYC | The Met exhibitions page | 1 | Weekly scrape current/upcoming exhibitions; parse date ranges and exhibition links; follow detail pages for curators/artists when needed. | title, start/end date, status, URL, venue, description | Homepage has good lists; detail pages may be needed for people and importance. | 1 |
| Art NYC | MoMA exhibitions page | 1 | Weekly scrape current/upcoming exhibitions, installations, performance programs, and film series links; preserve vague date labels such as "Fall 2026." | title, date range/date label, category, URL, member previews | Includes both exhibitions and smaller installations; requires category filtering. | 1 |
| Art NYC | Whitney, Guggenheim, New Museum, Brooklyn Museum, Frick, Studio Museum, ICP, Dia, PS1 | 2 | Weekly scrape each official exhibitions page; store raw HTML snapshots and normalized events. | title, dates, venue, artist/curator if available, URL | Site-by-site adapters; some pages use client-side rendering. | 1 |
| Art International | Tate, National Gallery, Royal Academy, Serpentine, Centre Pompidou, Louvre, Musee d'Orsay, Fondation Louis Vuitton | 2/3 | Monthly scrape official exhibition pages; apply high-profile filter before inclusion. | title, dates, institution, city, artist | The hard part is relevance filtering, not access. | 3 |
| Music Albums | MusicBrainz API | 1/2 | Weekly query recent/future releases where available; use primarily for identity and metadata enrichment. | artist, release title, date, label, release group, IDs | Future releases are incomplete because data depends on community entry. | 2 |
| Music Albums | Metacritic, AllMusic, Album of the Year | 2/3 | Weekly scrape or query upcoming/new-release pages; track anticipated albums and dates; cross-check with artist/label pages. | artist, album, date, label/genre if present, Metascore when available | Some pages may resist scraping or shift HTML; dates may be incomplete; Metacritic is better after review embargoes lift than for long-lead release discovery. | 2 |
| Music News | Pitchfork, Stereogum, NPR Music, Resident Advisor, Consequence, BrooklynVegan | 3 | RSS/search weekly for "announces album", "release date", "tour", "NYC", "Los Angeles"; NLP extract candidates. | article, artist, album/event, date, venue, source quote | Prose extraction and duplicate handling. | 3 |
| Music Events | Ticketmaster Discovery API | 1 | Weekly API query by classification and city for New York and Los Angeles through 2026; filter for major venues/artists. | event, date, venue, city, artist, ticket link | Coverage skewed toward Ticketmaster ecosystem; noisy without artist/venue filters. | 2 |
| Opera NYC | Met Opera season page | 1 | Weekly scrape current and next season pages; extract production title, composer, date range, new-production flag, and event pages. | title, composer, dates, new production, URL | HTML line is compact; detail enrichment needs per-production pages. | 1 |
| Opera Additional | Carnegie Hall, Lincoln Center, BAM, Operabase | 2/4 | Public pages first for concert opera/vocal programming; test Operabase public search before using account access. | title, date, venue, artists, company | Operabase may be subscription-gated; public calendars are fragmented. | 3 |
| Ballet NYC | New York City Ballet season page | 1 | Weekly scrape season blocks and production links; capture fall/winter/spring programs, galas, farewells, and repertory pages. | program, date range, specific dates, venue, links | Individual repertory/casting details may require deeper pages; date ranges can be season-relative. | 1 |
| Ballet NYC | ABT, Joyce Theater, BAM, Lincoln Center | 2 | Weekly scrape NYC ballet/dance programming pages; include major premieres, company visits, galas, and limited runs. | title/program, company, dates, venue, choreographers if available | Dance programming has mixed genres; needs category tagging. | 2 |

## Determinate Search Procedures

### Weekly API Pulls

- TMDb: pull all U.S. film releases from current date through December 31, 2026, by release date; enrich only items passing rough importance filters.
- TVmaze: pull full future schedule, U.S. schedule, and web schedule; keep premieres, season starts, finales, high-profile shows, and new series.
- Ticketmaster: pull music events in New York and Los Angeles; filter by venue list and artist prominence.
- MusicBrainz: query release groups/releases for future dates and use as enrichment rather than the sole discovery mechanism.

### Weekly Official-Page Scrapes

- Theatre NYC: Broadway.org, Playbill, priority Off-Broadway institutions.
- Art NYC: Met, MoMA, Whitney, Guggenheim, New Museum, Brooklyn Museum, Frick, Studio Museum, ICP, Dia, PS1.
- Opera NYC: Met Opera, Carnegie Hall vocal/opera pages, Lincoln Center.
- Ballet NYC: NYCB, ABT, Joyce, BAM, Lincoln Center.

### Monthly Wider Sweeps

- London theatre: high-profile West End debut productions only.
- London/Paris art: major exhibitions at top institutions only.
- Trade/editorial signal sources: screen, music, theatre, art announcement searches.

## Difficulties Already Visible

- Future dates come in mixed precision: exact dates, date ranges, seasons, quarters, and "ongoing." The schema must preserve the original label.
- Many official sources are accessible but not uniformly structured. We should expect source-specific parsers rather than one universal scraper.
- Some categories need discovery and ranking more than raw collection. MoMA and The Met can be scraped cleanly, but deciding what matters is editorial.
- Theatre requires multiple dates per item: previews, opening, closing, extension, and possibly Tony eligibility.
- Music albums are the least canonical before release. Public music sources are good for announcements, but not a single stable master calendar.
- Subscription sources may add value, but should not be infrastructure dependencies for version one.

## Recommended First Prototype Set

Start with eight sources that are both high-value and technically distinct:

1. TMDb Discover Movie API
2. TVmaze schedule APIs
3. Broadway.org show list
4. Playbill Broadway/Off-Broadway listings
5. The Met exhibitions page
6. MoMA exhibitions page
7. Met Opera season page
8. New York City Ballet season page

This set will quickly reveal the main normalization problems while staying close to public, automatable sources.
