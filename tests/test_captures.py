"""Capture-fixture + NY Phil API parser tests (date monkeypatched so they're deterministic)."""

import datetime as dt
import json
from pathlib import Path

from cultural_calendar import legacy as L
from cultural_calendar.core.config import Source

FIXTURES = Path(__file__).parent / "fixtures"


def _src(sid, category):
    return Source(id=sid, name=sid, category=category, type="html", url="x")


def test_frick_capture_future_only(monkeypatch):
    monkeypatch.setattr(L, "today", lambda: dt.date(2026, 6, 1))
    items = L.parse_frick_capture(_src("frick", "art"))
    titles = [i["title"] for i in items]
    assert any("Siena" in t for t in titles)
    assert any("Kent Monkman" in t for t in titles)
    assert all(i["category"] == "art" for i in items)
    # 2027 opening is held out of the 2026 horizon
    assert not any("Susanne de Court" in t for t in titles)


def test_nyphil_api_parse(monkeypatch):
    """NY Phil is now a JSON API source: filter to NYC + horizon, parse run ranges."""
    monkeypatch.setattr(L, "today", lambda: dt.date(2026, 6, 1))
    events = json.loads((FIXTURES / "nyphil_events.json").read_text())
    items = L.parse_nyphil_events(events)
    titles = [i["title"] for i in items]
    # NYC single + two NYC ranges; Vail dropped (NYC-only), 2027 dropped (horizon),
    # ShowInCalendar=false dropped.
    assert len(items) == 3
    assert not any("Vail" in t for t in titles)
    assert not any("Young People" in t for t in titles)
    assert all(i["category"] == "music" for i in items)
    # HTML entities are unescaped in titles.
    assert any("Prokofiev’s Fifth" in t for t in titles)
    # A run range yields a date_end and keeps the human label.
    rng = next(i for i in items if i["date_label"] == "Sep 16–Sep 19")
    assert rng["date_end"] == "2026-09-19"
    # A range crossing a month boundary still resolves the end date.
    cross = next(i for i in items if i["title"].startswith("Rouvali"))
    assert cross["date_end"] == "2026-12-01"
