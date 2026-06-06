import sqlite3
from datetime import datetime
from pathlib import Path


class SQLiteMemory:
    def __init__(self, db_path: str = "data/memory/edgetalk.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def save_message(self, session_id: str, role: str, content: str):
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO messages (session_id, role, content, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, role, content, created_at)
            )
            conn.commit()

    def get_recent_messages(self, session_id: str, limit: int = 6):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT role, content, created_at
                FROM messages
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (session_id, limit)
            )

            rows = cursor.fetchall()

        messages = [
            {
                "role": row[0],
                "content": row[1],
                "created_at": row[2]
            }
            for row in rows
        ]

        return list(reversed(messages))
