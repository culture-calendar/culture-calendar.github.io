#!/usr/bin/env python3
"""Back-compat shim. The implementation now lives in the `cultural_calendar` package.

Run `python3 toy_calendar.py [...]` or, equivalently, `python3 -m cultural_calendar [...]`.
Legacy function names are re-exported so older callers/tests keep working.
"""

from cultural_calendar.cli import main, run_imports  # noqa: F401
from cultural_calendar.legacy import *  # noqa: F401,F403

if __name__ == "__main__":
    main()
