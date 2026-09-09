from dataclasses import asdict
import time
from uuid import uuid4
from mini_agno.db.base import BaseDb
from mini_agno.models.message import Message
from mini_agno.session import Session
import sqlite3
import json


class SqliteDb(BaseDb):

    def __init__(self, db_file: str | None = None):
        self.db_file = db_file if db_file is not None else "db/mini_agno.db"
        self._create_table()

    def _create_table(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        with conn:
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS session
                         (session_id TEXT PRIMARY KEY,user_id TEXT NOT NULL, messages TEXT)"""
            )
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS memory
                         (memory_id TEXT PRIMARY KEY,user_id TEXT NOT NULL, memory TEXT,created_at INTEGER)"""
            )
        conn.close()

    def get_session(self, session_id: str) -> dict:
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT session_id, user_id, messages FROM session WHERE session_id = ?",
                (session_id,),
            )
            result = cursor.fetchone()

            if result is None:
                return None

            db_session_id, user_id, messages_json_str = result
            messages = [
                Message.model_validate(m) for m in json.loads(messages_json_str)
            ]
            return {
                "session_id": db_session_id,
                "user_id": user_id,
                "messages": messages,
            }

        finally:
            conn.close()

    def upsert_session(self, session: Session) -> None:
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            messages_as_dicts = [msg.model_dump() for msg in session.messages]

            cursor.execute(
                "INSERT OR REPLACE INTO session (session_id,user_id, messages) VALUES (?,?, ?)",
                (session.session_id, session.user_id, json.dumps(messages_as_dicts)),
            )
            conn.commit()
        finally:
            conn.close()

    def get_memories(self, user_id: str) -> list[str]:
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT memory_id, memory FROM memory WHERE user_id = ?",
                (user_id,),
            )
            result = cursor.fetchall()
            return [r[1] for r in result]
        finally:
            conn.close()

    def add_memory(self, user_id: str, memory: str) -> None:
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT memory_id FROM memory WHERE user_id = ? and memory = ?",
                (user_id, memory),
            )
            result = cursor.fetchone()
            # 如果改记忆不存在就插入(这里应该要做语义相似度分析，但先不考虑，比较复杂)
            if result is None:
                cursor.execute(
                    "INSERT INTO memory (memory_id, user_id, memory,created_at) VALUES (?,?, ?, ?)",
                    (uuid4().hex, user_id, memory, int(time.time() * 1000)),
                )
                cursor.execute(
                    "SELECT COUNT(*) FROM memory WHERE user_id = ?", (user_id,)
                )
                count = cursor.fetchone()[0]
                cursor.execute(
                    """
                    DELETE FROM memory WHERE rowid IN (
                        SELECT rowid FROM memory WHERE user_id = ? ORDER BY created_at ASC LIMIT ?
                    )
                    """,
                    (user_id, max(0, count - 50)),
                )
                conn.commit()
        finally:
            conn.close()
