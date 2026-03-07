import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Dict, List, Optional

class SqlEngine:
    def __init__(self, db_path: str = "gut_reigns.db"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS player_stats (
                    key TEXT PRIMARY KEY,
                    value INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    weeks_survived INTEGER,
                    ending_id TEXT,
                    death_reason TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS unlocked_cards (
                    card_id TEXT PRIMARY KEY,
                    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS seen_endings (
                    ending_id TEXT PRIMARY KEY,
                    seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def record_run(self, weeks: int, ending_id: str, death_reason: str) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO runs (weeks_survived, ending_id, death_reason) VALUES (?, ?, ?)",
                (weeks, ending_id, death_reason)
            )
            # Update total runs
            conn.execute("INSERT OR IGNORE INTO player_stats (key, value) VALUES ('total_runs', 0)")
            conn.execute("UPDATE player_stats SET value = value + 1 WHERE key = 'total_runs'")
            
            # Update seen ending
            conn.execute("INSERT OR IGNORE INTO seen_endings (ending_id) VALUES (?)", (ending_id,))
            
            conn.commit()

    def get_profile(self) -> Dict:
        with self._conn() as conn:
            stats = dict(conn.execute("SELECT key, value FROM player_stats").fetchall())
            seen_endings = [r["ending_id"] for r in conn.execute("SELECT ending_id FROM seen_endings").fetchall()]
            max_weeks_row = conn.execute("SELECT MAX(weeks_survived) as m FROM runs").fetchone()
            max_weeks = max_weeks_row["m"] if max_weeks_row and max_weeks_row["m"] else 0
            
            total_runs = stats.get("total_runs", 0)
            
            return {
                "total_runs": total_runs,
                "max_weeks": max_weeks,
                "seen_endings": seen_endings,
                "death_count": total_runs  # Approximate, assuming every run is a death/end
            }
