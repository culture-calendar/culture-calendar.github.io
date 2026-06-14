# Cultural Calendar: Venue and Institution Watchlist

This is the first operational watchlist for Broadway/Off-Broadway, music, and visual art. It is intentionally broad enough for discovery, then can be narrowed by source reliability and editorial yield.

## Current Decisions

- Prototype priority: balanced across film/TV, theatre, art, music, opera, and ballet.
- TV/music aperture: wide at first, to collect maybe-relevant items before tuning filters.
- Museum access: try public pages, embedded data, and public endpoints first; use browser-based capture when a public page is visible but script access is blocked.
- Ballet: New York only unless an exceptional non-New-York event breaks through.

## Museum Access Recommendation

The most effective path is a two-step strategy:

1. First inspect the public page for embedded JSON, API calls, feeds, or static data that can be fetched directly. This is more stable, cheaper, and easier to schedule.
2. If the public page is visible in a normal browser but blocks simple script access, use browser-based capture to save rendered HTML or network responses, then parse locally.

This is especially relevant because the toy prototype could see museum pages through web inspection, but direct script access hit HTTP 429 for The Met and HTTP 403 for MoMA. That suggests access is possible, but the collection method needs to be more careful.

## Broadway

Broadway should be handled comprehensively rather than selectively. The canonical procedure is to ingest Broadway.org and Playbill/IBDB, then treat all Broadway theatres as in scope.

Core Broadway sources:

- Broadway.org
- Playbill Broadway and Upcoming Broadway
- IBDB
- BroadwayWorld
- New York Theatre Guide

Broadway theatres to include:

- Al Hirschfeld Theatre
- Ambassador Theatre
- August Wilson Theatre
- Belasco Theatre
- Bernard B. Jacobs Theatre
- Booth Theatre
- Broadhurst Theatre
- Broadway Theatre
- Circle in the Square Theatre
- Ethel Barrymore Theatre
- Eugene O'Neill Theatre
- Gerald Schoenfeld Theatre
- Gershwin Theatre
- Hayes Theater
- Hudson Theatre
- Imperial Theatre
- James Earl Jones Theatre
- John Golden Theatre
- Lena Horne Theatre
- Longacre Theatre
- Lunt-Fontanne Theatre
- Lyceum Theatre
- Lyric Theatre
- Majestic Theatre
- Marquis Theatre
- Minskoff Theatre
- Music Box Theatre
- Nederlander Theatre
- Neil Simon Theatre
- New Amsterdam Theatre
- Palace Theatre
- Richard Rodgers Theatre
- Samuel J. Friedman Theatre
- Shubert Theatre
- Stephen Sondheim Theatre
- St. James Theatre
- Studio 54
- Todd Haimes Theatre
- Vivian Beaumont Theater
- Walter Kerr Theatre
- Winter Garden Theatre

## Off-Broadway and New York Theatre

Core institutions to scrape directly:

- The Public Theater
- New York Theatre Workshop
- Playwrights Horizons
- Atlantic Theater Company
- Signature Theatre
- Lincoln Center Theater
- Manhattan Theatre Club
- Roundabout Theatre Company
- Second Stage Theater
- MCC Theater
- Vineyard Theatre
- Soho Rep
- Ars Nova
- St. Ann's Warehouse
- BAM
- Classic Stage Company
- Theatre for a New Audience
- Irish Repertory Theatre
- La MaMa
- New York City Center
- The Shed

Secondary but important:

- Rattlestick Theater / Terrence McNally Theater
- HERE Arts Center
- The Flea
- The Tank
- Clubbed Thumb
- Target Margin Theater
- Abrons Arts Center
- Bushwick Starr
- National Black Theatre
- WP Theater
- Ma-Yi Theater Company
- Mint Theater Company
- Primary Stages
- Keen Company
- Transport Group
- Red Bull Theater
- Elevator Repair Service
- Ensemble Studio Theatre
- 59E59 Theaters
- Theater for the New City
- Dixon Place
- Mabou Mines
- New Georges
- Bedlam
- New Ohio Theatre / archive-following successor programming

Commercial/venue-specific Off-Broadway spaces worth monitoring:

- Lucille Lortel Theatre
- Minetta Lane Theatre
- Daryl Roth Theatre
- New World Stages
- Westside Theatre
- Orpheum Theatre
- Stage 42
- Theater 555
- Studio Seaview
- Theatre Row
- Astor Place Theatre

Theatre signal sources:

- New York Times theatre reviews
- New Yorker theatre listings/reviews
- Vulture theatre reviews
- New York Magazine
- Time Out New York
- TheaterMania
- Playbill news
- BroadwayWorld
- Deadline theatre coverage
- Variety theatre coverage
- Outer Critics Circle nominations
- Drama Desk nominations
- Lucille Lortel Awards nominations
- Obie Awards

## Music: New York

Classical, opera-adjacent, jazz, and institutional programming:

- Carnegie Hall
- Lincoln Center
- David Geffen Hall / New York Philharmonic
- Alice Tully Hall
- Mostly Mozart / Lincoln Center summer programming
- Met Opera
- Park Avenue Armory
- BAM
- The Shed
- National Sawdust
- Kaufman Music Center / Merkin Hall
- 92NY
- Roulette
- The Kitchen
- Issue Project Room
- Le Poisson Rouge
- Village Vanguard
- Blue Note
- Jazz at Lincoln Center
- Smoke Jazz Club
- Birdland

Popular, indie, experimental, electronic, and large-format venues:

- Bowery Ballroom
- Mercury Lounge
- Music Hall of Williamsburg
- Brooklyn Steel
- Webster Hall
- Terminal 5
- Racket NYC
- Irving Plaza
- Warsaw
- Brooklyn Paramount
- Kings Theatre
- Beacon Theatre
- Radio City Music Hall
- Madison Square Garden
- Barclays Center
- Forest Hills Stadium
- SummerStage / Central Park
- Prospect Park Bandshell / BRIC Celebrate Brooklyn
- Knockdown Center
- Basement
- Brooklyn Storehouse
- Elsewhere
- Brooklyn Bowl
- Public Records
- Pioneer Works
- Baby's All Right
- Market Hotel
- Sultan Room
- Bowery Electric
- Arlene's Grocery
- Rockwood Music Hall
- Joe's Pub
- Nublu
- Nowadays
- Elsewhere Zone One / Hall
- Under the K Bridge Park
- Randall's Island festival programming

New York music signal sources:

- New Yorker Goings On About Town
- New York Times music reviews
- Pitchfork news/reviews
- BrooklynVegan
- Stereogum
- Resident Advisor
- NPR Music
- Bandcamp Daily
- Songkick/Bandsintown for artist-date discovery
- Ticketmaster Discovery API
- AXS
- Dice

## Music: Los Angeles

Core venues and institutions:

- Hollywood Bowl
- Walt Disney Concert Hall / LA Phil
- The Greek Theatre
- The Wiltern
- Hollywood Palladium
- Fonda Theatre
- The Bellwether
- Teragram Ballroom
- El Rey Theatre
- The Regent Theater
- Lodge Room
- Troubadour
- Whisky a Go Go
- Roxy Theatre
- The Echo / Echoplex
- Zebulon
- Moroccan Lounge
- Gold-Diggers
- Hollywood Forever Cemetery
- Kia Forum
- SoFi Stadium
- Intuit Dome
- Crypto.com Arena
- Shrine Auditorium
- Orpheum Theatre
- Ace Hotel Theatre / successor programming
- REDCAT
- Skirball Cultural Center
- Ford Amphitheatre
- Getty music programming

Los Angeles signal sources:

- Los Angeles Times music reviews
- LA Phil calendar
- LAist
- KCRW
- DoLA
- Resident Advisor
- Pitchfork
- Stereogum
- Ticketmaster Discovery API
- AXS
- Dice

## Art: New York

Core museums and institutions:

- The Metropolitan Museum of Art
- MoMA
- MoMA PS1
- Whitney Museum of American Art
- Solomon R. Guggenheim Museum
- New Museum
- Brooklyn Museum
- The Frick Collection
- Studio Museum in Harlem
- Jewish Museum
- Museum of the City of New York
- International Center of Photography
- Dia Beacon / Dia Chelsea
- Queens Museum
- Bronx Museum
- El Museo del Barrio
- Noguchi Museum
- SculptureCenter
- Cooper Hewitt
- Morgan Library & Museum
- Neue Galerie
- Asia Society
- Japan Society
- Grey Art Museum
- Swiss Institute
- Artists Space
- The Drawing Center
- Center for Italian Modern Art
- Leslie-Lohman Museum of Art
- National Museum of the American Indian

Gallery and art-world signal sources:

- Artforum
- The Art Newspaper
- e-flux
- Ocula
- See Saw
- Hyperallergic
- ARTnews
- Frieze
- New York Times art reviews
- New Yorker art listings/reviews
- GalleriesNow
- gallery press pages for David Zwirner, Gagosian, Hauser & Wirth, Pace, Marian Goodman, Gladstone, Greene Naftali, Matthew Marks, Petzel, Paula Cooper, Lisson, Lehmann Maupin, Karma, Jack Shainman, Kasmin, James Cohan, Alexander Gray, and Salon 94.

## Art: London and Paris Breakthrough Watch

London:

- Tate Modern
- Tate Britain
- National Gallery
- Royal Academy
- Serpentine
- Hayward Gallery
- Whitechapel Gallery
- Barbican Art Gallery
- V&A
- British Museum

Paris:

- Louvre
- Musee d'Orsay
- Centre Pompidou
- Fondation Louis Vuitton
- Palais de Tokyo
- Bourse de Commerce / Pinault Collection
- Jeu de Paume
- Musee Picasso
- Musee Rodin

These should be monthly sweeps with a high-profile filter, not equal-weight daily sources.

## Notes for Automation

- Broadway can be exhaustive because the universe is small and canonical.
- Off-Broadway should be institution-led, not every venue with a stage.
- Music should combine venue calendars, ticketing APIs, and signal sources; venue calendars alone will be too noisy.
- Art should prefer official exhibition pages for dates and signal sources for importance.
- For all categories, keep raw snapshots and parse confidence because the source pages are heterogeneous.
