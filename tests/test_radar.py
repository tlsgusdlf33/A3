import datetime as dt

from a3.tasks.radar import Item, google_news_url, parse_feed, score_item

RSS = """<?xml version="1.0"?>
<rss version="2.0"><channel>
<item><title>건설기계 배출가스 규제 개정 - 뉴스A</title><link>https://ex.com/a?utm=1</link>
<pubDate>Fri, 18 Sep 2026 10:00:00 GMT</pubDate><source url="https://a">뉴스A</source></item>
<item><title>채용공고: 정비기사 모집</title><link>https://ex.com/b</link>
<pubDate>Fri, 18 Sep 2026 11:00:00 GMT</pubDate><source url="https://b">뉴스B</source></item>
</channel></rss>"""

ATOM = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
<entry><title>유압 펌프 신기술</title><link href="https://ex.com/c"/>
<updated>2026-09-19T08:00:00Z</updated></entry>
</feed>"""


def test_parses_rss():
    items = parse_feed(RSS, "fallback")
    assert len(items) == 2
    assert items[0].title == "건설기계 배출가스 규제 개정 - 뉴스A"
    assert items[0].published == dt.date(2026, 9, 18)
    assert items[0].source == "뉴스A"


def test_parses_atom_with_href_link():
    items = parse_feed(ATOM, "fallback")
    assert len(items) == 1
    assert items[0].link == "https://ex.com/c"
    assert items[0].published == dt.date(2026, 9, 19)
    assert items[0].source == "fallback"


def test_malformed_xml_returns_empty_instead_of_raising():
    assert parse_feed("<rss><channel><item>", "x") == []


def test_score_uses_weights():
    item = Item("건설기계 유압 규제", "", "", None)
    assert score_item(item, {"건설기계": 2, "유압": 2, "규제": 1}, []) == 5


def test_excluded_words_disqualify():
    item = Item("채용공고: 정비기사 모집", "", "", None)
    assert score_item(item, {"정비": 5}, ["채용공고"]) == -1


def test_key_ignores_query_string_differences():
    a = Item("같은 기사", "https://ex.com/x?utm_source=a", "", None)
    b = Item("같은 기사", "https://ex.com/x?utm_source=b", "", None)
    assert a.key == b.key


def test_google_news_url_adds_recency_window():
    url = google_news_url("건설기계", when_days=7)
    assert "when%3A7d" in url or "when:7d" in url
    assert "hl=ko" in url and "ceid=KR%3Ako" in url


def test_google_news_url_without_window():
    assert "when" not in google_news_url("건설기계", 0)
