import json
import sqlite3
import time
from pathlib import Path

from .config import get_settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  name TEXT NOT NULL,
  size INTEGER NOT NULL,
  status TEXT NOT NULL,
  pages INTEGER NOT NULL DEFAULT 0,
  chunks INTEGER NOT NULL DEFAULT 0,
  error TEXT,
  created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_documents_user ON documents(user_id);
CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  role TEXT NOT NULL,
  text TEXT NOT NULL,
  sources TEXT NOT NULL DEFAULT '[]',
  error TEXT NOT NULL DEFAULT '',
  created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(user_id, id);
"""


def data_path() -> Path:
    path = Path(get_settings().data_dir)
    (path / "pdfs").mkdir(parents=True, exist_ok=True)
    return path


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(data_path() / "documind.db")
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def create_document(doc_id: str, user_id: str, name: str, size: int) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT INTO documents (id, user_id, name, size, status, created_at) VALUES (?,?,?,?,?,?)",
            (doc_id, user_id, name, size, "indexing", time.time()),
        )


def update_document(doc_id: str, **fields) -> None:
    keys = ", ".join(f"{k} = ?" for k in fields)
    with connect() as conn:
        conn.execute(f"UPDATE documents SET {keys} WHERE id = ?", (*fields.values(), doc_id))


def list_documents(user_id: str) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM documents WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_document(doc_id: str, user_id: str) -> dict | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM documents WHERE id = ? AND user_id = ?", (doc_id, user_id)
        ).fetchone()
    return dict(row) if row else None


def delete_document(doc_id: str) -> None:
    with connect() as conn:
        conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))


def fail_stale_indexing() -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE documents SET status='error', error='El servidor se reinició durante el indexado' WHERE status='indexing'"
        )


def add_message(user_id: str, role: str, text: str, sources: list | None = None, error: str = "") -> None:
    with connect() as conn:
        conn.execute(
            "INSERT INTO messages (user_id, role, text, sources, error, created_at) VALUES (?,?,?,?,?,?)",
            (user_id, role, text, json.dumps(sources or [], ensure_ascii=False), error, time.time()),
        )


def list_messages(user_id: str, limit: int = 200) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM (SELECT * FROM messages WHERE user_id = ? ORDER BY id DESC LIMIT ?) ORDER BY id",
            (user_id, limit),
        ).fetchall()
    return [{**dict(r), "sources": json.loads(r["sources"])} for r in rows]


def clear_messages(user_id: str) -> None:
    with connect() as conn:
        conn.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
