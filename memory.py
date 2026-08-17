import sqlite3
import threading
import time
from typing import List, Dict

class MemoryStore:
    def __init__(self, db_path: str = "memory.db", max_messages: int = 10):
        self.db_path = db_path
        self.max_messages = max_messages  # number of pairs (user+assistant approx)
        self._lock = threading.Lock()

    def init_db(self):
        with self._get_conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at INTEGER NOT NULL
                )
                """
            )
            conn.commit()

    def _get_conn(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def add_message(self, chat_id: str, role: str, content: str):
        timestamp = int(time.time())
        with self._lock, self._get_conn() as conn:
            conn.execute(
                "INSERT INTO messages (chat_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (chat_id, role, content, timestamp),
            )
            conn.commit()
            self._trim_history(conn, chat_id)

    def _trim_history(self, conn, chat_id: str):
        # Keep only the most recent N*2 rows (approx user+assistant pairs)
        max_rows = self.max_messages * 2
        cur = conn.execute(
            "SELECT COUNT(*) FROM messages WHERE chat_id = ?", (chat_id,)
        )
        (count,) = cur.fetchone()
        if count <= max_rows:
            return
        # delete oldest rows
        to_delete = count - max_rows
        conn.execute(
            "DELETE FROM messages WHERE id IN (SELECT id FROM messages WHERE chat_id = ? ORDER BY created_at ASC LIMIT ?)",
            (chat_id, to_delete),
        )
        conn.commit()

    def get_history(self, chat_id: str) -> List[Dict[str, str]]:
        with self._get_conn() as conn:
            cur = conn.execute(
                "SELECT role, content FROM messages WHERE chat_id = ? ORDER BY created_at ASC",
                (chat_id,),
            )
            rows = cur.fetchall()
            # Convert to list of message dicts for OpenAI
            return [{"role": r[0], "content": r[1]} for r in rows]

    def clear_history(self, chat_id: str):
        with self._get_conn() as conn:
            conn.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
            conn.commit()
