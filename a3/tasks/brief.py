"""아침 브리핑 — 오늘 하루의 좌표를 한 화면에."""

from __future__ import annotations

import logging

import requests

from a3 import srs, util
from a3.config import Config
from a3.notify import Message
from a3.store import Store
from a3.tasks import TaskResult, register
from a3.tasks.decks import load_deck

log = logging.getLogger(__name__)
TIMEOUT = 15
OPEN_METEO = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "맑음", 1: "대체로 맑음", 2: "구름 조금", 3: "흐림",
    45: "안개", 48: "서리 안개", 51: "이슬비", 53: "이슬비", 55: "짙은 이슬비",
    61: "약한 비", 63: "비", 65: "강한 비", 71: "약한 눈", 73: "눈", 75: "강한 눈",
    80: "소나기", 81: "소나기", 82: "강한 소나기", 95: "뇌우", 96: "뇌우(우박)", 99: "뇌우(우박)",
}


def fetch_weather(config: Config) -> str:
    if not config.get("brief", "weather", default=True):
        return ""
    lat = config.get("brief", "latitude", default=37.5665)
    lon = config.get("brief", "longitude", default=126.9780)
    place = config.get("brief", "location_name", default="")
    try:
        resp = requests.get(
            OPEN_METEO,
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                "timezone": "Asia/Seoul",
                "forecast_days": 1,
            },
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        daily = resp.json()["daily"]
        code = WEATHER_CODES.get(daily["weather_code"][0], "—")
        lo, hi = daily["temperature_2m_min"][0], daily["temperature_2m_max"][0]
        pop = daily["precipitation_probability_max"][0]
        rain = f" · 강수확률 {pop}%" if pop is not None else ""
        return f"🌤️ {place} {code} {lo:.0f}~{hi:.0f}℃{rain}"
    except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
        log.warning("날씨 조회 실패: %s", exc)
        return ""


def _queue_line(config: Config, store: Store, key: str, filename: str, label: str) -> str:
    try:
        cards = load_deck(filename)["cards"]
    except (FileNotFoundError, ValueError) as exc:
        return f"{label}: 덱 오류 ({exc})"
    today = util.today()
    state = store.deck(key)
    due = sum(1 for c in cards if (r := state.get(str(c["id"]))) and srs.is_due(r, today))
    fresh = sum(1 for c in cards if str(c["id"]) not in state)
    done = len(cards) - fresh
    pct = int(done / len(cards) * 100) if cards else 0
    return f"{label}: 복습 {due} · 새카드 {fresh} · 진도 {done}/{len(cards)} ({pct}%)"


def _dday_line(config: Config, section: str, icon: str) -> str:
    raw = config.get(section, "date", default="")
    name = config.get(section, "name", default=section)
    date = util.parse_date(raw) if raw else None
    if not date:
        return ""
    label = util.dday_label(date)
    mark = " ※추정" if config.get(section, "provisional", default=False) else ""
    return f"{icon} {name} {label} ({date.isoformat()}){mark}"


@register("brief", "아침 브리핑 — D-day, 학습 큐, 날씨, 최근 실행")
def run(config: Config, store: Store) -> TaskResult:
    today = util.today()
    weekday = "월화수목금토일"[today.weekday()]
    lines = [f"{today.isoformat()} ({weekday})"]

    weather = fetch_weather(config)
    if weather:
        lines.append(weather)
    lines.append("")

    for section, icon in (("exam", "🏗️"), ("english", "🗣️")):
        line = _dday_line(config, section, icon)
        if line:
            lines.append(line)
    lines.append("")

    lines.append("📚 오늘의 학습량")
    lines.append("  " + _queue_line(config, store, "exam", "exam_deck.yaml", "기술사"))
    lines.append("  " + _queue_line(config, store, "english", "english_deck.yaml", "영어"))

    runs = store.recent_runs(4)
    if runs:
        lines.append("")
        lines.append("🕒 최근 실행")
        for r in runs:
            mark = "✓" if r.get("ok", True) else "✗"
            lines.append(f"  {mark} {r['at'][:16]} {r['task']} — {r['summary']}")

    return TaskResult(
        "brief",
        Message("☀️ 오늘의 브리핑", "\n".join(lines), tags=["sunrise"]),
        "브리핑 발송",
    )
