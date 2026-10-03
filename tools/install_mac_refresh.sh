#!/bin/zsh
# Install (or reinstall) the weekly Mac refresh: a private clone in ~/.cultural-calendar/repo
# and a launchd agent that runs tools/mac_refresh.sh on Sundays at 6:50 PM.
# Safe to re-run. Remove with:  tools/install_mac_refresh.sh --uninstall
set -eu
LABEL="org.culture-calendar.mac-refresh"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
BASE="$HOME/.cultural-calendar"
REPO="$BASE/repo"
LOG="$HOME/Library/Logs/cultural-calendar-refresh.log"
GH="$(command -v gh)"

if [[ "${1:-}" == "--uninstall" ]]; then
  launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
  rm -f "$PLIST"
  echo "Removed the launchd job. The clone in $BASE is left in place; delete it by hand if you like."
  exit 0
fi

mkdir -p "$BASE" "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
if [[ ! -d "$REPO/.git" ]]; then
  git clone -q https://github.com/culture-calendar/culture-calendar.github.io.git "$REPO"
fi
# Push with the gh login stored in the keychain (works unattended while you're logged in).
git -C "$REPO" config credential.helper "!$GH auth git-credential"
git -C "$REPO" config user.name "$(git config --global user.name)"
git -C "$REPO" config user.email "$(git config --global user.email)"

cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/caffeinate</string><string>-is</string>
    <string>/bin/zsh</string><string>$REPO/tools/mac_refresh.sh</string>
  </array>
  <!-- Sunday 18:50. If the Mac is asleep then, launchd runs it at the next wake (the iMac's
       own repeating 6:55 PM weekend wake). caffeinate holds off sleep until the job ends. -->
  <key>StartCalendarInterval</key>
  <dict><key>Weekday</key><integer>0</integer><key>Hour</key><integer>18</integer><key>Minute</key><integer>50</integer></dict>
  <key>StandardOutPath</key><string>$LOG</string>
  <key>StandardErrorPath</key><string>$LOG</string>
</dict>
</plist>
PL

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "Installed $LABEL (Sundays 6:50 PM). Log: $LOG"
echo "Run it once now:  launchctl kickstart -k gui/$(id -u)/$LABEL"
