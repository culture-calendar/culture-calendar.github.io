"""Ocula gallery-capture parser tests (pure, offline)."""

import datetime as dt

from cultural_calendar import legacy as L


def test_dates_range_year_at_end():
    assert L.parse_ocula_dates("X White Cube 11 June–14 August 2026 New York")[:2] == ("2026-06-11", "2026-08-14")


def test_dates_cross_year():
    s, e, label, prec = L.parse_ocula_dates("Doris Salcedo White Cube 12 November 2026–23 January 2027 New York")
    assert (s, e) == ("2026-11-12", "2027-01-23")
    assert prec == "exact"


def test_dates_from_form():
    assert L.parse_ocula_dates("CATHERINE OPIE Lehmann Maupin From 4 March 2026 New York")[:2] == ("2026-03-04", None)


def test_exhibitions_allowlist_ny_future(monkeypatch):
    monkeypatch.setattr(L, "today", lambda: dt.date(2026, 6, 18))
    monkeypatch.setattr(L, "end_date", lambda: dt.date(2027, 12, 31))
    rows = [
        {"gallery_slug": "white-cube", "href": "/art-galleries/white-cube/exhibitions/doris-salcedo/",
         "text": "Doris Salcedo White Cube 12 November 2026–23 January 2027 New York"},
        {"gallery_slug": "gagosian-gallery", "href": "/art-galleries/gagosian-gallery/exhibitions/brice-marden/",
         "text": "Brice Marden I Am Plane Image Gagosian 10 September–17 October 2026 West 21st Street, New York"},
        {"gallery_slug": "lehmann-maupin", "href": "/my-ocula/exhibition-previews/lehmann-maupin/catherine-opie-1/",
         "text": "CATHERINE OPIE Lehmann Maupin From 4 March 2026 501 West 24th Street, New York"},
        {"gallery_slug": "white-cube", "href": "/my-ocula/exhibition-previews/white-cube/theaster-gates/",
         "text": "THEASTER GATES And Other paintings White Cube 6 March–4 April 2026 Paris"},
    ]
    items = L.parse_ocula_exhibitions(rows)
    titles = [i["title"] for i in items]
    assert "Doris Salcedo" in titles
    assert all(i["category"] == "art" and i["city"] == "New York" for i in items)
    assert not any("Brice Marden" in t for t in titles)   # Gagosian excluded (scraped directly)
    assert not any("CATHERINE OPIE" in t.upper() for t in titles)  # past opening
    assert not any("THEASTER" in t.upper() for t in titles)  # Paris, not NY
    salcedo = next(i for i in items if i["title"] == "Doris Salcedo")
    assert salcedo["venue_or_platform"] == "White Cube"
    assert salcedo["date_start"] == "2026-11-12"
