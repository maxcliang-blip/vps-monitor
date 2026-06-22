#!/usr/bin/env bash
set -euo pipefail

URL_FILE="/home/opc/vpsmonitor/.tunnel-url"
INDEX_FILE="/home/opc/vpsmonitor/docs/index.html"
REPO_DIR="/home/opc/vpsmonitor"
LAST_URL=""

while true; do
  if [[ -f "$URL_FILE" ]]; then
    NEW_URL=$(cat "$URL_FILE")
    if [[ -n "$NEW_URL" && "$NEW_URL" != "$LAST_URL" ]]; then
      LAST_URL="$NEW_URL"
      echo "[auto-update] Tunnel URL changed to: $NEW_URL"

      # Update the API_HOST in docs/index.html
      sed -i "s|const API_HOST = .*|const API_HOST = '$NEW_URL';  // Cloudflare Tunnel URL|" "$INDEX_FILE"

      # Commit and push
      cd "$REPO_DIR"
      git add "$INDEX_FILE" 2>/dev/null
      git -c user.name="vps-monitor" -c user.email="vps-monitor@localhost" \
        commit -m "Auto-update tunnel URL" 2>/dev/null || true
      git push origin main 2>/dev/null || true
      echo "[auto-update] Pushed to GitHub"
    fi
  fi
  sleep 30
done
