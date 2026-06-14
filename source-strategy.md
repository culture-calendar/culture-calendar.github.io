# Cultural Calendar: Source Strategy

## Editorial Scope

The calendar is meant to help New Yorker editors plan coverage through the end of 2026, especially profiles and longer-lead pieces around culturally significant releases, openings, premieres, exhibitions, and performances.

The geographic bias should vary by category:

- Film and television: national, with release/platform dates as the primary organizing principle.
- Theatre: New York first, especially Broadway and Off-Broadway; track major West End debut productions when they are culturally significant in their own right, not merely New York shows transferring to London.
- Art: New York first; track very high-profile London and Paris exhibitions, plus rare breakthrough events elsewhere.
- Music: New York first, Los Angeles second; ignore routine regional programming unless it has national cultural significance.
- Opera: New York first, with major U.S. and international companies included when programming is important enough for coverage planning.
- Ballet: scope narrowly to New York, especially New York City Ballet, American Ballet Theatre, Joyce Theater dance programming, BAM, and Lincoln Center.

The calendar should include both firm dates and vague planning dates such as "Fall 2026," "Q4 2026," or "TBA 2026." Vague dates are important for profiles and assignment planning even before publicists announce exact openings.

## Data Model Implications

Each item should preserve both a normalized date and a human date label:

- `date_start`
- `date_end`
- `date_precision`: exact, month, season, quarter, year, tba
- `date_label`: "Fall 2026," "opens Dec. 1, 2026," etc.
- `source_url`
- `source_name`
- `source_confidence`: high, medium, low
- `last_checked`
- `category`
- `subcategory`
- `city`
- `venue_or_platform`
- `people`: cast, directors, artists, composers, choreographers, curators, writers, producers
- `editorial_notes`
- `importance_score`
- `profile_potential_score`

For ranking, the first version should use explainable tags and scores rather than a black-box model. Useful signals include:

- New Yorker relevance
- prominence of attached people
- institution/platform/distributor prestige
- novelty: debut, premiere, revival, transfer, first major retrospective, first album in years
- scarcity: limited run, one-night event, rare U.S. appearance
- coverage potential: profile, Talk, review, critic item, Goings On listing
- date urgency

## Film Sources

Best initial sources:

- TMDb API: strong for release windows, cast/crew, production companies, platforms, popularity, and metadata enrichment.
- IMDb public/non-commercial datasets: useful for identity resolution and credits, with licensing constraints.
- The Numbers and Box Office Mojo: useful for theatrical release schedules and distributor cross-checking.
- Rotten Tomatoes and Metacritic: useful as editorial signal sources, not canonical dates.
- Studio/distributor press pages: canonical for important releases but fragmented.

Access notes:

TMDb is likely the best first API. It will require an API key but should be stable and repeatable. Public pages such as The Numbers and Box Office Mojo may require scraper care. IMDbPro can be considered later for richer industry metadata, but start with public/non-commercial IMDb data and TMDb.

## Television Sources

Best initial sources:

- TVmaze API: strong for episode schedules, premiere dates, network/streaming metadata, and daily schedules.
- TMDb TV API: useful for broader discovery, popularity, cast/crew, and platform metadata.
- Network and streamer press sites: canonical but fragmented.
- Metacritic TV and Rotten Tomatoes TV: useful for editorial signal and critical attention.

Access notes:

TVmaze is probably the cleanest first source for scheduling. Streamers are inconsistent about future dates, so press pages and entertainment-trade reporting will matter for long-lead items.

## Theatre Sources

Best initial sources:

- Broadway.org: official Broadway League show listings.
- IBDB: canonical production and people metadata for Broadway.
- Playbill: strong for Broadway and Off-Broadway listings, announcements, cast changes, openings, closings, and extensions.
- BroadwayWorld: broad coverage and useful discovery.
- TheaterMania and New York Theatre Guide: useful for Off-Broadway and Off-Off-Broadway discovery.
- Official institutional calendars: Public Theater, NYTW, BAM, Lincoln Center Theater, Roundabout, MTC, Second Stage, Atlantic, Signature, Playwrights Horizons, MCC, Vineyard, Soho Rep, St. Ann's Warehouse, Classic Stage, Irish Rep, TFANA, La MaMa, Ars Nova.
- London Theatre, Official London Theatre, WhatsOnStage, and venue/company pages: useful for major West End debuts.

Special fields:

- `previews_start`
- `opening_night`
- `closing_date`
- `limited_run`
- `extension_announced`
- `transfer_origin`
- `world_premiere`
- `broadway_debut`
- `notable_cast`
- `playwright`
- `director`
- `composer`
- `choreographer`
- `producer`
- `tony_eligibility_season`

Access notes:

Theatre data will require a mix of official pages and editorial/trade sources. Opening night, previews, and closing dates should be stored separately. Public scraping should be enough for an initial version.

## Art and Museum Sources

Best New York sources:

- The Met
- MoMA
- Whitney Museum
- Guggenheim
- Brooklyn Museum
- New Museum
- Frick Collection
- Jewish Museum
- Studio Museum in Harlem
- ICP
- Dia
- Queens Museum
- PS1

High-priority non-New-York sources:

- Tate
- National Gallery, London
- Royal Academy
- Serpentine
- Centre Pompidou
- Louvre
- Musee d'Orsay
- Fondation Louis Vuitton
- Prado
- Reina Sofia
- Venice Biennale
- Art Basel
- Frieze

Discovery/signal sources:

- Artforum
- e-flux
- The Art Newspaper
- Ocula
- See Saw
- museum press pages

Access notes:

Official museum exhibition pages should be canonical for dates. Many are scrapeable but will need site-specific adapters. Aggregators are useful for discovery and importance signals but should not override official dates.

## Music Sources

Best album sources:

- MusicBrainz API: useful for release metadata and artist identity.
- Metacritic upcoming albums: useful for anticipated major releases.
- AllMusic new releases: useful as a broad release feed.
- Album of the Year: useful for discovery and public anticipation.
- Pitchfork, Stereogum, Consequence, NPR Music, Resident Advisor, The Quietus, BrooklynVegan: useful for announcement discovery and editorial priority.
- Label and artist press pages: canonical for important releases.

Best programming/event sources:

- Ticketmaster Discovery API: broad coverage for large events.
- Lincoln Center
- Carnegie Hall
- BAM
- Park Avenue Armory
- The Shed
- Brooklyn Academy of Music
- LA Phil
- Walt Disney Concert Hall
- Hollywood Bowl
- major NYC and LA venues/promoters

Access notes:

Forward-looking album data is messy. MusicBrainz is useful but may miss anticipated unreleased albums until they are publicly entered. Editorial music sites and label press pages will be essential. NYC and LA should be prioritized for live programming.

## Opera Sources

Best sources:

- Met Opera official season pages
- Lincoln Center
- Carnegie Hall for concert opera and vocal programming
- Operabase, if public access is sufficient or subscription access proves worthwhile
- Lyric Opera of Chicago
- San Francisco Opera
- LA Opera
- Houston Grand Opera
- Santa Fe Opera
- Royal Opera
- Paris Opera
- Salzburg Festival
- Glyndebourne
- Bayreuth

Access notes:

Met Opera is the first target because it is central, structured enough, and editorially relevant. Operabase may become useful for breadth, but public access should be tested before relying on subscriptions or session cookies.

## Ballet Sources

Best sources:

- New York City Ballet
- American Ballet Theatre
- Joyce Theater for dance programming
- Lincoln Center
- Brooklyn Academy of Music

Access notes:

Ballet calendars are usually available on official company pages, but productions, casting, choreographers, and premieres may appear across separate season, repertory, and press-release pages. New works, major revivals, farewells, and galas should be emphasized. Non-New-York ballet should be treated as exceptional rather than routine.

## Access Policy

Start public-first:

1. APIs and public structured feeds.
2. Official public pages with stable scraping.
3. Public editorial/trade sources for discovery and importance.
4. Subscription/session-cookie access only after a source has proven uniquely valuable and no public substitute works.

Potential subscription sources:

- IMDbPro
- Variety
- The Ankler
- Operabase, if useful and available

Avoid building the first version around cookie-dependent sources. They are brittle and may create terms-of-service or maintenance problems.

## First Build Recommendation

The first technical milestone should be a source registry plus a small ingestion prototype:

1. Create a source registry table with category, source URL, source type, access method, fields available, reliability, update cadence, scraping difficulty, and notes.
2. Build initial importers for TMDb, TVmaze, The Met, MoMA, Broadway.org or Playbill, Met Opera, NYCB or ABT, and one music source.
3. Store raw source snapshots as well as normalized calendar items.
4. Display items in a sortable table grouped by month and category.
5. Add filters for exact/vague dates, New York relevance, profile potential, and high-importance items.

The first version should optimize for editorial scanning, not completeness.
