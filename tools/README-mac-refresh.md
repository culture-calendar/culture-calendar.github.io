# Weekly Mac refresh

Some sources (Merkin, Brooklyn Museum, The Met, Serpentine, and others over time) refuse
GitHub's datacenter runners but serve an ordinary home connection. So the Pennington iMac
refreshes everything it can reach once a week and pushes the saved caches; GitHub then rebuilds
and publishes the page from them.

- **When:** Sundays at 6:50 PM. If the iMac is asleep, launchd runs the job at the next wake —
  the iMac already wakes itself at 6:55 PM on weekends (`pmset -g sched`). `caffeinate` keeps it
  awake until the job finishes; then normal sleep resumes. It does not run if the Mac is shut
  down or nobody is logged in.
- **Where:** its own clone in `~/.cultural-calendar/repo` (never your working copy).
- **Log:** `~/Library/Logs/cultural-calendar-refresh.log`
- **What it commits:** only `*_capture/*.json` caches, and only if tests pass before and after.

Commands (from the repo root):

```bash
tools/install_mac_refresh.sh              # install or reinstall
launchctl kickstart -k gui/$(id -u)/org.culture-calendar.mac-refresh   # run once now
tail -40 ~/Library/Logs/cultural-calendar-refresh.log                  # see what happened
tools/install_mac_refresh.sh --uninstall  # remove the job
```

The bot-walled sources that need a real browser (MoMA, Frick, Ocula, Park Avenue Armory,
Met Opera) are not covered here; they are refreshed in the monthly Claude-in-Chrome session
(`cultural_calendar/capture/README.md`).
