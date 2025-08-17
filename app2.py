from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = 'log.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT NOT NULL,
            name TEXT NOT NULL,
            mac TEXT NOT NULL,
            room TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT uid, name, mac, room, timestamp FROM logs ORDER BY id DESC')
    logs = c.fetchall()
    conn.close()

    html = "<h2>RFID Access Log</h2><table border='1'><tr><th>UID</th><th>Name</th><th>MAC</th><th>Room</th><th>Timestamp</th></tr>"
    for uid, name, mac, room, timestamp in logs:
        html += f"<tr><td>{uid}</td><td>{name}</td><td>{mac}</td><td>{room}</td><td>{timestamp}</td></tr>"
    html += "</table>"
    return html

@app.route('/log', methods=['POST'])
def log_data():
    try:
        data = request.get_json(force=True)
        print("📥 Received:", data)

        uid = data.get('uid')
        name = data.get('name')
        mac = data.get('mac')
        room = data.get('room')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if not uid or not name or not mac or not room:
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('INSERT INTO logs (uid, name, mac, room, timestamp) VALUES (?, ?, ?, ?, ?)',
                  (uid, name, mac, room, timestamp))
        conn.commit()
        conn.close()

        return jsonify({'status': 'success', 'message': 'Log recorded'}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')