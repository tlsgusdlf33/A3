import json

import pytest
import requests

from a3.config import Config, DEFAULTS
from a3.notify import Message, Notifier


class FakeResponse:
    def __init__(self, status=200):
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code}")


class FakeSession:
    def __init__(self, status=200):
        self.calls = []
        self.status = status

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return FakeResponse(self.status)


def make_config(**notify):
    import copy

    data = copy.deepcopy(DEFAULTS)
    data["notify"].update(notify)
    return Config(data)


def test_ntfy_sends_json_payload_with_korean_title():
    cfg = make_config(channels=["ntfy"], ntfy={"server": "https://ntfy.sh", "topic": "t1", "priority": "high"})
    session = FakeSession()
    results = Notifier(cfg, session).send(Message("한글 제목", "본문", tags=["bell"]))
    assert results[0].ok
    url, kwargs = session.calls[0]
    payload = json.loads(kwargs["data"].decode("utf-8"))
    assert url == "https://ntfy.sh"
    assert payload["topic"] == "t1"
    assert payload["title"] == "한글 제목"  # 헤더가 아닌 JSON 이라 한글이 살아 있어야 한다
    assert payload["priority"] == 4
    assert payload["tags"] == ["bell"]


def test_ntfy_without_topic_fails_clearly():
    cfg = make_config(channels=["ntfy"], ntfy={"server": "https://ntfy.sh", "topic": ""})
    result = Notifier(cfg, FakeSession()).send(Message("t", "b"))[0]
    assert not result.ok and "topic" in result.detail


def test_long_body_is_truncated_for_ntfy():
    cfg = make_config(channels=["ntfy"], ntfy={"server": "https://ntfy.sh", "topic": "t"})
    session = FakeSession()
    Notifier(cfg, session).send(Message("t", "가" * 9000))
    payload = json.loads(session.calls[0][1]["data"].decode("utf-8"))
    assert len(payload["message"]) <= 3500


def test_one_failing_channel_does_not_stop_the_others():
    cfg = make_config(channels=["ntfy", "console"], ntfy={"server": "https://ntfy.sh", "topic": "t"})
    session = FakeSession(status=500)
    results = Notifier(cfg, session).send(Message("t", "b"))
    assert [r.ok for r in results] == [False, True]


def test_unknown_channel_is_reported():
    cfg = make_config(channels=["carrier-pigeon"])
    result = Notifier(cfg, FakeSession()).send(Message("t", "b"))[0]
    assert not result.ok


def test_dry_run_skips_network():
    cfg = make_config(channels=["ntfy"], dry_run=True, ntfy={"server": "https://ntfy.sh", "topic": "t"})
    session = FakeSession()
    result = Notifier(cfg, session).send(Message("t", "b"))[0]
    assert result.ok and session.calls == []


def test_telegram_requires_token(monkeypatch):
    monkeypatch.delenv("A3_TELEGRAM_TOKEN", raising=False)
    cfg = make_config(channels=["telegram"], telegram={"chat_id": "123"})
    result = Notifier(cfg, FakeSession()).send(Message("t", "b"))[0]
    assert not result.ok
