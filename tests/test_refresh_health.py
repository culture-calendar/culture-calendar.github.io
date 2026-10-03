"""Telling broken sources from quiet ones, and alerting only on what needs a human (Oct 2026).

Background: six parsers broke silently for weeks because a page that loads but parses nothing
looked the same as a museum between shows, and both just served the old cache as "stale".
"""

import datetime as dt
import importlib.util
from pathlib import Path

from cultural_calendar import legacy as L
from cultural_calendar import registry as R
from cultural_calendar.core.config import Source

ROOT = Path(__file__).resolve().parents[1]
TODAY = dt.date(2026, 10, 3)
_SRC = Source(id="x_test", name="Test Venue", category="art", type="html", url="https://example.com")


def _row(title, start):
    return {"title": title, "category": "art", "date_start": start, "date_label": start,
            "date_precision": "exact", "source_url": "https://example.com/" + title, "external_id": title}


def _run(monkeypatch, tmp_path, parser):
    monkeypatch.setattr(L, "today", lambda: TODAY)
    monkeypatch.setattr(L, "DB_PATH", tmp_path / "t.db")
    monkeypatch.setattr(L, "save_raw", lambda *a, **k: None)
    monkeypatch.setattr(L, "fetch_valid_page", lambda *a, **k: "<html>a page</html>")
    cache = tmp_path / "cache.json"
    L.save_capture_fixture(cache, [_row("Cached Show", "2026-12-01")])
    conn = L.connect()
    L.import_with_cache(conn, _SRC, cache, parser)
    return conn.execute("select status, message from source_runs order by id desc limit 1").fetchone()


def test_quiet_page_is_ok_but_unreadable_page_is_flagged(monkeypatch, tmp_path):
    def quiet(source, text):   # recognizes two shows, both already open
        rows = [_row("Open Show", "2026-02-12"), _row("Older Show", "2026-03-28")]
        return [r for r in rows if dt.date.fromisoformat(r["date_start"]) >= L.today()]
    status, msg = _run(monkeypatch, tmp_path, quiet)
    assert status == "ok" and "page lists 2" in msg and "none upcoming yet" in msg

    status, msg = _run(monkeypatch, tmp_path, lambda source, text: [])  # recognizes nothing: site changed
    assert status == "stale" and "nothing recognizable" in msg
    assert L.today() == TODAY  # the probe restored the real today()


def _alert_module():
    spec = importlib.util.spec_from_file_location("refresh_alert", ROOT / "tools" / "refresh_alert.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_alert_flags_only_what_needs_a_human():
    alert = _alert_module()
    fresh, old = TODAY - dt.timedelta(days=3), TODAY - dt.timedelta(days=63)
    runs = {
        "va_london": ("Victoria and Albert Museum", "ok", "0 upcoming — page lists 4 current or past, none upcoming yet"),
        "summer_city": ("Summer for the City", "ok", "out of season — festival page not live (returns each spring)"),
        "lisson": ("Lisson Gallery (NY)", "stale", "1 from last-good cache — fetch blocked/invalid (stale)"),
        "alice_tully": ("Alice Tully Hall (CMS)", "stale", "30 from cache — page fetched but nothing recognizable (check parser/shape)"),
        "joyce": ("The Joyce Theater", "stale", "17 from last-good cache — fetch blocked/invalid (stale)"),
    }
    ages = {sid: fresh for sid in {**R.MAC_REFRESHED, **R.BROWSER_CAPTURED}}
    ages["moca_la"] = TODAY - dt.timedelta(days=R.MAC_REFRESH_MAX_DAYS + 5)   # Sunday job stopped
    ages["moma_exhibitions"] = old                                           # monthly session missed
    problems = alert.find_problems(runs, TODAY, ages)
    flat = {k: " ".join(v) for k, v in problems.items()}
    assert "Alice Tully" in flat["unreadable"]                 # broken parser: always an alert
    assert "Joyce" in flat["failing"]                          # stale and not known-blocked
    assert "Lisson" not in " ".join(flat.values())             # known-blocked, cache fresh: fine
    assert "Victoria" not in " ".join(flat.values()) and "Summer" not in " ".join(flat.values())
    assert "moca_la" in flat["mac"] and "moma_exhibitions" in flat["browser"]
    assert "frick" not in flat["browser"]                      # captured recently: fine


def test_summer_city_out_of_season_is_not_a_failure(monkeypatch, tmp_path):
    monkeypatch.setattr(L, "DB_PATH", tmp_path / "t.db")
    src = Source(id="summer_city", name="Summer for the City", category="music", type="html", url="https://lc/sftc")
    home = "<html><head><title>Lincoln Center</title></head><body>" + "x" * 200_000 + "</body></html>"
    monkeypatch.setattr(L, "fetch_text", lambda *a, **k: home)
    conn = L.connect()
    assert L.import_summer_city(conn, src) == 0
    assert tuple(conn.execute("select status, message from source_runs").fetchone()) == (
        "ok", "out of season — festival page not live (returns each spring)")
    # A small block page is NOT mistaken for dormancy: it goes through the normal stale path.
    monkeypatch.setattr(L, "fetch_text", lambda *a, **k: "<html><title>Just a moment...</title></html>")
    monkeypatch.setattr(L, "fetch_valid_page", lambda *a, **k: None)
    L.import_summer_city(conn, src)
    assert conn.execute("select status from source_runs order by id desc limit 1").fetchone()[0] == "stale"


def test_moca_reads_dates_from_listing_card_not_the_repeated_page_header(monkeypatch, tmp_path):
    # Every MOCA exhibition page repeats the current shows' run above its own dates.
    monkeypatch.setattr(L, "today", lambda: TODAY)
    monkeypatch.setattr(L, "save_detail", lambda *a, **k: None)
    monkeypatch.setattr(L, "upsert_detail", lambda *a, **k: None)
    detail = ('<meta property="og:title" content="Julian Charrière: Deep End">'
              "<p>On view Sept 20, 2026 – Jan 3, 2027</p><p>Nov 15, 2026 – June 6, 2027</p>")
    monkeypatch.setattr(L, "fetch_text", lambda *a, **k: detail)
    src = Source(id="moca_la", name="MOCA Los Angeles", category="art", type="html", url="https://www.moca.org/exhibitions")
    card = {"title": "MOCA Grand Avenue Julian Charrière: Deep End Nov 15, 2026 – June 6, 2027",
            "source_url": "https://www.moca.org/exhibitions/julian-charriere", "external_id": "jc"}
    kept = L.hydrate_museum_dates(None, src, [card])
    assert [(k["title"], k["date_start"]) for k in kept] == [("Julian Charrière: Deep End", "2026-11-15")]


def test_guggenheim_with_no_upcoming_section_is_quiet_not_a_crash(monkeypatch, tmp_path):
    # Oct 2026: with nothing announced, Guggenheim sends "upcoming": {"items": null}; the importer
    # crashed ("'NoneType' object is not iterable") and the page showed an error for the source.
    monkeypatch.setattr(L, "today", lambda: TODAY)
    monkeypatch.setattr(L, "DB_PATH", tmp_path / "t.db")
    monkeypatch.setattr(L, "save_raw", lambda *a, **k: None)
    page = ('{"on_view": {"items": [{"title": "Guggenheim Pop", "slug": "pop", '
            '"dates": {"start": {"day": "5", "month": "June", "year": "2026"}}}]}, '
            '"upcoming": {"items": null}}')
    monkeypatch.setattr(L, "fetch_text", lambda *a, **k: page)
    src = Source(id="guggenheim", name="Guggenheim", category="art", type="html", url="https://g/exhibitions")
    conn = L.connect()
    assert L.import_guggenheim(conn, src) == 0
    assert tuple(conn.execute("select status, message from source_runs").fetchone()) == (
        "ok", "0 upcoming — page lists 1 current or past, none upcoming yet")
