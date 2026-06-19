# Capture tier — refresh procedure (no Playwright)

Most sources refresh unattended (HTTP + `requests`, including the JSON APIs for TMDb, TVMaze,
Carnegie/Algolia, and **NY Phil**). A few art sources cannot be fetched by any script — their
data is server-rendered behind bot protection that 403s `requests`/`curl`, so they're
refreshed by hand through a real browser (Claude-in-Chrome):

| Source | Why it needs a real browser | Fixture |
|--------|-----------------------------|---------|
| MoMA   | Akamai-style bot check serves a contentless shell / 403 to non-browser clients; data is in the page HTML, no API. | `moma_capture/moma-exhibition-links.json` |
| Frick  | Yottaa returns HTTP 418 / blank to automated Chromium (headless and headful). | `frick_capture/frick-exhibitions.json` |
| Ocula  | Cloudflare-walls scripts (curl/requests 403); a real browser passes. Aggregates major-gallery NY shows + fairs. | `ocula_capture/ocula-ny.json` |

We tried headless Playwright; it worked only for MoMA and not Frick, for a heavy dependency.
Since the cadence is seasonal, these two are refreshed by hand through **Claude-in-Chrome**
(a real, trusted browser session). The importer then parses the fixtures as before.

## How to refresh (run inside the connected browser)

### MoMA — `https://www.moma.org/calendar/exhibitions`
Run this in the page via the Chrome `javascript_tool`, then write the result to
`moma_capture/moma-exhibition-links.json` as `{capturedAt, url, exhibitionLinks:[{text,href}]}`.
Build `href` from the id (the DOM returns raw URLs blocked by the MCP):

```js
(() => {
  const seen = new Set(), out = [];
  for (const a of document.querySelectorAll('a[href*="/calendar/exhibitions/"]')) {
    const m = (a.getAttribute('href')||'').match(/\/calendar\/exhibitions\/(\d+)/);
    if (!m || seen.has(m[1])) continue; seen.add(m[1]);
    let card = a; for (let i=0;i<4;i++){ card = card.parentElement || card; if (card.textContent.length>40) break; }
    out.push({ id:m[1], text:a.textContent.replace(/\s+/g,' ').trim(),
               cardText:card.textContent.replace(/\s+/g,' ').trim().slice(0,160) });
  }
  return out;            // reconstruct href = `https://www.moma.org/calendar/exhibitions/${id}`
})();
```

### Frick — `https://www.frick.org/exhibitions`
Get the page text (`get_page_text`), read the entries under the **UPCOMING** heading
(title + "Month D, YYYY to Month D, YYYY"), and write them to
`frick_capture/frick-exhibitions.json` as `{capturedAt, source, note, exhibitions:[{title,start,label}]}`.
`parse_frick_capture` keeps only future openings within the horizon, so out-of-horizon 2027
entries can be listed safely.

### Ocula — major NY galleries + fairs
Two pages, both in the connected browser:
- Exhibitions: `https://ocula.com/cities/usa/new-york-art-galleries/exhibitions/?gallery-type=gallery&date=upcoming`
- Fairs: `https://ocula.com/art-fairs/`

For each, run the snippet below and write the rows to `ocula_capture/ocula-ny.json` under
`exhibitions` / `fairs` as raw `{href|slug, gallery_slug, text}`. The importer
(`parse_ocula_exhibitions` / `parse_ocula_fairs`) does all parsing — allowlist
(`OCULA_MAJOR_GALLERIES`, which excludes Gagosian/Pace since we scrape those directly),
New-York filter, future-only, and date parsing — so the fixture is just the raw capture.

```js
[...document.querySelectorAll('a[href*="/art-galleries/"][href*="/exhibitions/"], a[href*="/exhibition-previews/"]')]
  .map(a => { const h=a.getAttribute('href')||''; const m=h.match(/\/(?:art-galleries|exhibition-previews)\/([^/]+)\//);
    let c=a; for(let i=0;i<7;i++){ if(!c.parentElement)break; c=c.parentElement; if(/\d{1,2}\s+[A-Za-z]+.*20\d{2}/.test(c.textContent))break; }
    return m ? {href:h, gallery_slug:m[1], text:c.textContent.replace(/\s+/g,' ').trim().slice(0,200)} : null; })
  .filter(Boolean);
```

**Discipline:** an empty/blocked capture must never overwrite a good fixture — if the page
didn't render, leave the existing JSON in place.
