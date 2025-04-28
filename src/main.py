# sinkhole/main.py

import time
import threading
import yaml
import sqlite3
from dnslib.server import DNSServer, BaseResolver
from dnslib import DNSRecord, RR, QTYPE, A
from flask import Flask
from updater import start_scheduler  # Make sure updater.py is importable!
from database import init_db

# ---- Load config ----
with open('config.yaml') as f:
    cfg = yaml.safe_load(f)

LISTEN_IP = cfg['dns']['listen_ip']
PORT = cfg['dns']['port']
UPSTREAM_DNS = cfg['dns']['upstream_resolver']
DB_PATH = cfg['database']['path']

# ---- DNS Sinkhole Resolver ----
def is_blocked(domain):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT 1 FROM blocked_domains WHERE domain = ?', (domain,))
    blocked = c.fetchone() is not None
    conn.close()
    return blocked

class SinkholeResolver(BaseResolver):
    def resolve(self, request, handler):
        qname = request.q.qname
        domain = str(qname).rstrip('.')
        qtype = request.q.qtype

        if is_blocked(domain):
            reply = request.reply()
            reply.add_answer(RR(qname, QTYPE.A, rdata=A("0.0.0.0"), ttl=60))
            log_action(domain, handler.client_address[0], "BLOCK")
            return reply
        try:
            raw_resp = request.send(UPSTREAM_DNS, 53, timeout=5)
            resp = DNSRecord.parse(raw_resp)
            log_action(domain, handler.client_address[0], "ALLOW")
            return resp
        except Exception as e:
            reply = request.reply()
            reply.header.rcode = 2  # RCODE.SERVFAIL
            log_action(domain, handler.client_address[0], "ERROR")
            return reply

def log_action(domain, client_ip, action):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
      "INSERT INTO query_logs(timestamp, client_ip, domain, action) VALUES(datetime('now'), ?, ?, ?)",
      (client_ip, domain, action)
    )
    conn.commit()
    conn.close()

# ---- Web UI ----
app = Flask(__name__)

@app.route('/')
def home():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM query_logs ORDER BY timestamp DESC LIMIT 50')
    logs = c.fetchall()
    conn.close()
    return str(logs)  # Later replace with a real HTML template!

# ---- Runner Threads ----
def run_dns_server():
    resolver = SinkholeResolver()
    server = DNSServer(resolver, port=PORT, address=LISTEN_IP)
    server.start_thread()
    print(f"Sinkhole DNS server running on {LISTEN_IP}:{PORT}")

def run_web_ui():
    app.run(host="127.0.0.1", port=5000, debug=False)  # set debug=False for production

def run_blocklist_updater():
    start_scheduler()

# ---- Main Entrypoint ----
if __name__ == "__main__":
    init_db()

    # Start DNS server in a thread
    threading.Thread(target=run_dns_server, daemon=True).start()

    # Start blocklist updater in a thread
    threading.Thread(target=run_blocklist_updater, daemon=True).start()

    # Start web UI (blocking call, stays in main thread)
    run_web_ui()

