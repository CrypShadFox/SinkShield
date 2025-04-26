# SinkShield

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)  ![Python Version](https://img.shields.io/badge/python-3.10%2B-green)

A **DNS Sinkhole & Blocklist Manager** with auto-updating feeds, proxying for allowed queries, and a polished Flask Web UI. Perfect for home labs, SOC learning, or lightweight network protection.

---

## 🚀 Features

- **Automatic Blocklist Fetching**  
  Pulls curated domain lists (e.g. from Firebog) on a schedule  
- **Sinkhole & Proxy**  
  Returns `0.0.0.0` for blocked domains; forwards allowed queries to your upstream DNS  
- **SQLite Logging**  
  Records each query with timestamp, client IP, domain, and action (`ALLOW`/`BLOCK`)  
- **Flask Dashboard**  
  - Live statistics (total/blocked/allowed)  
  - Recent queries table  
  - Blocklist preview  
- **Configurable** via `config.yaml`

---

## 📦 Prerequisites

- **Python 3.10+**  
- `pip`  
- Optional: a Linux/WSL environment for binding to low ports (53)

---

## 🛠️ Installation

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/SinkShield.git
cd SinkShield

# 2. Create & activate a virtual environment
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows PowerShell

# 3. Install dependencies
pip install -r requirements.txt
```

---
## Configuration
Copy & edit `config.yaml` to suit your environment:

```yaml
database:
  path: "sinkhole.db"

dns:
  listen_ip: "0.0.0.0"           # IP to bind
  port:  5353                    # Use 53 in prod (requires root)
  timeout: 5                     # Upstream DNS timeout (seconds)
  upstream_resolver: "8.8.8.8"   # Your preferred DNS

blocklist:
  urls:
    - "https://v.firebog.net/hosts/AdguardDNS.txt"
    - "https://v.firebog.net/hosts/Prigent-Ads.txt"
    - "https://gitlab.com/quidsup/notrack-blocklists/raw/master/notrack-blocklist.txt"
  update_interval_hours: 24

webui:
  host: "127.0.0.1"
  port: 5000
```
## Usage

- Initialize the database

```bash
python src/database.py
```

-  Start the DNS Sinkhole
```bash
python src/server.py
```

-  Launch the Web UI
```bash
python src/webui.py
```
- Test with dig
```bash
# Blocked domain → should return 0.0.0.0
dig @127.0.0.1 -p 5353 doubleclick.net A +short

# Allowed domain → real A record
dig @127.0.0.1 -p 5353 google.com A +short
```

## Things I might add later

- Pagination, filtering & search in the Web UI

- User authentication (Flask-Login)

- Chart.js graphs for query trends

- Docker & docker-compose support

- Prometheus metrics endpoint

- REST API for manual block/unblock

