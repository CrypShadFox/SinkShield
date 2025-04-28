import time
import yaml
import sqlite3
from dnslib.server import DNSServer, BaseResolver
from dnslib import DNSRecord, RR, QTYPE, A

# load config
with open('config.yaml') as f:
    cfg = yaml.safe_load(f)

LISTEN_IP       = cfg['dns']['listen_ip']
PORT            = cfg['dns']['port']
UPSTREAM_DNS    = cfg['dns']['upstream_resolver']
DB_PATH         = cfg['database']['path']

def is_blocked(domain):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT 1 FROM blocked_domains WHERE domain = ?', (domain,))
    blocked = c.fetchone() is not None
    conn.close()
    return blocked

class SinkholeResolver(BaseResolver):
    def resolve(self, request, handler):
        qname  = request.q.qname
        domain = str(qname).rstrip('.')
        qtype  = request.q.qtype

        if is_blocked(domain):
            # blocked: return 0.0.0.0 with the *same* ID
            reply = request.reply()
            reply.add_answer(RR(qname, QTYPE.A, rdata=A("0.0.0.0"), ttl=60))
            log_action(domain, handler.client_address[0], "BLOCK")
            return reply

        # allowed: *proxy* the exact client packet to upstream
        try:
            # request.pack() is the raw bytes sent by your client
            raw_resp = request.send(UPSTREAM_DNS, 53, timeout=5)
            resp    = DNSRecord.parse(raw_resp)
            log_action(domain, handler.client_address[0], "ALLOW")
            return resp
        except Exception as e:
            # on any error, return a SERVFAIL with the correct ID
            reply = request.reply()
            reply.header.rcode = RCODE.SERVFAIL
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

if __name__ == "__main__":
    from database import init_db
    init_db()
    # start your blocklist updater here, too...
    resolver = SinkholeResolver()
    server = DNSServer(resolver, port=PORT, address=LISTEN_IP)
    server.start_thread()
    print(f"Sinkhole running on {LISTEN_IP}:{PORT}")
    while True:
        time.sleep(60)
