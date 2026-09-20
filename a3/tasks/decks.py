"""YAML 덱 로딩 (exam/english 공용)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@lru_cache(maxsize=8)
def load_deck(filename: str) -> dict[str, Any]:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"덱 파일이 없습니다: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    cards = data.get("cards") or []
    if not cards:
        raise ValueError(f"{path}: cards 가 비어 있습니다.")
    ids = [str(c["id"]) for c in cards]
    if len(ids) != len(set(ids)):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        raise ValueError(f"{path}: 중복된 카드 id {dupes}")
    return data
