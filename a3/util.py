"""작은 공용 도구들."""

from __future__ import annotations

import datetime as dt
import os
import re
import unicodedata

KST = dt.timezone(dt.timedelta(hours=9))


def now() -> dt.datetime:
    """설정된 타임존(기본 KST) 기준 현재 시각."""
    return dt.datetime.now(tz=KST)


def today() -> dt.date:
    return now().date()


def parse_date(value: str | dt.date | None) -> dt.date | None:
    if value is None:
        return None
    if isinstance(value, dt.date):
        return value
    value = str(value).strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%Y.%m.%d", "%Y/%m/%d", "%Y%m%d"):
        try:
            return dt.datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"날짜 형식을 알 수 없습니다: {value!r}")


def dday(target: dt.date, base: dt.date | None = None) -> int:
    """남은 일수. 양수면 아직 남음, 0이면 당일, 음수면 지남."""
    return (target - (base or today())).days


def dday_label(target: dt.date, base: dt.date | None = None) -> str:
    d = dday(target, base)
    if d > 0:
        return f"D-{d}"
    if d == 0:
        return "D-DAY"
    return f"D+{-d}"


def display_width(text: str) -> int:
    """한글 등 전각 문자를 2칸으로 세는 표시 폭."""
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in text)


def truncate(text: str, limit: int, suffix: str = "…") -> str:
    """표시 폭 기준으로 자른다."""
    if display_width(text) <= limit:
        return text
    out, width = [], 0
    budget = limit - display_width(suffix)
    for ch in text:
        w = 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
        if width + w > budget:
            break
        out.append(ch)
        width += w
    return "".join(out) + suffix


_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def strip_html(text: str) -> str:
    import html

    return _WS_RE.sub(" ", html.unescape(_TAG_RE.sub(" ", text or ""))).strip()


def env_flag(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "y", "on")
