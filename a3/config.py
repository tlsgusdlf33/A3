"""설정 로딩.

우선순위: 환경변수 > config.yaml > 내장 기본값.
비밀값(토큰 등)은 config.yaml 대신 환경변수/.env 에 둔다.
"""

from __future__ import annotations

import copy
import os
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULTS: dict[str, Any] = {
    "timezone": "Asia/Seoul",
    "state_path": "state/a3.json",
    "owner": {
        "name": "",
        "job": "건설기계/유압 설비 엔지니어",
    },
    "exam": {
        "name": "건설기계기술사",
        # 2026년 회차(138~140회)는 종료. 다음은 2027년 141회.
        # Q-Net 공고 전까지는 추정치이므로 provisional: true 로 둔다.
        "date": "2027-02-06",
        "provisional": True,
        "round": "141회(추정)",
        "source": "https://www.q-net.or.kr/crf021.do",
        "daily_cards": 3,
        "categories": [],  # 비우면 전체. 특정 분야만 돌리고 싶을 때 채운다.
    },
    "english": {
        "name": "OPIc",
        "target_level": "IH",
        "date": "",
        "provisional": False,
        # 말하기와 표현은 quota 를 나눈다. 섞어서 뽑으면 말하기가 밀려 사라진다.
        "speaking_cards": 2,
        "word_cards": 5,
        "tags": [],  # 비우면 전체. 예: ["오픽-롤플레이", "오픽-돌발"]
    },
    "radar": {
        "max_items": 6,
        "lookback_days": 7,
        "min_score": 1,
        "google_news_queries": [
            "건설기계 기술사",
            "유압 펌프 기술 동향",
            "건설기계 배출가스 규제",
            "건설기계 안전 기준 개정",
            "기계 엔지니어 부업",
            "기술문서 번역 프리랜서",
            "중소기업 기술개발 지원사업 기계",
        ],
        "feeds": [],  # 임의 RSS/Atom URL 추가 가능
        "keywords": {
            "건설기계": 2,
            "기술사": 3,
            "유압": 2,
            "펌프": 2,
            "굴삭기": 1,
            "규제": 1,
            "개정": 1,
            "지원사업": 2,
            "공고": 1,
            "부업": 2,
            "프리랜서": 2,
            "외주": 1,
            "자문": 2,
            "강의": 1,
        },
        "exclude": ["채용공고", "구인구직"],
    },
    "brief": {
        # 기본값: 서울. Open-Meteo(키 불필요) 사용.
        "weather": True,
        "latitude": 37.5665,
        "longitude": 126.9780,
        "location_name": "서울",
    },
    "notify": {
        "channels": ["console"],  # console / ntfy / telegram / discord
        "ntfy": {
            "server": "https://ntfy.sh",
            "topic": "",  # 환경변수 A3_NTFY_TOPIC 로도 지정 가능
            "priority": "default",
        },
        "telegram": {
            "chat_id": "",  # 환경변수 A3_TELEGRAM_CHAT_ID
        },
        "discord": {
            "webhook_url": "",  # 환경변수 A3_DISCORD_WEBHOOK
        },
        "dry_run": False,
    },
}

# 환경변수 -> 설정 경로 매핑
ENV_MAP = {
    "A3_NTFY_TOPIC": ("notify", "ntfy", "topic"),
    "A3_NTFY_SERVER": ("notify", "ntfy", "server"),
    "A3_TELEGRAM_CHAT_ID": ("notify", "telegram", "chat_id"),
    "A3_DISCORD_WEBHOOK": ("notify", "discord", "webhook_url"),
    "A3_STATE_PATH": ("state_path",),
    "A3_EXAM_DATE": ("exam", "date"),
    "A3_ENGLISH_DATE": ("english", "date"),
}

# 비밀 토큰은 설정 파일에 넣지 않는다.
SECRET_ENV = {
    "ntfy_token": "A3_NTFY_TOKEN",
    "telegram_token": "A3_TELEGRAM_TOKEN",
}


def _deep_merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def _set_path(data: dict, path: tuple[str, ...], value: Any) -> None:
    node = data
    for part in path[:-1]:
        node = node.setdefault(part, {})
    node[path[-1]] = value


class Config:
    def __init__(self, data: dict[str, Any], path: Path | None = None):
        self.data = data
        self.path = path

    def get(self, *path: str, default: Any = None) -> Any:
        node: Any = self.data
        for part in path:
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    def secret(self, name: str) -> str:
        return os.environ.get(SECRET_ENV.get(name, name), "").strip()

    def resolve(self, value: str | Path) -> Path:
        """상대경로는 레포 루트 기준으로 푼다."""
        p = Path(value).expanduser()
        return p if p.is_absolute() else REPO_ROOT / p

    @property
    def state_path(self) -> Path:
        return self.resolve(self.get("state_path", default="state/a3.json"))


def load(path: str | Path | None = None) -> Config:
    """설정을 읽는다. path 가 없으면 A3_CONFIG 또는 repo/config.yaml 을 쓴다."""
    candidate = path or os.environ.get("A3_CONFIG") or REPO_ROOT / "config.yaml"
    cfg_path = Path(candidate)
    if not cfg_path.is_absolute():
        cfg_path = REPO_ROOT / cfg_path

    data = copy.deepcopy(DEFAULTS)
    if cfg_path.exists():
        loaded = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
        if not isinstance(loaded, dict):
            raise ValueError(f"{cfg_path}: 최상위는 매핑이어야 합니다.")
        data = _deep_merge(data, loaded)
    else:
        cfg_path = None  # type: ignore[assignment]

    for env_name, target in ENV_MAP.items():
        raw = os.environ.get(env_name)
        if raw is not None and raw.strip():
            _set_path(data, target, raw.strip())

    channels = os.environ.get("A3_CHANNELS", "").strip()
    if channels:
        data["notify"]["channels"] = [c.strip() for c in channels.split(",") if c.strip()]

    if os.environ.get("A3_DRY_RUN", "").strip().lower() in ("1", "true", "yes", "on"):
        data["notify"]["dry_run"] = True

    return Config(data, cfg_path)
