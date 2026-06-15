"""Date-parsing engine tests (pure, deterministic)."""

import datetime as dt

from cultural_calendar import legacy as L


def test_parse_us_date():
    assert L.parse_us_date("Oct 15, 2026") == dt.date(2026, 10, 15)
    assert L.parse_us_date("October 15, 2026") == dt.date(2026, 10, 15)
    assert L.parse_us_date("not a date") is None


def test_extract_exhibition_window_year_at_end_of_range():
    # Start has no year; year comes from the end of the range.
    start, label = L.extract_exhibition_window("Apr 30–Oct 19, 2026")
    assert start == dt.date(2026, 4, 30)
    assert "Apr 30" in label


def test_extract_exhibition_window_full_range_and_through():
    start, _ = L.extract_exhibition_window("March 6, 2026–July 12, 2026")
    assert start == dt.date(2026, 3, 6)
    # A "Through ..." (closing-only) signal yields no opening date.
    assert L.extract_exhibition_window("Through January 4, 2026")[0] is None


def test_extract_exhibition_window_season():
    start, label = L.extract_exhibition_window("Opening Fall 2026")
    assert start is None and "Fall 2026" in label


def test_met_opera_season_year_context():
    # 2026-27 season: Sep-Dec -> 2026, Jan-Aug -> 2027.
    assert L.met_opera_opening_date("Sep 22 - Oct 20") == dt.date(2026, 9, 22)
    assert L.met_opera_opening_date("Feb 3 - Mar 1") == dt.date(2027, 2, 3)


def test_pac_opening_date(monkeypatch):
    # PAC's date-range element comes in several shapes; the opening is the first month/day,
    # with the trailing year governing a run. Horizon/already-running filtering is the caller's.
    monkeypatch.setattr(L, "today", lambda: dt.date(2026, 6, 15))
    assert L.extract_pac_date("Sep 13, 2026")[0] == dt.date(2026, 9, 13)
    assert L.extract_pac_date("Jun 28—Jul 26, 2026")[0] == dt.date(2026, 6, 28)
    assert L.extract_pac_date("Nov 20, 2026—Jan 3, 2027")[0] == dt.date(2026, 11, 20)
    assert L.extract_pac_date("June 20 at 7pm")[0] == dt.date(2026, 6, 20)
    assert L.extract_pac_date("Begins July 11, 11:00am—1:00pm")[0] == dt.date(2026, 7, 11)
    # A run that opened before today resolves to its (past) opening, so the caller drops it
    # as already-running rather than treating the range's end as a new opening.
    assert L.extract_pac_date("Jun 12—Jul 19, 2026")[0] == dt.date(2026, 6, 12)
    assert L.extract_pac_date("Tickets on sale soon")[0] is None


def test_metacritic_date_variants():
    assert L.parse_metacritic_date("12 June 2026")[0] == "2026-06-12"
    assert L.parse_metacritic_date("Dec 2026")[2] == "month"
    assert L.parse_metacritic_date("2026")[2] == "year"
    assert L.parse_metacritic_date("TBA")[2] == "year"
