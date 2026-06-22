#!/usr/bin/env bash
set -euo pipefail

URL_FILE="/home/opc/vpsmonitor/.tunnel-url"
LOG_FILE="/home/opc/vpsmonitor/tunnel.log"

cloudflared tunnel --url http://localhost:8080 --no-autoupdate 2>&1 | tee "$LOG_FILE" | while IFS= read -r line; do
    echo "$line"
    if [[ "$line" =~ https://([a-z0-9-]+)\.trycloudflare\.com ]]; then
        echo "${BASH_REMATCH[0]}" > "$URL_FILE"
    fi
done
