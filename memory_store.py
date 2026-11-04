"""Private per-installation memory store. Never put this database in Git."""
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.environ.get("JARVIS_DB_PATH", Path(__file__).resolve().parent / "jarvis_memory.db"))


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.execute("CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY, note TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
    db.commit()
    return db


def add_memory(note: str) -> None:
    note = note.strip()
    if not note or len(note) > 2000:
        raise ValueError("Memory must contain 1–2000 characters.")
    with connect() as db:
        db.execute("INSERT INTO memories(note) VALUES (?)", (note,))


def list_memories(limit: int = 100):
    with connect() as db:
        return db.execute("SELECT id, note, created_at FROM memories ORDER BY id DESC LIMIT ?", (limit,)).fetchall()


def update_memory(memory_id: int, note: str) -> bool:
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
