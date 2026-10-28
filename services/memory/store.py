
import os
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = PROJECT_ROOT / "storage" / "jarvis_memory.sqlite3"


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class MemoryStore:
    """Persistent local storage for JARVIS conversations and messages."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        configured_path = db_path or os.getenv("JARVIS_MEMORY_DB")
        self.db_path = (
            Path(configured_path).expanduser().resolve()
            if configured_path
            else DEFAULT_DB_PATH
        )
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                    content TEXT NOT NULL CHECK (length(content) > 0),
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (conversation_id)
                        REFERENCES conversations(conversation_id)
                        ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_messages_conversation_time
                    ON messages(conversation_id, created_at);
                """
            )

    def create_conversation(self, title: str = "New conversation") -> str:
        conversation_id = str(uuid4())
        now = utc_now()

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO conversations
                    (conversation_id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (conversation_id, title, now, now),
            )

        return conversation_id

    def save_exchange(
        self,
        conversation_id: str,
        user_message: str,
        assistant_reply: str,
    ) -> None:
        """Save both sides of an exchange atomically."""
        now = utc_now()

        with self._connect() as connection:
            conversation = connection.execute(
                "SELECT 1 FROM conversations WHERE conversation_id = ?",
                (conversation_id,),
            ).fetchone()

            if conversation is None:
                raise ValueError("Conversation does not exist.")

            connection.executemany(
                """
                INSERT INTO messages
                    (message_id, conversation_id, role, content, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (str(uuid4()), conversation_id, "user", user_message, now),
                    (str(uuid4()), conversation_id, "assistant", assistant_reply, now),
                ],
            )

            connection.execute(
                "UPDATE conversations SET updated_at = ? WHERE conversation_id = ?",
                (now, conversation_id),
            )

    
    def get_messages(
        self,
        conversation_id: str,
        limit: int = 100,
    ) -> list[dict[str, str]]:
        if limit < 1:
            raise ValueError("Limit must be positive.")

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT role, content, created_at
                FROM (
                    SELECT
                        role,
                        content,
                        created_at,
                        rowid AS sequence
                    FROM messages
                    WHERE conversation_id = ?
                    ORDER BY created_at DESC, rowid DESC
                    LIMIT ?
                )
                ORDER BY created_at ASC, sequence ASC
                """,
                (conversation_id, limit),
            ).fetchall()

        return [dict(row) for row in rows]

    
    def list_conversations(self, limit: int = 50) -> list[dict[str, str]]:
        if limit < 1:
            raise ValueError("Limit must be positive.")

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT conversation_id, title, created_at, updated_at
                FROM conversations
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [dict(row) for row in rows]
    
    
    def conversation_exists(self, conversation_id: str) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM conversations WHERE conversation_id = ?",
                (conversation_id,),
            ).fetchone()

        return row is not None


