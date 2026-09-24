"""A dead-simple JSON disk cache so real model calls are made at most once.

Keyed by (tier name, model, prompt, sample index). Lets you re-run the harness
and the deferral sweep without paying for the large model twice.
"""
from __future__ import annotations

import hashlib
import json
import os
import threading

from .config import CACHE_PATH

_lock = threading.Lock()
_store: dict | None = None


def _load() -> dict:
    global _store
    if _store is None:
        if os.path.exists(CACHE_PATH):
            with open(CACHE_PATH, "r") as f:
                _store = json.load(f)
        else:
            _store = {}
    return _store


def key(*parts) -> str:
    raw = "\x1f".join(str(p) for p in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get(k: str):
    with _lock:
        return _load().get(k)


def put(k: str, value: dict) -> None:
    with _lock:
        store = _load()
        store[k] = value
        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        tmp = CACHE_PATH + ".tmp"
        with open(tmp, "w") as f:
            json.dump(store, f)
        os.replace(tmp, CACHE_PATH)
