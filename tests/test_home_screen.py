"""Add to Home Screen: iOS icon, manifest, publish step, and app-safe outbound links (offline).

iOS ignores SVG favicons; it wants an opaque, square PNG apple-touch-icon (it composites any
transparency onto black and applies its own rounded mask). Standalone mode has no back button,
so outbound entry links must open outside the app shell (target=_blank).
"""

import datetime as dt
import json
import struct
from pathlib import Path

from cultural_calendar import legacy as L
from cultural_calendar.core.config import Source

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def _png_header(path: Path) -> tuple[int, int, int]:
    """(width, height, colour_type) from the IHDR chunk — no Pillow needed in CI."""
    data = path.read_bytes()[:33]
    assert data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR", f"{path.name} is not a PNG"
    width, height = struct.unpack(">II", data[16:24])
    return width, height, data[25]


def _render(monkeypatch, tmp_path) -> str:
    monkeypatch.setattr(L, "today", lambda: dt.date(2026, 10, 3))
    monkeypatch.setattr(L, "end_date", lambda: dt.date(2027, 12, 31))
    monkeypatch.setattr(L, "DB_PATH", tmp_path / "t.db")
    monkeypatch.setattr(L, "HTML_PATH", tmp_path / "page.html")
    conn = L.connect()
    src = Source(id="tmdb_movies", name="TMDb", category="film", type="json_api", url="x")
    L.upsert_item(conn, src, {
        "title": "Test Film", "category": "film", "date_start": "2026-11-06",
        "date_label": "Nov 6, 2026", "date_precision": "exact",
        "source_url": "https://example.com/film", "external_id": "t:1",
    })
    conn.commit()
    L.render_html(conn)
    return (tmp_path / "page.html").read_text()


def test_page_head_has_home_screen_tags(monkeypatch, tmp_path):
    page = _render(monkeypatch, tmp_path)
    assert '<link rel="apple-touch-icon" href="apple-touch-icon.png">' in page
    assert '<link rel="manifest" href="manifest.webmanifest">' in page
    assert '<meta name="apple-mobile-web-app-title" content="Cultural Calendar">' in page
    assert '<meta name="apple-mobile-web-app-capable" content="yes">' in page


def test_outbound_links_leave_the_app_shell(monkeypatch, tmp_path):
    page = _render(monkeypatch, tmp_path)
    assert '<a href="https://example.com/film" target="_blank" rel="noopener">' in page


def test_apple_touch_icon_is_opaque_square_180():
    width, height, colour_type = _png_header(SITE / "apple-touch-icon.png")
    assert (width, height) == (180, 180)
    assert colour_type == 2  # truecolour, no alpha channel (iOS would composite alpha onto black)


def test_manifest_icons_exist_at_declared_sizes():
    manifest = json.loads((SITE / "manifest.webmanifest").read_text())
    assert manifest["short_name"] == "Cultural Calendar" and manifest["display"] == "standalone"
    for icon in manifest["icons"]:
        w, h, _ = _png_header(SITE / icon["src"])
        assert f"{w}x{h}" == icon["sizes"]


def test_pages_workflow_publishes_the_icons():
    wf = (ROOT / ".github" / "workflows" / "weekly-refresh.yml").read_text()
    assert "cp site/*.png site/manifest.webmanifest _site/" in wf
    assert "_site/apple-touch-icon-precomposed.png" in wf
