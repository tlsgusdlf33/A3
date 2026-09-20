"""기회/동향 레이더.

구글 뉴스 RSS + 임의 RSS 를 긁어 키워드 점수를 매기고, 처음 보는 항목만 알린다.
API 키가 필요 없고 막히지 않는 경로만 쓴다.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import logging
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass

import requests

from a3 import util
from a3.config import Config
from a3.notify import Message
from a3.store import Store
from a3.tasks import TaskResult, register

log = logging.getLogger(__name__)

TIMEOUT = 20
SEEN_NS = "radar"
USER_AGENT = "a3-personal-assistant/0.1 (+https://github.com/tlsgusdlf33/A3)"
GOOGLE_NEWS = "https://news.google.com/rss/search"


@dataclass
class Item:
    title: str
    link: str
    source: str
    published: dt.date | None
    score: int = 0

    @property
    def key(self) -> str:
        # 링크는 리다이렉트 파라미터가 붙어 달라질 수 있어 제목도 섞는다.
        base = f"{self.title.strip().lower()}|{urllib.parse.urlsplit(self.link).path}"
        return hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]


def google_news_url(query: str, when_days: int = 0) -> str:
    """구글 뉴스 검색 RSS.

    검색 RSS 는 최신순이 아니라 관련도순이라 오래된 기사가 섞여 온다.
    `when:Nd` 연산자로 피드 단계에서 기간을 잘라야 실제로 새 소식만 남는다.
    """
    q = f"{query} when:{when_days}d" if when_days > 0 else query
    params = urllib.parse.urlencode({"q": q, "hl": "ko", "gl": "KR", "ceid": "KR:ko"})
    return f"{GOOGLE_NEWS}?{params}"


def _parse_date(text: str | None) -> dt.date | None:
    if not text:
        return None
    from email.utils import parsedate_to_datetime

    try:
        return parsedate_to_datetime(text).date()
    except (TypeError, ValueError):
        pass
    try:  # Atom: 2026-09-20T01:02:03Z
        return dt.datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def parse_feed(xml_text: str, fallback_source: str) -> list[Item]:
    """RSS 2.0 과 Atom 을 모두 받는다."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        log.warning("피드 파싱 실패 (%s): %s", fallback_source, exc)
        return []

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    items: list[Item] = []

    for node in root.iter():
        tag = node.tag.split("}")[-1]
        if tag not in ("item", "entry"):
            continue
        title = util.strip_html(_text(node, ("title",), ns))
        link = _text(node, ("link",), ns)
        if not link:
            link_el = node.find("atom:link", ns)
            if link_el is not None:
                link = link_el.get("href", "")
        source = util.strip_html(_text(node, ("source",), ns)) or fallback_source
        published = _parse_date(
            _text(node, ("pubDate",), ns) or _text(node, ("published", "updated"), ns)
        )
        if title:
            items.append(Item(title=title, link=link.strip(), source=source, published=published))
    return items


def _text(node: ET.Element, tags: tuple[str, ...], ns: dict) -> str:
    for tag in tags:
        for child in node:
            if child.tag.split("}")[-1] == tag and (child.text or "").strip():
                return child.text.strip()
    return ""


def score_item(item: Item, keywords: dict[str, int], exclude: list[str]) -> int:
    haystack = f"{item.title} {item.source}".lower()
    for bad in exclude:
        if bad.lower() in haystack:
            return -1
    return sum(weight for word, weight in keywords.items() if word.lower() in haystack)


@register("radar", "부업/기술동향 레이더 — 새 소식만 골라 알림")
def run(config: Config, store: Store) -> TaskResult:
    cfg = config.get("radar", default={}) or {}
    lookback = int(cfg.get("lookback_days", 7))
    queries = list(cfg.get("google_news_queries", []))
    feeds = [(google_news_url(q, lookback), q) for q in queries]
    feeds += [(url, url) for url in cfg.get("feeds", [])]
    if not feeds:
        return TaskResult("radar", None, "설정된 피드가 없습니다.")

    keywords = dict(cfg.get("keywords", {}))
    exclude = list(cfg.get("exclude", []))
    min_score = int(cfg.get("min_score", 1))
    max_items = int(cfg.get("max_items", 6))

    today = util.today()
    cutoff = today - dt.timedelta(days=lookback)
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    collected: dict[str, Item] = {}
    failures: list[str] = []

    for url, label in feeds:
        try:
            resp = session.get(url, timeout=TIMEOUT)
            resp.raise_for_status()
        except requests.RequestException as exc:
            log.warning("피드 실패 %s: %s", label, exc)
            failures.append(label)
            continue
        for item in parse_feed(resp.text, label):
            if item.published and item.published < cutoff:
                continue
            if store.is_seen(SEEN_NS, item.key):
                continue
            item.score = score_item(item, keywords, exclude)
            if item.score < min_score:
                continue
            prior = collected.get(item.key)
            if prior is None or item.score > prior.score:
                collected[item.key] = item

    ranked = sorted(collected.values(), key=lambda i: (-i.score, i.title))[:max_items]

    if not ranked:
        detail = f" (피드 {len(failures)}개 실패)" if failures else ""
        summary = f"새 항목 없음{detail}"
        body = f"오늘 새로 걸린 소식이 없습니다.{detail}"
        return TaskResult("radar", Message("📡 레이더", body, tags=["satellite"]), summary)

    lines = [f"키워드에 걸린 새 소식 {len(ranked)}건", ""]
    for i, item in enumerate(ranked, 1):
        when = item.published.isoformat() if item.published else "날짜미상"
        lines.append(f"{i}. [{item.score}점] {util.truncate(item.title, 90)}")
        lines.append(f"   {item.source} · {when}")
        if item.link:
            lines.append(f"   {item.link}")
        lines.append("")
    if failures:
        lines.append(f"⚠️ 가져오지 못한 피드: {', '.join(failures[:3])}")
    body = "\n".join(lines).rstrip()

    for item in ranked:
        store.mark_seen(SEEN_NS, item.key, today.isoformat())
    # 점수 미달로 버린 것도 다시 보지 않도록 기록한다.
    for key in collected:
        store.mark_seen(SEEN_NS, key, today.isoformat())

    return TaskResult(
        "radar",
        Message("📡 레이더", body, tags=["satellite"], click_url=ranked[0].link),
        f"신규 {len(ranked)}건",
        changed=True,
    )
