"""After a refresh, raise (or clear) one GitHub issue when sources need a human.

Run by the weekly workflow after "Refresh the calendar". It reads this run's source results
from data/calendar.db plus each hand-/Mac-refreshed cache's `capturedAt` stamp and reports:

  * pages a parser can no longer read (a site change: fix the parser);
  * sources failing that aren't on the known-blocked lists (newly blocked, or a site change);
  * caches overdue for refresh: the Sunday Mac job (registry.MAC_REFRESHED) or the monthly
    Claude-in-Chrome session (registry.BROWSER_CAPTURED).

Sources that are merely "stale" on GitHub because GitHub is refused are NOT alerts, as long as
their cache is being kept fresh. One issue, labelled `refresh-alert`, mentions @hdfinder-tech
(so GitHub emails him); later runs comment only when the list of problems changes, and the issue
closes itself once everything is healthy.

    python tools/refresh_alert.py            # in CI (needs GH_TOKEN with issues:write)
    python tools/refresh_alert.py --dry-run  # print what it would post
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cultural_calendar import legacy as L  # noqa: E402
from cultural_calendar import registry as R  # noqa: E402

LABEL = "refresh-alert"
TITLE = "Calendar refresh needs attention"
MENTION = "@hdfinder-tech"


def latest_runs(db_path: Path) -> dict[str, tuple[str, str, str]]:
    """source_id -> (name, status, message) for each source's most recent run."""
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            """select r.source_id, r.source_name, r.status, coalesce(r.message, '')
               from source_runs r join (select source_id, max(id) id from source_runs group by source_id) m
               on m.id = r.id"""
        ).fetchall()
    return {sid: (name, status, msg) for sid, name, status, msg in rows}


def captured_at(path: Path) -> dt.date | None:
    try:
        return dt.date.fromisoformat(str(json.loads(path.read_text()).get("capturedAt"))[:10])
    except (OSError, ValueError, AttributeError, TypeError):
        return None


def find_problems(runs: dict[str, tuple[str, str, str]], today: dt.date,
                  ages: dict[str, dt.date | None]) -> dict[str, list[str]]:
    """Group what needs a human, by what to do about it. `ages` maps the Mac-refreshed and
    browser-captured source ids to their cache's capturedAt date."""
    expected_stale = set(R.MAC_REFRESHED) | set(R.BROWSER_CAPTURED)
    out: dict[str, list[str]] = {"unreadable": [], "failing": [], "mac": [], "browser": []}
    for sid, (name, status, msg) in sorted(runs.items(), key=lambda kv: kv[1][0]):
        if "nothing recognizable" in msg or "parser error" in msg:
            out["unreadable"].append(f"**{name}**: {msg}")
        elif status not in ("ok", "skipped") and sid not in expected_stale:
            out["failing"].append(f"**{name}** ({status}): {msg}")
    for group, limit, key in ((R.MAC_REFRESHED, R.MAC_REFRESH_MAX_DAYS, "mac"),
                              (R.BROWSER_CAPTURED, R.BROWSER_CAPTURE_MAX_DAYS, "browser")):
        for sid in group:
            when = ages.get(sid)
            if when is None or (today - when).days > limit:
                name = runs.get(sid, (sid, "", ""))[0]
                age = f"{(today - when).days} days ago ({when})" if when else "never"
                out[key].append(f"**{name}**: last refreshed {age}")
    return {k: v for k, v in out.items() if v}


SECTION_HEADS = {
    "unreadable": "Pages the parser can no longer read (likely a site change; the parser needs updating)",
    "failing": "Failing, and not on the known-blocked lists (newly blocked, or a site change)",
    "mac": "Overdue: the Sunday Mac refresh hasn't updated these (check "
           "`~/Library/Logs/cultural-calendar-refresh.log` on the Pennington iMac)",
    "browser": "Overdue: the monthly Claude-in-Chrome refresh (see cultural_calendar/capture/README.md)",
}


def render(problems: dict[str, list[str]], today: dt.date) -> str:
    parts = [f"Weekly refresh of {today:%B %-d, %Y}."]
    for key, lines in problems.items():
        parts.append(f"### {SECTION_HEADS[key]}\n" + "\n".join(f"- {ln}" for ln in lines))
    digest = hashlib.sha1(json.dumps(problems, sort_keys=True).encode()).hexdigest()[:12]
    return "\n\n".join(parts) + f"\n\n<!-- problems:{digest} -->"


def gh(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=False)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    today = L.today()
    runs = latest_runs(L.DB_PATH)
    ages = {sid: captured_at(p) for sid, p in {**R.MAC_REFRESHED, **R.BROWSER_CAPTURED}.items()}
    problems = find_problems(runs, today, ages)
    body = render(problems, today) if problems else ""

    if args.dry_run:
        print(body or "All sources healthy; no alert.")
        return 0

    gh("label", "create", LABEL, "--color", "b60205", "--description", "Calendar refresh needs attention", "--force")
    listed = json.loads(gh("issue", "list", "--label", LABEL, "--state", "open", "--json", "number", "--limit", "1").stdout or "[]")
    number = str(listed[0]["number"]) if listed else None

    if problems:
        if number is None:
            gh("issue", "create", "--title", TITLE, "--label", LABEL, "--body", f"{MENTION} {body}")
            print("opened alert issue")
            return 0
        view = json.loads(gh("issue", "view", number, "--json", "body,comments").stdout or "{}")
        last = (view.get("comments") or [{}])[-1].get("body") or view.get("body") or ""
        marker = body.rsplit("<!-- problems:", 1)[1]
        if marker in last:
            print(f"alert #{number} unchanged; not commenting")
        else:
            gh("issue", "comment", number, "--body", body)
            print(f"updated alert #{number}")
    elif number is not None:
        gh("issue", "comment", number, "--body", f"All sources healthy as of {today:%B %-d, %Y}. Closing.")
        gh("issue", "close", number)
        print(f"closed alert #{number}")
    else:
        print("all sources healthy; no alert")
    return 0


if __name__ == "__main__":
    sys.exit(main())
