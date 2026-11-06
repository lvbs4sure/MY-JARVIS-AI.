"""Bounded, inert, local-only previews. No filesystem writes or model calls."""
from pathlib import PureWindowsPath

MAX_BYTES = 1_000_000


def preview_upload(upload):
    name = PureWindowsPath(str(upload.name)).name
    if PureWindowsPath(name).suffix.lower() not in {".txt", ".md", ".csv"}:
        raise ValueError("Choose a TXT, Markdown or CSV file.")
    if upload.size > MAX_BYTES:
        raise ValueError("File exceeds the 1 MB preview limit. Nothing was saved.")
    position = upload.tell()
    try:
        upload.seek(0)
        payload = upload.read(MAX_BYTES + 1)
    finally:
        upload.seek(position)
    if len(payload) > MAX_BYTES:
        raise ValueError("File exceeds the 1 MB preview limit. Nothing was saved.")
    try:
        text = payload.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("Preview requires a UTF-8 text file.") from None
    if any(ord(char) < 32 and char not in "\t\n\r" for char in text):
        raise ValueError("This file contains binary control data and cannot be previewed.")
    return name, text[:4000], len(payload), len(text) > 4000
