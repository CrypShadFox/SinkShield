import sqlite3
import requests
import yaml
import os
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

def load_config():
    with open('config.yaml') as f:
        return yaml.safe_load(f)

def fetch_feed(url):
    """Download a blocklist and return a list of domains."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return [line.strip() for line in resp.text.splitlines()
            if line and not line.startswith('#')]

def load_local_file(path):
    """Load a local blocklist and return a list of domains."""
    if not os.path.exists(path):
        print(f"[{datetime.now()}] Local file not found: {path}")
        return []
    with open(path, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

def update_blocklist(db_path, feed_urls, local_files):
    """Fetch all feeds and local files and upsert them into the DB."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Load from URLs
    for url in feed_urls:
        try:
            domains = fetch_feed(url)
            for domain in domains:
                c.execute(
                    'INSERT OR IGNORE INTO blocked_domains(domain) VALUES (?)',
                    (domain,)
                )
            print(f"[{datetime.now()}] Updated from {url} ({len(domains)} domains)")
        except Exception as e:
            print(f"[{datetime.now()}] Failed to update {url}: {e}")

    # Load from local files
    for filepath in local_files:
        try:
            domains = load_local_file(filepath)
            for domain in domains:
                c.execute(
                    'INSERT OR IGNORE INTO blocked_domains(domain) VALUES (?)',
                    (domain,)
                )
            print(f"[{datetime.now()}] Updated from {filepath} ({len(domains)} domains)")
        except Exception as e:
            print(f"[{datetime.now()}] Failed to update {filepath}: {e}")

    conn.commit()
    conn.close()

def start_scheduler():
    cfg = load_config()
    db_path = cfg['database']['path']
    urls = cfg['blocklist']['urls']
    locals = cfg['blocklist'].get('local_files', [])
    interval = cfg['blocklist']['update_interval_hours']

    scheduler = BackgroundScheduler()
    # Run once at startup
    scheduler.add_job(update_blocklist, 'date',
                      args=[db_path, urls, locals], id='initial_load')
    # Then every N hours
    scheduler.add_job(update_blocklist, 'interval',
                      hours=interval, args=[db_path, urls, locals], id='periodic_load')
    scheduler.start()
    print(f"Blocklist updater scheduled every {interval} hour(s).")

if __name__ == "__main__":
    start_scheduler()
    # Keep the script alive so the scheduler can run:
    import time
    while True:
        time.sleep(60)
