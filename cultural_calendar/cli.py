"""Command-line entrypoint: run the importers via the registry, then dedupe + render.

Usage:
    python -m cultural_calendar [--source ID ...] [--reset] [--aperture wide|conservative]
"""

from __future__ import annotations

import argparse
import os

from . import legacy
from .core.config import DB_PATH, HTML_PATH, load_sources
from .registry import plugin_for


def run_imports(selected: set[str] | None = None, aperture: str = "wide") -> None:
    conn = legacy.connect()
    warnings: list[str] = []
    for source in load_sources():
        if selected and source.id not in selected:
            continue
        plugin = plugin_for(source)
        try:
            if source.requires_env and not os.environ.get(source.requires_env):
                legacy.record_run(conn, source, "skipped", f"missing {source.requires_env}")
                print(f"{source.name}: 0 (skipped)")
                continue
            conn.execute("delete from items where source_id = ?", (source.id,))
            conn.commit()
            count = plugin.run(conn, source, aperture)
            print(f"{source.name}: {count} [{plugin.tactic}]")
            warning = plugin.health(count)
            if warning:
                warnings.append(warning)
        except Exception as exc:  # keep going; one bad source shouldn't sink the run
            legacy.record_run(conn, source, "error", str(exc))
            print(f"{source.name}: ERROR {exc}")
    conn.commit()
    legacy.dedupe_theatre(conn)
    legacy.render_html(conn)
    print(f"Wrote {HTML_PATH}")
    print(f"Wrote {DB_PATH}")
    if warnings:
        print("\nHealth warnings (possible scraper drift):")
        for w in warnings:
            print(f"  ! {w}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="cultural_calendar")
    parser.add_argument("--source", action="append", help="Run only this source id; can be repeated.")
    parser.add_argument("--reset", action="store_true", help="Clear prior runs and items before importing.")
    parser.add_argument("--aperture", choices=["wide", "conservative"], default="wide", help="TV filtering aperture.")
    args = parser.parse_args()
    if args.reset and DB_PATH.exists():
        DB_PATH.unlink()
    run_imports(set(args.source) if args.source else None, args.aperture)


if __name__ == "__main__":
    main()
