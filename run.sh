#!/bin/zsh
# Hourly on the Mac (launchd com.ksofronis.somaigia-cards): site blocks datacenter IPs, so the build runs here and pushes to Pages.
set -e
export PATH=/opt/homebrew/bin:/usr/bin:/bin
cd "${0:A:h}"
git pull -q --rebase origin main
python3 build.py --max 80
python3 gallery.py
git add -A c review feed manifest.json bad_images.json
git diff --cached --quiet || { git commit -q -m "build $(date -u +%FT%TZ)"; git push -q origin main; }
