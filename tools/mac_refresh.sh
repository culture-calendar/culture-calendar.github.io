#!/bin/zsh
# Weekly refresh of the Cultural Calendar from the Pennington Mac's residential IP.
#
# Several sites refuse GitHub's datacenter runners but serve this Mac normally, so launchd
# (org.culture-calendar.mac-refresh, Sundays 6:50 PM — the iMac's own 6:55 PM weekend wake
# runs it if it was asleep) calls this from its OWN clone, ~/.cultural-calendar/repo. It never
# touches a working copy, so it can't commit anyone's half-finished edits, and it stays clear
# of macOS's privacy wall around ~/Documents.
#
# Steps: sync to origin, test, refresh every source, test again, commit only the *_capture
# caches, push, ask GitHub to redeploy. TMDb is skipped (no key here); GitHub's own weekly run
# covers it. Log: ~/Library/Logs/cultural-calendar-refresh.log
#
# Install / test / remove: see tools/README-mac-refresh.md.

main() {
  set -u
  export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
  local repo="$HOME/.cultural-calendar/repo"
  echo "=== $(date '+%Y-%m-%d %H:%M:%S %Z') weekly Mac refresh ==="
  cd "$repo" || { echo "FAIL: no clone at $repo"; return 1; }

  # The clone holds no local work, so mirror origin exactly (no merges to go wrong).
  git fetch -q origin && git reset -q --hard origin/main || { echo "FAIL: could not sync with GitHub"; return 1; }
  echo "at $(git rev-parse --short HEAD)"

  python3 -m pytest -q 2>&1 | tail -1
  [[ ${pipestatus[1]} -eq 0 ]] || { echo "FAIL: tests failing before refresh; aborting"; return 1; }

  python3 -m cultural_calendar 2>&1 | grep -E ": [0-9]+ \[" || true

  python3 -m pytest -q 2>&1 | tail -1
  [[ ${pipestatus[1]} -eq 0 ]] || { echo "FAIL: tests failing after refresh; not committing"; return 1; }

  git add -- '*_capture/*.json'
  if git diff --cached --quiet; then
    echo "no cache changes; nothing to publish"
    return 0
  fi
  git diff --cached --stat | tail -1
  git commit -q -m "Weekly Mac refresh $(date +%Y-%m-%d): caches from the Pennington Mac" \
    -m "Automated by tools/mac_refresh.sh (launchd). Refreshes sources GitHub's runners are refused."

  if ! git push -q origin HEAD:main; then   # someone pushed meanwhile: replay on top once
    git fetch -q origin && git rebase -q origin/main && git push -q origin HEAD:main \
      || { echo "FAIL: push rejected"; return 1; }
  fi
  echo "pushed $(git rev-parse --short HEAD)"
  gh workflow run weekly-refresh.yml --ref main && echo "deploy requested"
}

# Defined as a function so zsh parses the whole script before running it: the git reset above
# can rewrite this very file mid-run.
main "$@"
