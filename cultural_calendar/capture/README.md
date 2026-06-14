# Capture tier — refresh procedure (no Playwright)

Most sources refresh unattended (HTTP + `requests`, including the JSON APIs for TMDb, TVMaze,
Carnegie/Algolia, and **NY Phil**). Two art sources cannot be fetched by any script — their
data is server-rendered behind bot protection that 403s `requests`/`curl` **and** blocks
automated browsers (Playwright headless *and* headful both fail):

| Source | Why it needs a real browser | Fixture |
|--------|-----------------------------|---------|
| MoMA   | Akamai-style bot check serves a contentless shell / 403 to non-browser clients; data is in the page HTML, no API. | `moma_capture/moma-exhibition-links.json` |
| Frick  | Yottaa returns HTTP 418 / blank to automated Chromium (headless and headful). | `frick_capture/frick-exhibitions.json` |

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

**Discipline:** an empty/blocked capture must never overwrite a good fixture — if the page
didn't render, leave the existing JSON in place.
