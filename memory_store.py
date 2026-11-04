"""Private per-installation memory store. Never put this database in Git."""
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(os.environ.get("JARVIS_DB_PATH", Path(__file__).resolve().parent / "jarvis_memory.db"))


@contextmanager
def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    try:
        with db:
            db.execute("CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY, note TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
            yield db
    finally:
        db.close()


def add_memory(note: str) -> None:
    if not isinstance(note, str):
        raise ValueError("Memory must be text.")
    note = note.strip()
    if not note or len(note) > 2000:
        raise ValueError("Memory must contain 1–2000 characters.")
    with connect() as db:
        db.execute("INSERT INTO memories(note) VALUES (?)", (note,))


def count_memories():
    with connect() as db:
        return db.execute("SELECT COUNT(*) FROM memories").fetchone()[0]


def list_memories(limit: int = 100):
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
        raise ValueError("Memory list limit must be between 1 and 1000.")
    with connect() as db:
        return db.execute("SELECT id, note, created_at FROM memories ORDER BY id DESC LIMIT ?", (limit,)).fetchall()


def update_memory(memory_id: int, note: str) -> bool:
    if not isinstance(note, str):
        raise ValueError("Memory must be text.")
    note = note.strip()
    if not note or len(note) > 2000:
        raise ValueError("Memory must contain 1–2000 characters.")
    with connect() as db:
        result = db.execute("UPDATE memories SET note = ? WHERE id = ?", (note, memory_id))
        return result.rowcount > 0


def delete_memory(memory_id: int) -> bool:
    with connect() as db:
        result = db.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        return result.rowcount > 0


def search_memories(query: str, limit: int = 20):
    """Search private notes without exposing them to an external search service."""
    if not isinstance(query, str):
        raise ValueError("Search must be text.")
    query = query.strip()
    if not query:
        return []
    if len(query) > 200:
        raise ValueError("Search must be at most 200 characters.")
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 100:
        raise ValueError("Search limit must be between 1 and 100.")
    # Escape LIKE wildcards so a user's % or _ is treated literally.
    escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    with connect() as db:
        return db.execute(
            "SELECT id, note, created_at FROM memories "
            "WHERE note LIKE ? ESCAPE '\\' ORDER BY id DESC LIMIT ?",
            (f"%{escaped}%", limit),
        ).fetchall()
