# VPS Monitor — AGENTS.md

## Architecture

Single-file Python HTTP server (`monitor.py`) serving a Geometry Dash-themed monitoring dashboard.

**Stack:**
- Python 3 + stdlib `http.server`, `psutil` for system stats
- No framework, no build step, no dependencies beyond `psutil`

**Two frontend copies:**
- `monitor.py` embeds HTML as a raw string — served when hitting the VPS directly on port 8080
- `docs/index.html` — standalone copy for GitHub Pages, has configurable `API_HOST`

## Services (systemd, all auto-start on boot)

| Service | File | What it does |
|---|---|---|
| `vps-monitor` | `/etc/systemd/system/vps-monitor.service` | Python backend on port 8080 |
| `vps-monitor-tunnel` | `/etc/systemd/system/vps-monitor-tunnel.service` | Cloudflare quick tunnel → HTTPS URL |
| `vps-monitor-url-updater` | `/etc/systemd/system/vps-monitor-url-updater.service` | Monitors `.tunnel-url`, pushes URL changes to GitHub |

## Commands

```bash
sudo systemctl restart vps-monitor        # restart backend
sudo systemctl restart vps-monitor-tunnel  # restart tunnel (new URL)
sudo systemctl restart vps-monitor-url-updater
sudo journalctl -u vps-monitor -f         # tail logs
```

## Important gotchas

- **Tunnel URL is ephemeral** — quick tunnels generate a random `*.trycloudflare.com` URL on every restart. The auto-updater syncs the new URL to `docs/index.html` and pushes to GitHub every 30s.
- **Both HTML copies must be kept in sync** — `docs/index.html` and the embedded HTML in `monitor.py` (the `HTML = r"""..."""` block at line 15). When adding new cards/metrics, edit both.
- **CORS preflight** — `do_OPTIONS` handler is required in the Python server for cross-origin requests from GitHub Pages. Without it, browsers block the fetch.
- **API path** — the frontend fetches from `/api/data`. The Python server serves everything else as HTML.
- **SELinux context** — scripts under `/home` need `chcon -t bin_t` before systemd can execute them (exit code 203).
- **The `.tunnel-url` file and `tunnel.log` are gitignored** — they're ephemeral artifacts.
- **No README** — this is the only instruction file.

## Key URLs

- GitHub Pages: `https://maxcliang-blip.github.io/vps-monitor/`
- Direct VPS: `http://129.80.7.65:8080`
