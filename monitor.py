#!/usr/bin/env python3
"""VPS Monitor with Geometry Dash theme"""

import http.server
import json
import os
import socketserver
import subprocess
import time
import urllib.parse

import psutil

PORT = 8080

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VPS Monitor - Geometry Dash</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  background: linear-gradient(180deg, #1a0a3e 0%, #0d0520 100%);
  color: #fff;
  font-family: 'Press Start 2P', monospace;
  min-height: 100vh;
  overflow-x: hidden;
  position: relative;
}

/* Stars */
.stars {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  pointer-events: none;
  z-index: 0;
}
.star {
  position: absolute;
  width: 3px; height: 3px;
  background: #fff;
  border-radius: 50%;
  animation: twinkle var(--d) ease-in-out infinite alternate;
}
@keyframes twinkle {
  0% { opacity: 0.2; }
  100% { opacity: 1; }
}

/* Ground */
.ground {
  position: fixed;
  bottom: 0; left: 0;
  width: 100%; height: 48px;
  z-index: 2;
  display: flex;
}
.ground-block {
  width: 48px; height: 48px;
  flex-shrink: 0;
}
.ground-block:nth-child(odd) { background: #2d1b69; }
.ground-block:nth-child(even) { background: #3d2599; }

/* Header */
.header {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 30px 20px 20px;
}
.header h1 {
  font-size: 28px;
  color: #ffd700;
  text-shadow: 3px 3px 0 #ff6b00, -1px -1px 0 #ff6b00;
  letter-spacing: 2px;
}
.header .subtitle {
  font-size: 10px;
  color: #8a7cc0;
  margin-top: 10px;
}

/* Cube icon */
.cube-row {
  display: flex;
  justify-content: center;
  gap: 6px;
  margin: 15px 0;
}
.cube {
  width: 20px; height: 20px;
  background: #4a90d9;
  transform: rotate(45deg);
  animation: bounce 1.5s ease-in-out infinite;
}
.cube:nth-child(2) { animation-delay: 0.2s; background: #ffd700; }
.cube:nth-child(3) { animation-delay: 0.4s; background: #ff6b35; }
.cube:nth-child(4) { animation-delay: 0.6s; background: #4a90d9; }
.cube:nth-child(5) { animation-delay: 0.8s; background: #ffd700; }
@keyframes bounce {
  0%, 100% { transform: rotate(45deg) translateY(0); }
  50% { transform: rotate(45deg) translateY(-10px); }
}

/* Main grid */
.grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 18px;
  max-width: 1100px;
  margin: 20px auto 80px;
  padding: 0 18px;
}

/* Card */
.card {
  background: linear-gradient(135deg, rgba(74,144,217,0.15) 0%, rgba(255,215,0,0.08) 100%);
  border: 2px solid rgba(255,215,0,0.3);
  border-radius: 8px;
  padding: 18px;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(4px);
}
.card::before {
  content: '';
  position: absolute;
  top: 0; left: 0;
  right: 0; height: 4px;
  background: linear-gradient(90deg, #4a90d9, #ffd700, #ff6b35);
}
.card-title {
  font-size: 11px;
  color: #ffd700;
  margin-bottom: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.card-title .icon {
  display: inline-block;
  width: 16px; height: 16px;
  background: #ffd700;
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
}

/* Stat rows */
.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.stat-row:last-child { border-bottom: none; }
.stat-label {
  font-size: 9px;
  color: #8a7cc0;
}
.stat-value {
  font-size: 11px;
  color: #fff;
}

/* Progress bar wrapper */
.bar-wrapper {
  margin: 8px 0;
}
.bar-label {
  font-size: 9px;
  color: #8a7cc0;
  margin-bottom: 5px;
  display: flex;
  justify-content: space-between;
}
.bar-track {
  width: 100%;
  height: 18px;
  background: rgba(0,0,0,0.4);
  border: 2px solid rgba(255,215,0,0.2);
  border-radius: 4px;
  position: relative;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  transition: width 0.8s ease;
  position: relative;
}
.bar-fill::after {
  content: '';
  position: absolute;
  top: 0; left: 0;
  right: 0; bottom: 0;
  background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.15) 50%, transparent 100%);
  animation: shimmer 2s infinite;
}
@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
.bar-fill.low { background: linear-gradient(90deg, #4a90d9, #6ab0f9); }
.bar-fill.medium { background: linear-gradient(90deg, #ffd700, #ffb700); }
.bar-fill.high { background: linear-gradient(90deg, #ff6b35, #ff4444); }

/* Alert flash */
@keyframes alert-pulse {
  0%, 100% { box-shadow: 0 0 5px rgba(255,68,68,0.5); }
  50% { box-shadow: 0 0 25px rgba(255,68,68,0.9); }
}
.card.alert {
  border-color: #ff4444;
  animation: alert-pulse 1s ease-in-out infinite;
}
.card.alert::before {
  background: linear-gradient(90deg, #ff4444, #ff6b35, #ff4444);
}

/* Spike decorations */
.spike {
  width: 0; height: 0;
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
  border-bottom: 18px solid rgba(255,107,53,0.3);
  position: absolute;
  bottom: 48px;
  z-index: 1;
}

/* Server info bar */
.server-info {
  position: relative;
  z-index: 1;
  text-align: center;
  font-size: 8px;
  color: #5a4a8a;
  padding: 8px;
  margin-bottom: 4px;
}

/* Process list */
.process-list {
  margin-top: 10px;
  max-height: 180px;
  overflow-y: auto;
}
.process-list::-webkit-scrollbar { width: 4px; }
.process-list::-webkit-scrollbar-track { background: transparent; }
.process-list::-webkit-scrollbar-thumb { background: rgba(255,215,0,0.3); border-radius: 2px; }
.process-item {
  display: flex;
  justify-content: space-between;
  font-size: 8px;
  padding: 4px 0;
  color: #aaa;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}
.process-item .pname { color: #ccc; max-width: 160px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.process-item .pcpu { color: #4a90d9; }
.process-item .pmem { color: #ffd700; }

/* Network table */
.net-table {
  width: 100%;
  font-size: 8px;
  border-collapse: collapse;
  margin-top: 6px;
}
.net-table th {
  color: #ffd700;
  text-align: left;
  padding: 4px 2px;
  border-bottom: 1px solid rgba(255,215,0,0.2);
}
.net-table td {
  color: #aaa;
  padding: 4px 2px;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}

@media (max-width: 600px) {
  .header h1 { font-size: 18px; }
  .grid { grid-template-columns: 1fr; padding: 0 10px; }
}
</style>
</head>
<body>

<div class="stars" id="stars"></div>
<div class="spike" style="left:5%"></div>
<div class="spike" style="left:15%"></div>
<div class="spike" style="left:30%"></div>
<div class="spike" style="left:50%"></div>
<div class="spike" style="left:65%"></div>
<div class="spike" style="left:80%"></div>
<div class="spike" style="left:92%"></div>

<div class="header">
  <div class="cube-row">
    <div class="cube"></div><div class="cube"></div><div class="cube"></div>
    <div class="cube"></div><div class="cube"></div>
  </div>
  <h1>VPS MONITOR</h1>
  <div class="subtitle">GEOMETRY DASH EDITION</div>
</div>

<div class="server-info" id="serverInfo">Loading...</div>

<div class="grid" id="grid"></div>

<div class="ground" id="ground"></div>

<script>
const API_HOST = '';
const COLORS = { low: '#4a90d9', medium: '#ffd700', high: '#ff6b35' };

function clamp(v, min, max) { return Math.min(max, Math.max(min, v)); }

function pctClass(pct) {
  if (pct < 50) return 'low';
  if (pct < 80) return 'medium';
  return 'high';
}

function pctColor(pct) {
  if (pct < 50) return COLORS.low;
  if (pct < 80) return COLORS.medium;
  return COLORS.high;
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return (bytes / Math.pow(1024, i)).toFixed(1) + ' ' + units[i];
}

function formatBits(bits) {
  if (bits === 0) return '0 b';
  const units = ['b', 'Kb', 'Mb', 'Gb', 'Tb'];
  const i = Math.floor(Math.log(bits) / Math.log(1000));
  return (bits / Math.pow(1000, i)).toFixed(1) + ' ' + units[i];
}

function barHTML(label, used, total, pct, suffix) {
  const cls = pctClass(pct);
  return `<div class="bar-wrapper">
    <div class="bar-label">
      <span>${label}</span>
      <span>${used}${suffix || ''} / ${total}${suffix || ''}</span>
    </div>
    <div class="bar-track">
      <div class="bar-fill ${cls}" style="width:${pct}%"></div>
    </div>
    <div class="bar-label" style="justify-content:flex-end">
      <span style="color:${pctColor(pct)}">${pct.toFixed(1)}%</span>
    </div>
  </div>`;
}

function buildCards(d) {
  const g = document.getElementById('grid');
  g.innerHTML = '';

  function alertClass(pct) {
    return pct > 90 ? 'card alert' : 'card';
  }

  // CPU
  g.innerHTML += `<div class="${alertClass(d.cpu)}">
    <div class="card-title"><span class="icon"></span> CPU</div>
    ${barHTML('Usage', d.cpu.toFixed(1), 100, d.cpu, '%')}
    <div class="stat-row"><span class="stat-label">Frequency</span><span class="stat-value">${d.cpu_freq || 'N/A'}</span></div>
    <div class="stat-row"><span class="stat-label">Load Average</span><span class="stat-value">${d.load_avg}</span></div>
    <div class="stat-row"><span class="stat-label">Processes</span><span class="stat-value">${d.processes}</span></div>
    <div class="stat-row"><span class="stat-label">Zombie</span><span class="stat-value" style="color:${d.zombies > 0 ? '#ff4444' : '#4a90d9'}">${d.zombies}</span></div>
  </div>`;

  // Memory
  g.innerHTML += `<div class="${alertClass(d.mem_pct)}">
    <div class="card-title"><span class="icon"></span> Memory</div>
    ${barHTML('RAM', formatBytes(d.mem_used), formatBytes(d.mem_total), d.mem_pct)}
    <div class="stat-row"><span class="stat-label">Available</span><span class="stat-value">${formatBytes(d.mem_avail)}</span></div>
    ${d.swap_total > 0 ? barHTML('Swap', formatBytes(d.swap_used), formatBytes(d.swap_total), d.swap_pct) : ''}
  </div>`;

  // Storage
  let diskHTML = `<div class="card">
    <div class="card-title"><span class="icon"></span> Storage</div>`;
  for (const disk of d.disks) {
    diskHTML += barHTML(disk.mount, formatBytes(disk.used), formatBytes(disk.total), disk.pct);
  }
  diskHTML += `</div>`;
  g.innerHTML += diskHTML;

  // Inodes
  if (d.inodes && d.inodes.length) {
    let inodeHTML = `<div class="card">
      <div class="card-title"><span class="icon"></span> Inodes</div>`;
    for (const n of d.inodes) {
      inodeHTML += `<div class="stat-row"><span class="stat-label">${n.mount}</span><span class="stat-value" style="color:${n.pct > 80 ? '#ff6b35' : '#4a90d9'}">${n.pct}% (${n.used}/${n.total})</span></div>`;
    }
    inodeHTML += `</div>`;
    g.innerHTML += inodeHTML;
  }

  // Network
  g.innerHTML += `<div class="card">
    <div class="card-title"><span class="icon"></span> Network</div>
    <table class="net-table">
      <tr><th>Interface</th><th>RX</th><th>TX</th></tr>
      ${d.network.map(n => `<tr><td>${n.name}</td><td>${n.rx}<br><span style="color:#4a90d9;font-size:7px">${n.rx_speed}</span></td><td>${n.tx}<br><span style="color:#ff6b35;font-size:7px">${n.tx_speed}</span></td></tr>`).join('')}
    </table>
  </div>`;

  // Disk I/O
  if (d.disk_io && d.disk_io.length) {
    let ioHTML = `<div class="card">
      <div class="card-title"><span class="icon"></span> Disk I/O</div>
      <table class="net-table">
        <tr><th>Disk</th><th>Read</th><th>Write</th></tr>`;
    for (const io of d.disk_io) {
      ioHTML += `<tr><td>${io.name}</td><td>${io.read}<br><span style="color:#4a90d9;font-size:7px">${io.read_speed}</span></td><td>${io.written}<br><span style="color:#ff6b35;font-size:7px">${io.write_speed}</span></td></tr>`;
    }
    ioHTML += `</table></div>`;
    g.innerHTML += ioHTML;
  }

  // Connections & Security
  g.innerHTML += `<div class="card">
    <div class="card-title"><span class="icon"></span> Connections & Security</div>
    <div class="stat-row"><span class="stat-label">TCP Connections</span><span class="stat-value">${d.tcp_connections}</span></div>
    <div class="stat-row"><span class="stat-label">Failed SSH (24h)</span><span class="stat-value" style="color:${d.failed_ssh > 0 ? '#ff6b35' : '#4a90d9'}">${d.failed_ssh}</span></div>
    <div class="stat-row"><span class="stat-label">Ping (google.com)</span><span class="stat-value">${d.ping_ms || 'N/A'}</span></div>
    ${d.pkg_updates !== null ? `<div class="stat-row"><span class="stat-label">Package Updates</span><span class="stat-value" style="color:${d.pkg_updates > 0 ? '#ffd700' : '#4a90d9'}">${d.pkg_updates}</span></div>` : ''}
  </div>`;

  // System
  g.innerHTML += `<div class="card">
    <div class="card-title"><span class="icon"></span> System</div>
    <div class="stat-row"><span class="stat-label">Uptime</span><span class="stat-value">${d.uptime}</span></div>
    <div class="stat-row"><span class="stat-label">Hostname</span><span class="stat-value">${d.hostname}</span></div>
    <div class="stat-row"><span class="stat-label">OS</span><span class="stat-value">${d.os}</span></div>
    <div class="stat-row"><span class="stat-label">Kernel</span><span class="stat-value">${d.kernel}</span></div>
    <div class="stat-row"><span class="stat-label">Users</span><span class="stat-value">${d.users}</span></div>
  </div>`;

  // Service Uptimes
  if (d.svc_uptime && Object.keys(d.svc_uptime).length) {
    let svcHTML = `<div class="card">
      <div class="card-title"><span class="icon"></span> Monitor Services</div>`;
    for (const [name, val] of Object.entries(d.svc_uptime)) {
      svcHTML += `<div class="stat-row"><span class="stat-label">${name}</span><span class="stat-value" style="font-size:8px;color:#aaa">${val}</span></div>`;
    }
    svcHTML += `</div>`;
    g.innerHTML += svcHTML;
  }

  // Top processes by CPU
  if (d.top_cpu && d.top_cpu.length) {
    let procsHTML = `<div class="card">
      <div class="card-title"><span class="icon"></span> Top CPU</div>
      <div class="process-list">`;
    for (const p of d.top_cpu) {
      procsHTML += `<div class="process-item">
        <span class="pname">${p.name}</span>
        <span class="pcpu">${p.cpu}%</span>
        <span class="pmem">${p.mem}%</span>
      </div>`;
    }
    procsHTML += `</div></div>`;
    g.innerHTML += procsHTML;
  }

  // Top processes by memory
  if (d.top_mem && d.top_mem.length) {
    let memHTML = `<div class="card">
      <div class="card-title"><span class="icon"></span> Top Memory</div>
      <div class="process-list">`;
    for (const p of d.top_mem) {
      memHTML += `<div class="process-item">
        <span class="pname">${p.name}</span>
        <span class="pcpu">${p.cpu}%</span>
        <span class="pmem">${p.mem}%</span>
      </div>`;
    }
    memHTML += `</div></div>`;
    g.innerHTML += memHTML;
  }

  // Running services
  if (d.services && d.services.length) {
    let svcHTML = `<div class="card">
      <div class="card-title"><span class="icon"></span> Running Services</div>
      <div class="process-list">`;
    for (const s of d.services) {
      svcHTML += `<div class="process-item">
        <span class="pname">${s}</span>
      </div>`;
    }
    svcHTML += `</div></div>`;
    g.innerHTML += svcHTML;
  }
}

// Generate stars
(function initStars() {
  const c = document.getElementById('stars');
  for (let i = 0; i < 80; i++) {
    const s = document.createElement('div');
    s.className = 'star';
    s.style.left = Math.random() * 100 + '%';
    s.style.top = Math.random() * 70 + '%';
    s.style.setProperty('--d', (1 + Math.random() * 2) + 's');
    s.style.width = s.style.height = (1 + Math.random() * 2) + 'px';
    c.appendChild(s);
  }
})();

// Ground blocks
(function initGround() {
  const g = document.getElementById('ground');
  const n = Math.ceil(window.innerWidth / 48) + 2;
  for (let i = 0; i < n; i++) {
    const b = document.createElement('div');
    b.className = 'ground-block';
    g.appendChild(b);
  }
})();

async function fetchData() {
  try {
    const r = await fetch(API_HOST + '/api/data');
    const d = await r.json();
    document.getElementById('serverInfo').textContent =
      d.hostname + '  |  ' + d.uptime + '  |  ' + d.os;
    buildCards(d);
  } catch(e) {
    document.getElementById('serverInfo').textContent = 'Error fetching data';
  }
}

fetchData();
setInterval(fetchData, 3000);
</script>
</body>
</html>
"""


class DataHandler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == '/api/data':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            data = collect_data()
            self.wfile.write(json.dumps(data).encode())
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML.encode())


_io_prev = {}
_net_prev = {}
_cpu_cache = {'pct': 0.0}

def _cpu_monitor():
    while True:
        _cpu_cache['pct'] = psutil.cpu_percent(interval=1)
        time.sleep(2)

def _start_cpu_monitor():
    import threading
    t = threading.Thread(target=_cpu_monitor, daemon=True)
    t.start()
    # First measurement is instant
    _cpu_cache['pct'] = psutil.cpu_percent(interval=0)

def get_cpu_freq():
    try:
        freqs = []
        for i in range(os.cpu_count() or 1):
            path = f'/sys/devices/system/cpu/cpu{i}/cpufreq/scaling_cur_freq'
            if os.path.exists(path):
                with open(path) as f:
                    freqs.append(int(f.read().strip()) // 1000)
        if freqs:
            avg = sum(freqs) / len(freqs)
            return f'{avg:.0f} MHz'
    except Exception:
        pass
    return 'N/A'

def get_ping_latency():
    try:
        out = subprocess.run(
            ['ping', '-c', '1', '-W', '3', 'google.com'],
            capture_output=True, text=True, timeout=5
        )
        for line in out.stdout.split('\n'):
            if 'time=' in line:
                ms = line.split('time=')[1].split()[0]
                return ms
    except Exception:
        pass
    return None

def get_tcp_connections():
    try:
        count = 0
        with open('/proc/net/tcp') as f:
            for i, line in enumerate(f):
                if i > 0:
                    count += 1
        with open('/proc/net/tcp6') as f:
            for i, line in enumerate(f):
                if i > 0:
                    count += 1
        return count
    except Exception:
        return 0

def get_failed_logins():
    try:
        out = subprocess.check_output(
            ['journalctl', '-u', 'sshd', '--since', '24 hours ago', '--no-pager', '--no-legend'],
            stderr=subprocess.DEVNULL, timeout=5, text=True
        )
        count = out.count('Failed password')
        return count if count > 0 else 0
    except Exception:
        return 0

_pkg_cache = {'count': None, 'done': False}

def get_package_updates():
    if _pkg_cache['done']:
        return _pkg_cache['count']
    _pkg_cache['done'] = True
    try:
        out = subprocess.run(
            ['dnf', 'check-update', '--quiet'],
            capture_output=True, text=True, timeout=2
        )
        _pkg_cache['count'] = len([l for l in out.stdout.strip().split('\n') if l]) if out.returncode == 100 else 0
    except Exception:
        _pkg_cache['count'] = None
    return _pkg_cache['count']

def get_inode_usage():
    try:
        inodes = []
        for part in psutil.disk_partitions():
            try:
                st = os.statvfs(part.mountpoint)
                total = st.f_files
                free = st.f_ffree
                used = total - free
                if total > 0:
                    pct = round(used / total * 100, 1)
                    inodes.append({
                        'mount': part.mountpoint,
                        'used': used,
                        'total': total,
                        'pct': pct,
                    })
            except Exception:
                pass
        return inodes
    except Exception:
        return []

def get_service_uptimes():
    try:
        result = {}
        for svc in ['vps-monitor', 'vps-monitor-tunnel', 'vps-monitor-url-updater']:
            out = subprocess.run(
                ['systemctl', 'show', '-p', 'ActiveEnterTimestamp', svc],
                capture_output=True, text=True, timeout=3
            )
            line = out.stdout.strip()
            if '=' in line:
                val = line.split('=', 1)[1]
                result[svc] = val if val != '' else 'N/A'
            else:
                result[svc] = 'N/A'
        return result
    except Exception:
        return {}

def collect_data():
    # CPU
    cpu_pct = _cpu_cache['pct']
    load = os.getloadavg()
    load_str = f'{load[0]:.2f} {load[1]:.2f} {load[2]:.2f}'
    cpu_freq = get_cpu_freq()

    # Zombie processes
    zombie_count = 0
    try:
        for p in psutil.process_iter(['status']):
            try:
                if p.info['status'] == 'zombie':
                    zombie_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception:
        pass

    # Memory
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    # Disks
    disks = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks.append({
                'mount': part.mountpoint,
                'total': usage.total,
                'used': usage.used,
                'pct': usage.percent,
            })
        except PermissionError:
            pass

    # Inode usage
    inodes = get_inode_usage()

    # Disk I/O
    global _io_prev
    io_now = psutil.disk_io_counters(perdisk=True)
    io_data = []
    for name in ('sda', 'nvme0n1', 'vda', 'xda'):
        if name in io_now:
            c = io_now[name]
            prev = _io_prev.get(name)
            if prev:
                dt = time.time() - prev['time']
                read_speed = (c.read_bytes - prev['read_bytes']) / dt if dt > 0 else 0
                write_speed = (c.write_bytes - prev['write_bytes']) / dt if dt > 0 else 0
            else:
                read_speed = write_speed = 0
            _io_prev[name] = {'read_bytes': c.read_bytes, 'write_bytes': c.write_bytes, 'time': time.time()}
            io_data.append({
                'name': name,
                'read': format_bytes(c.read_bytes),
                'written': format_bytes(c.write_bytes),
                'read_speed': format_bytes(read_speed) + '/s',
                'write_speed': format_bytes(write_speed) + '/s',
            })
            break

    # Network
    global _net_prev
    net = psutil.net_io_counters(pernic=True)
    net_data = []
    for name, counters in sorted(net.items()):
        if name == 'lo':
            continue
        prev = _net_prev.get(name)
        if prev:
            dt = time.time() - prev['time']
            rx_speed = (counters.bytes_recv - prev['rx']) / dt if dt > 0 else 0
            tx_speed = (counters.bytes_sent - prev['tx']) / dt if dt > 0 else 0
        else:
            rx_speed = tx_speed = 0
        _net_prev[name] = {'rx': counters.bytes_recv, 'tx': counters.bytes_sent, 'time': time.time()}
        net_data.append({
            'name': name,
            'rx': format_bytes(counters.bytes_recv) + ' RX',
            'tx': format_bytes(counters.bytes_sent) + ' TX',
            'rx_speed': format_bytes(rx_speed) + '/s',
            'tx_speed': format_bytes(tx_speed) + '/s',
        })
        if len(net_data) >= 4:
            break

    # TCP connections
    tcp_connections = get_tcp_connections()

    # Uptime
    uptime_sec = time.time() - psutil.boot_time()
    days = int(uptime_sec // 86400)
    hours = int((uptime_sec % 86400) // 3600)
    minutes = int((uptime_sec % 3600) // 60)
    if days > 0:
        uptime_str = f'{days}d {hours}h {minutes}m'
    else:
        uptime_str = f'{hours}h {minutes}m'

    # Top processes by CPU
    top_cpu = []
    for p in sorted(psutil.process_iter(['name', 'cpu_percent', 'memory_percent']),
                     key=lambda p: p.info['cpu_percent'] or 0, reverse=True)[:10]:
        try:
            if p.info['cpu_percent'] is not None:
                top_cpu.append({
                    'name': (p.info['name'] or '?')[:20],
                    'cpu': round(p.info['cpu_percent'] or 0, 1),
                    'mem': round(p.info['memory_percent'] or 0, 1),
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Top processes by memory
    top_mem = []
    for p in sorted(psutil.process_iter(['name', 'cpu_percent', 'memory_percent']),
                     key=lambda p: p.info['memory_percent'] or 0, reverse=True)[:10]:
        try:
            if p.info['memory_percent'] is not None:
                top_mem.append({
                    'name': (p.info['name'] or '?')[:20],
                    'cpu': round(p.info['cpu_percent'] or 0, 1),
                    'mem': round(p.info['memory_percent'] or 0, 1),
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Running services
    services = []
    try:
        out = subprocess.check_output(
            ['systemctl', 'list-units', '--type=service', '--state=running', '--no-pager', '--no-legend'],
            stderr=subprocess.DEVNULL, timeout=5, text=True
        )
        for line in out.strip().split('\n')[:15]:
            parts = line.split()
            if len(parts) >= 1:
                name = parts[0].replace('.service', '')[:25]
                services.append(name)
    except Exception:
        pass

    # Failed SSH logins (24h)
    failed_ssh = get_failed_logins()

    # Package updates
    pkg_updates = get_package_updates()

    # Ping latency
    ping_ms = get_ping_latency()

    # Service uptimes
    svc_uptime = get_service_uptimes()

    return {
        'cpu': cpu_pct,
        'cpu_freq': cpu_freq,
        'load_avg': load_str,
        'processes': len(psutil.pids()),
        'zombies': zombie_count,
        'mem_total': mem.total,
        'mem_used': mem.used,
        'mem_avail': mem.available,
        'mem_pct': mem.percent,
        'swap_total': swap.total,
        'swap_used': swap.used,
        'swap_pct': swap.percent,
        'disks': disks,
        'inodes': inodes,
        'disk_io': io_data,
        'network': net_data,
        'tcp_connections': tcp_connections,
        'uptime': uptime_str,
        'hostname': os.uname().nodename,
        'os': f'{os.uname().sysname} {os.uname().release}',
        'kernel': os.uname().version.split()[0],
        'users': len(psutil.users()),
        'top_cpu': top_cpu,
        'top_mem': top_mem,
        'services': services,
        'failed_ssh': failed_ssh,
        'pkg_updates': pkg_updates,
        'ping_ms': ping_ms,
        'svc_uptime': svc_uptime,
    }


def format_bytes(bytes_val):
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if bytes_val < 1024:
            return f'{bytes_val:.1f} {unit}'
        bytes_val /= 1024
    return f'{bytes_val:.1f} PB'


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == '__main__':
    print(f'  ___ ___ ___   ___ ___ ___ ___ ___ ___ ___ ')
    print(f' | _ \ _ \ _ \ / __| __/ __|_ _/ __| __| _ \\')
    print(f' |  _/  _/   / \__ \ _| (__ | |\__ \ _||   /')
    print(f' |_| |_| |_|_\\ |___/___\___|___|___/___|_|_\\')
    print(f' ===========================================')
    print(f'  VPS Monitor - Geometry Dash Edition')
    print(f'  Listening on http://0.0.0.0:{PORT}')
    print(f'  Press Ctrl+C to stop')
    print(f' ===========================================')
    _start_cpu_monitor()
    server = ThreadedHTTPServer(('0.0.0.0', PORT), DataHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down...')
        server.shutdown()
