"""Source registry: maps each source id to its tactic, importer, and health range.

This replaces the original ``if source.id == ... elif ...`` dispatch in run_imports.
Sources not given a dedicated importer fall through to ``import_html_source`` (the HTML
catch-all that internally handles the museum framework, the capture fixtures, broadway
hydration, and the per-site HTML parsers).
"""

from __future__ import annotations

from . import legacy
from .core.config import Source
from .sources.base import SourcePlugin

# Sources with a dedicated importer. Everything else -> html catch-all (import_html_source).
_DEDICATED: dict[str, tuple[str, object, bool]] = {
    # id: (tactic, importer, needs_aperture)
    "tvmaze_full_schedule": ("json_api", legacy.import_tvmaze, True),
    "tmdb_movies": ("json_api", legacy.import_tmdb, False),
    "carnegie_hall": ("json_api", legacy.import_carnegie, False),
    "ibdb": ("html", legacy.import_ibdb, False),
    "nyphil_concerts": ("json_api", legacy.import_nyphil_api, False),
    "gagosian": ("embedded_json", legacy.import_gallery_nextdata, False),
    "guggenheim": ("embedded_json", legacy.import_guggenheim, False),
    "lacma": ("html", legacy.import_lacma, False),
    "va_london": ("html", legacy.import_va, False),
    "tate_modern": ("html", legacy.import_tate, False),
    "tate_britain": ("html", legacy.import_tate, False),
    "fondation_lv": ("html", legacy.import_flv, False),
    "serpentine": ("html", legacy.import_serpentine, False),
    "armory": ("html", legacy.import_armory, False),
    "pac_nyc": ("html", legacy.import_pac, False),
    "the_shed": ("html", legacy.import_the_shed, False),
    "ocula": ("capture", legacy.import_ocula, False),
    "marian_goodman": ("html", legacy.import_marian_goodman, False),
    "lisson": ("html", legacy.import_lisson, False),
    "tanya_bonakdar": ("html", legacy.import_tanya_bonakdar, False),
    "bargemusic": ("json_api", legacy.import_bargemusic, False),
    "joyce": ("html", legacy.import_joyce, False),
    "merkin": ("html", legacy.import_merkin, False),
    "alice_tully": ("html", legacy.import_alice_tully, False),
    "jalc": ("json_api", legacy.import_jalc, False),
    "abt": ("html", legacy.import_abt, False),
    "summer_city": ("html", legacy.import_summer_city, False),
}

# Tactic label for the html-catch-all sources (for docs/health/tests clarity).
_HTML_TACTIC = {
    "new_museum": "embedded_json",
    "moma_exhibitions": "capture",
    "frick": "capture",
    "npg_london": "capture",
    "grand_palais": "capture",
    "centre_pompidou": "capture",
    "mam_paris": "capture",
}

# Expected row ranges (health / silent-drift alarm). Wide enough to tolerate normal churn,
# tight enough to catch a source that breaks to 0 or balloons.
EXPECTED_ROWS: dict[str, tuple[int, int]] = {
    # Upper bounds widened for the rolling ~18-month horizon (more months of programming).
    "tmdb_movies": (15, 200), "tvmaze_full_schedule": (40, 450),
    "carnegie_hall": (20, 450), "metacritic_albums": (40, 520),
    "broadway_org": (1, 30), "playbill_broadway": (0, 30), "playbill_offbroadway": (3, 60),
    "bam_programs": (0, 12), "met_exhibitions": (1, 25), "moma_exhibitions": (0, 30),
    "whitney": (0, 30), "brooklyn_museum": (0, 25), "moca_la": (0, 20), "lacma": (0, 25),
    "pace_gallery": (0, 20), "gagosian": (0, 20), "guggenheim": (0, 20), "frick": (0, 20),
    "new_museum": (0, 20), "met_opera_2026_27": (5, 40), "nycb_seasons": (5, 50),
    "nyphil_concerts": (5, 240), "aoty_upcoming": (0, 60), "ibdb": (0, 40),
    "pac_nyc": (1, 25), "the_shed": (1, 25), "armory": (0, 30), "tate_modern": (0, 20), "tate_britain": (0, 20), "serpentine": (0, 20),
    "npg_london": (0, 20), "fondation_lv": (0, 20), "grand_palais": (0, 20),
    "centre_pompidou": (0, 20), "va_london": (0, 20), "mam_paris": (0, 20),
    "ocula": (0, 40), "marian_goodman": (0, 20), "lisson": (0, 20), "tanya_bonakdar": (0, 20),
    "bargemusic": (0, 80), "joyce": (0, 30), "merkin": (0, 160), "alice_tully": (0, 60),
    "jalc": (0, 60), "abt": (0, 40), "summer_city": (0, 150),
}


def plugin_for(source: Source) -> SourcePlugin:
    expected = EXPECTED_ROWS.get(source.id)
    if source.id in _DEDICATED:
        tactic, importer, needs_aperture = _DEDICATED[source.id]
        return SourcePlugin(source.id, tactic, importer, needs_aperture, expected)
    tactic = _HTML_TACTIC.get(source.id, "html")
    return SourcePlugin(source.id, tactic, legacy.import_html_source, False, expected)


# --- Refresh ownership (used by tools/refresh_alert.py) -------------------------------------
# On GitHub's runners these sources are expected to come back "stale": the live fetch is
# refused there, so GitHub serves the committed cache. What matters is that someone keeps that
# cache fresh, judged by its `capturedAt` stamp (bumped on every successful fetch).

# Refused by GitHub, fine from a home connection: the Pennington Mac refreshes them weekly
# (tools/mac_refresh.sh). Overdue after MAC_REFRESH_MAX_DAYS -> the Sunday job isn't running.
MAC_REFRESHED: dict[str, "Path"] = {
    "lisson": legacy.LISSON_CACHE,
    "moca_la": legacy.museum_cache_path("moca_la"),
    "brooklyn_museum": legacy.museum_cache_path("brooklyn_museum"),
    "met_exhibitions": legacy.MET_CAPTURE,
    "serpentine": legacy.SERPENTINE_CAPTURE,
}
MAC_REFRESH_MAX_DAYS = 15

# No script can fetch these at all: captured by hand in the monthly Claude-in-Chrome session
# (cultural_calendar/capture/README.md). Overdue after BROWSER_CAPTURE_MAX_DAYS.
BROWSER_CAPTURED: dict[str, "Path"] = {
    "moma_exhibitions": legacy.MOMA_CAPTURE_LINKS,
    "frick": legacy.FRICK_CAPTURE,
    "ocula": legacy.OCULA_CAPTURE,
    "armory": legacy.ARMORY_CAPTURE,
    "met_opera_2026_27": legacy.MET_OPERA_CAPTURE,
}
BROWSER_CAPTURE_MAX_DAYS = 45


def relabel_by_capture_age(conn, source: Source, count: int, today: "dt.date | None" = None) -> None:
    """Make a run's status describe the DATA, not GitHub's fetch.

    A Mac-refreshed source whose live fetch was refused here serves its saved cache and records
    "stale" — though the Mac may have refreshed it this morning. A browser-captured source always
    serves its capture, and some importers call that "ok" however old it is. So re-label by the
    capture's age: within its refresh window it's current ("ok"); past it, "stale" with the age.
    A page that was fetched but couldn't be read stays flagged — that's a real break."""
    import datetime as dt
    import json

    if source.id in BROWSER_CAPTURED:
        path, limit, how, relabel = BROWSER_CAPTURED[source.id], BROWSER_CAPTURE_MAX_DAYS, "browser capture of", ("ok", "stale")
    elif source.id in MAC_REFRESHED:
        path, limit, how, relabel = MAC_REFRESHED[source.id], MAC_REFRESH_MAX_DAYS, "refreshed from the Pennington Mac on", ("stale",)
    else:
        return
    row = conn.execute("select id, status, coalesce(message, '') from source_runs where source_id = ? "
                       "order by id desc limit 1", (source.id,)).fetchone()
    if not row or row[1] not in relabel or "nothing recognizable" in row[2] or "parser error" in row[2]:
        return
    try:
        captured = dt.date.fromisoformat(str(json.loads(path.read_text()).get("capturedAt"))[:10])
    except (OSError, ValueError, TypeError, AttributeError):
        return
    age = ((today or legacy.today()) - captured).days
    n = f"{count} {'entry' if count == 1 else 'entries'}"
    when = f"{captured:%b} {captured.day}"
    if age <= limit:
        status, message = "ok", f"{n} — {how} {when}"
    else:
        status, message = "stale", f"{n} — {how} {when}, {age} days old (due for refresh)"
    conn.execute("update source_runs set status = ?, message = ? where id = ?", (status, message, row[0]))
    conn.commit()
