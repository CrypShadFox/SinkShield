# SinkShield

![Python Version](https://img.shields.io/badge/python-3.10%2B-green)

A **Simple DNS Sinkhole & Blocklist Manager** with auto-updating feeds, proxying for allowed queries, and a Flask Web interface. Good for home labs and SOC learning.

---

## Features

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

## Prerequisites

- **Python 3.10+**  
- `pip`  
- Optional: a Linux/WSL environment for binding to low ports (53)

---

## Installation

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
# config.yaml

database:
  path: "sinkhole.db"

dns:
  listen_ip: "127.0.0.1"
  port: 5353
  timeout: 10
  upstream_resolver: "8.8.8.8"

blocklist:
  urls:
    - "https://v.firebog.net/hosts/AdguardDNS.txt"
    - "https://v.firebog.net/hosts/Prigent-Ads.txt"
    - "https://gitlab.com/quidsup/notrack-blocklists/raw/master/notrack-blocklist.txt"
  local_files:
    - "txt/C2.txt" # Example
  update_interval_hours: 24  # Set how often you want to update the blocklist
```
## Usage

- Initialize the database

```bash
python3 src/database.py
```

- Start the server
```bash
python3 src/main.py
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

- Chart.js graphs for query trends


