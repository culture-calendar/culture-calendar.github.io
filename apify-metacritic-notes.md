# Apify Metacritic Scraper Notes

Source checked: https://apify.com/automation-lab/metacritic-scraper

## Why It Matters

Metacritic should be part of the Cultural Calendar source set. It is useful less as a canonical release calendar and more as an editorial-signal layer for movies, TV, and albums: critical attention, Metascore, "Must See" flags, genre, ratings, descriptions, and normalized Metacritic URLs.

The Apify actor is worth testing because it claims to use Metacritic's backend JSON API rather than rendered-page scraping. That would be more stable than trying to parse Metacritic HTML directly.

## Extracted Fields

The actor advertises these fields:

- `metacriticId`
- `title`
- `type`
- `metascore`
- `rating`
- `releaseDate`
- `year`
- `genres`
- `platforms`
- `description`
- `mustPlay`
- `mustSee`
- `imageUrl`
- `url`
- `scrapedAt`

## Inputs

The key inputs are:

- `searchQueries`: list of search terms
- `contentType`: `all`, `game`, `movie`, or `tv`
- `maxResultsPerSearch`
- `maxRequestRetries`

## Pricing / Access

The page lists pay-per-event pricing:

- small actor start fee
- per-result fee

This means it is suitable for small validation runs, but we should avoid broad uncontrolled keyword sweeps.

## Limitations

- It is search-based, not a release-calendar endpoint.
- Search results are returned by relevance, not release date or score.
- User scores, review counts, and individual reviews are not included.
- It does not scrape individual movie/show detail pages.
- It is community-maintained, so reliability should be verified before making it a core dependency.
- It requires an Apify token if we automate it.

## Proposed Test

Run a small validation against controlled query sets:

- Movies: `2026 movies`, `upcoming movies`, plus titles discovered from TMDb.
- TV: `2026 tv`, `Netflix 2026`, `HBO 2026`, plus titles discovered from TVmaze.
- Albums, if supported directly by Metacritic pages rather than this actor: test separately, because the actor page specifically emphasizes games, movies, and TV.

For our system, the strongest use is probably enrichment:

1. Discover titles from TMDb and TVmaze.
2. Search Metacritic/Apify by title.
3. Attach Metascore, release date, genre, and "must see" flags.
4. Use those fields in editorial ranking after release or near release.

## Recommendation

Add Metacritic to the registry now. Treat Apify as a pragmatic adapter to test, not as the primary source of future release dates.
