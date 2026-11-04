"""Opt-in, per-installation local chat history, separate from private memories."""
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import re
import sqlite3
import uuid

DB_PATH=Path(__file__).resolve().parent/"jarvis_chat_history.db"


def _validate_id(value):
    if not isinstance(value,str) or not re.fullmatch(r"[a-f0-9]{32}",value):
        raise ValueError("Invalid conversation identifier.")


def _messages(messages):
    if not isinstance(messages,list) or len(messages)>1000:
        raise ValueError("Chat history supports up to 1,000 messages per conversation. Existing saved history is unchanged.")
    clean=[]
    for item in messages:
        if not isinstance(item,dict) or item.get("role") not in ("user","assistant") or not isinstance(item.get("content"),str):
            raise ValueError("Invalid conversation message.")
        if item.get("cancelled") or not item.get("ok",True):
            continue
        text=item["content"]
        for variable in ("GEMINI_API_KEY","GOOGLE_API_KEY","OPENAI_API_KEY"):
            key=os.getenv(variable,"")
            if len(key)>=8:
                text=text.replace(key,"[redacted API key]")
        clean.append({"role":item["role"],"content":text})
    payload=json.dumps(clean,ensure_ascii=False)
    if len(payload.encode("utf-8"))>2_000_000:
        raise ValueError("Conversation exceeds the 2 MB history limit. Existing saved history is unchanged.")
    return clean,payload


@contextmanager
def _connect():
    connection=sqlite3.connect(DB_PATH,timeout=3)
    try:
        with connection:
            connection.execute("CREATE TABLE IF NOT EXISTS conversations (id TEXT PRIMARY KEY, title TEXT NOT NULL, messages TEXT NOT NULL, updated_at TEXT NOT NULL)")
            yield connection
    finally:
        connection.close()


def save_conversation(messages,conversation_id=None):
    clean,payload=_messages(messages)
    if not clean:return conversation_id
    identity=conversation_id or uuid.uuid4().hex
    _validate_id(identity)
    title=next((row["content"] for row in clean if row["role"]=="user"),"Conversation").replace("\n"," ")[:60]
    updated=datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _connect() as db:
        db.execute("INSERT INTO conversations VALUES (?, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET title=excluded.title, messages=excluded.messages, updated_at=excluded.updated_at",(identity,title,payload,updated))
    return identity


def list_conversations():
    if not DB_PATH.exists():return []
    with _connect() as db:
        return db.execute("SELECT id,title,updated_at FROM conversations ORDER BY updated_at DESC, rowid DESC LIMIT 100").fetchall()


def load_conversation(identity):
    _validate_id(identity)
    if not DB_PATH.exists():return None
    with _connect() as db:
        row=db.execute("SELECT messages FROM conversations WHERE id=?",(identity,)).fetchone()
    return _messages(json.loads(row[0]))[0] if row else None


def sync_history(state):
    if not state.get("save_chat_history") or not state.get("chat") or state.get("request_job") is not None:
        return
    _,payload=_messages(state["chat"])
    if payload==state.get("history_snapshot"):return
    identity=save_conversation(state["chat"],state.get("history_id"))
    if identity:
        state["history_id"]=identity
        state["history_snapshot"]=payload
