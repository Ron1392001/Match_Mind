import sqlite3

conn = sqlite3.connect('data.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS players_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    round_name TEXT NOT NULL,
    player_name TEXT NOT NULL,
    team TEXT,
    goals INTEGER,
    assists INTEGER,
    passes INTEGER,
    distance REAL,
    position TEXT,
    date_added TEXT DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()

print("✅ Database initialized successfully.")