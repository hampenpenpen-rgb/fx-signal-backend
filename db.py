import sqlite3, time
from typing import List, Dict, Any

DB_PATH = "app.sqlite3"

def now() -> int:
    return int(time.time())

def conn():
    c = sqlite3.connect(DB_PATH)
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA busy_timeout=5000")
    return c

def init_db():
    c = conn(); cur = c.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS devices(
      device_id TEXT PRIMARY KEY,
      expo_token TEXT NOT NULL,
      updated_at INTEGER NOT NULL
    )""")
    c.commit(); c.close()

def upsert_device(device_id: str, expo_token: str):
    c = conn(); cur = c.cursor()
    cur.execute("""INSERT INTO devices(device_id, expo_token, updated_at)
      VALUES(?,?,?)
      ON CONFLICT(device_id) DO UPDATE SET expo_token=excluded.expo_token, updated_at=excluded.updated_at
    """, (device_id, expo_token, now()))
    c.commit(); c.close()

def list_devices() -> List[Dict[str, Any]]:
    c = conn(); cur = c.cursor()
    cur.execute("SELECT device_id, expo_token FROM devices ORDER BY updated_at DESC")
    rows = [{"device_id": r[0], "expo_token": r[1]} for r in cur.fetchall()]
    c.close(); return rows
