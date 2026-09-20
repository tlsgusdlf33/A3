"""JSON 파일 기반 상태 저장소.

SQLite 대신 JSON 을 쓰는 이유: 사람이 읽을 수 있고, git diff 가 되고,
GitHub Actions 가 매일 커밋해도 히스토리가 깨끗하게 남는다.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1


def _empty() -> dict[str, Any]:
    return {
        "schema": SCHEMA_VERSION,
        "cards": {},  # deck -> card_id -> {ease, interval, due, reps, lapses, last}
        "seen": {},  # namespace -> {key: iso_date}
        "runs": [],  # 최근 실행 기록 (최대 MAX_RUNS)
        "meta": {},
    }


MAX_RUNS = 200
MAX_SEEN_PER_NS = 2000


class Store:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.data = self._read()

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return _empty()
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError(f"{self.path}: 상태 파일을 읽을 수 없습니다 ({exc}).") from exc
        if not isinstance(raw, dict):
            raise ValueError(f"{self.path}: 상태 파일 최상위는 객체여야 합니다.")
        base = _empty()
        base.update(raw)
        for key in ("cards", "seen", "meta"):
            if not isinstance(base.get(key), dict):
                base[key] = {}
        if not isinstance(base.get("runs"), list):
            base["runs"] = []
        return base

    def save(self) -> None:
        """원자적 쓰기 — 중간에 죽어도 기존 상태가 깨지지 않는다."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(self.path.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(self.data, fh, ensure_ascii=False, indent=1, sort_keys=True)
                fh.write("\n")
            os.replace(tmp, self.path)
        except BaseException:
            Path(tmp).unlink(missing_ok=True)
            raise

    # --- 카드(간격 반복) ---

    def deck(self, name: str) -> dict[str, dict[str, Any]]:
        return self.data["cards"].setdefault(name, {})

    def card(self, deck: str, card_id: str) -> dict[str, Any] | None:
        return self.deck(deck).get(card_id)

    def put_card(self, deck: str, card_id: str, record: dict[str, Any]) -> None:
        self.deck(deck)[card_id] = record

    # --- 중복 억제(레이더) ---

    def is_seen(self, namespace: str, key: str) -> bool:
        return key in self.data["seen"].setdefault(namespace, {})

    def mark_seen(self, namespace: str, key: str, stamp: str) -> None:
        ns = self.data["seen"].setdefault(namespace, {})
        ns[key] = stamp
        if len(ns) > MAX_SEEN_PER_NS:
            # 오래된 것부터 버린다.
            for old in sorted(ns, key=lambda k: ns[k])[: len(ns) - MAX_SEEN_PER_NS]:
                ns.pop(old, None)

    # --- 실행 기록 ---

    def log_run(self, task: str, stamp: str, summary: str, ok: bool = True) -> None:
        self.data["runs"].append(
            {"task": task, "at": stamp, "summary": summary, "ok": ok}
        )
        if len(self.data["runs"]) > MAX_RUNS:
            del self.data["runs"][: len(self.data["runs"]) - MAX_RUNS]

    def recent_runs(self, limit: int = 10) -> list[dict[str, Any]]:
        return list(reversed(self.data["runs"][-limit:]))
