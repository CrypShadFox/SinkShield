
from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route('/')
def home():
    conn = sqlite3.connect('sinkhole.db')
    c = conn.cursor()
    c.execute('SELECT * FROM query_logs ORDER BY timestamp DESC LIMIT 50')
    logs = c.fetchall()
    conn.close()
    return str(logs)  # Later replace with a real HTML template!

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

