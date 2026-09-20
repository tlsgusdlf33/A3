"""휴대폰 알림 발송.

채널 우선순위 없이 설정된 모든 채널로 보낸다. 한 채널이 실패해도 나머지는 계속.
- ntfy   : 앱 설치 + 토픽 이름만 있으면 끝. 가입/서버 불필요. (권장)
- telegram: 봇 토큰 + chat_id
- discord : 웹훅 URL
- console : 표준출력 (로컬 테스트/Actions 로그)
"""

from __future__ import annotations

import json
import logging
import urllib.parse
from dataclasses import dataclass, field
from typing import Any

import requests

from a3.util import truncate

log = logging.getLogger(__name__)

TIMEOUT = 20
# ntfy 본문 상한. 서버 기본 제한(4KiB)보다 넉넉히 아래로 잡는다.
NTFY_BODY_LIMIT = 3500
TELEGRAM_LIMIT = 4000
DISCORD_LIMIT = 1900
PRIORITY_MAP = {"min": 1, "low": 2, "default": 3, "high": 4, "max": 5, "urgent": 5}


@dataclass
class Message:
    title: str
    body: str
    tags: list[str] = field(default_factory=list)
    priority: str = "default"
    click_url: str = ""


@dataclass
class Result:
    channel: str
    ok: bool
    detail: str = ""


class Notifier:
    def __init__(self, config, session: requests.Session | None = None):
        self.config = config
        self.session = session or requests.Session()
        self.channels = list(config.get("notify", "channels", default=["console"]))
        self.dry_run = bool(config.get("notify", "dry_run", default=False))

    def send(self, message: Message) -> list[Result]:
        results: list[Result] = []
        for channel in self.channels:
            handler = getattr(self, f"_send_{channel}", None)
            if handler is None:
                results.append(Result(channel, False, "알 수 없는 채널"))
                continue
            if self.dry_run and channel != "console":
                results.append(Result(channel, True, "dry-run (실제 발송 안 함)"))
                continue
            try:
                results.append(handler(message))
            except requests.RequestException as exc:
                log.warning("%s 발송 실패: %s", channel, exc)
                results.append(Result(channel, False, str(exc)))
        if not results:
            results.append(Result("none", False, "설정된 채널이 없습니다."))
        return results

    # --- 채널 구현 ---

    def _send_console(self, message: Message) -> Result:
        line = "─" * 48
        print(f"\n{line}\n▶ {message.title}\n{line}\n{message.body}\n")
        if message.click_url:
            print(f"🔗 {message.click_url}\n")
        return Result("console", True)

    def _send_ntfy(self, message: Message) -> Result:
        topic = (self.config.get("notify", "ntfy", "topic", default="") or "").strip()
        if not topic:
            return Result("ntfy", False, "topic 이 비어 있습니다 (A3_NTFY_TOPIC).")
        server = (
            self.config.get("notify", "ntfy", "server", default="https://ntfy.sh")
            or "https://ntfy.sh"
        ).rstrip("/")

        headers: dict[str, str] = {
            # 헤더에는 ASCII 만 들어갈 수 있어 제목은 RFC 2047 대신 URL 인코딩 후
            # ntfy 의 X-Title 대신 JSON 본문을 쓴다. (아래 payload 참고)
            "Content-Type": "application/json",
        }
        token = self.config.secret("ntfy_token")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        # 메시지가 따로 지정하지 않았으면(= "default") 설정값을 쓴다.
        priority = message.priority
        if priority == "default":
            priority = self.config.get("notify", "ntfy", "priority", default="default")
        payload: dict[str, Any] = {
            "topic": topic,
            "title": truncate(message.title, 120),
            "message": message.body[:NTFY_BODY_LIMIT],
            "priority": PRIORITY_MAP.get(priority, 3),
            "markdown": True,
        }
        if message.tags:
            payload["tags"] = message.tags
        if message.click_url:
            payload["click"] = message.click_url

        resp = self.session.post(server, data=json.dumps(payload).encode("utf-8"),
                                 headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        return Result("ntfy", True, f"{server}/{topic}")

    def _send_telegram(self, message: Message) -> Result:
        token = self.config.secret("telegram_token")
        chat_id = (self.config.get("notify", "telegram", "chat_id", default="") or "").strip()
        if not token or not chat_id:
            return Result("telegram", False, "토큰 또는 chat_id 가 없습니다.")
        text = f"*{_md_escape(message.title)}*\n\n{message.body}"[:TELEGRAM_LIMIT]
        resp = self.session.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            },
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        return Result("telegram", True)

    def _send_discord(self, message: Message) -> Result:
        url = (self.config.get("notify", "discord", "webhook_url", default="") or "").strip()
        if not url:
            return Result("discord", False, "webhook_url 이 없습니다.")
        content = f"**{message.title}**\n{message.body}"[:DISCORD_LIMIT]
        resp = self.session.post(url, json={"content": content}, timeout=TIMEOUT)
        resp.raise_for_status()
        return Result("discord", True)


def _md_escape(text: str) -> str:
    for ch in ("_", "*", "[", "]", "`"):
        text = text.replace(ch, "\\" + ch)
    return text


def ntfy_subscribe_url(server: str, topic: str) -> str:
    return f"{server.rstrip('/')}/{urllib.parse.quote(topic)}"
