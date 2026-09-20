"""태스크를 실제로 돌려 본다 (네트워크는 타지 않는 것들만)."""

import copy

import pytest

from a3 import tasks
from a3.config import DEFAULTS, Config
from a3.store import Store

tasks.load_all()


@pytest.fixture
def config():
    data = copy.deepcopy(DEFAULTS)
    data["notify"]["channels"] = []
    data["brief"]["weather"] = False
    return Config(data)


@pytest.fixture
def store(tmp_path):
    return Store(tmp_path / "s.json")


def test_exam_serves_requested_number(config, store):
    config.data["exam"]["daily_cards"] = 3
    result = tasks.get("exam")(config, store)
    assert len(result.extras["ids"]) == 3
    assert "건설기계기술사" in result.message.body
    assert "D-" in result.message.title or "D-DAY" in result.message.title


def test_exam_does_not_repeat_the_same_cards_next_day(config, store, monkeypatch):
    import datetime as dt

    from a3.tasks import exam as exam_mod

    day1 = tasks.get("exam")(config, store).extras["ids"]
    monkeypatch.setattr(exam_mod.util, "today", lambda: dt.date(2026, 9, 21))
    day2 = tasks.get("exam")(config, store).extras["ids"]
    assert not set(day1) & set(day2)


def test_exam_category_filter(config, store):
    config.data["exam"]["categories"] = ["유압 시스템"]
    config.data["exam"]["daily_cards"] = 5
    result = tasks.get("exam")(config, store)
    assert all(i.startswith("01") or i.startswith("02") for i in result.extras["ids"])


def test_exam_rejects_unknown_category(config, store):
    config.data["exam"]["categories"] = ["존재하지 않는 분야"]
    with pytest.raises(ValueError):
        tasks.get("exam")(config, store)


def test_exam_without_date_still_works(config, store):
    config.data["exam"]["date"] = ""
    result = tasks.get("exam")(config, store)
    assert "시험일 미설정" in result.message.body


def test_exam_flags_provisional_date(config, store):
    result = tasks.get("exam")(config, store)
    assert "추정" in result.message.body


def test_english_serves_both_kinds_by_their_own_quota(config, store):
    config.data["english"]["speaking_cards"] = 2
    config.data["english"]["word_cards"] = 5
    result = tasks.get("english")(config, store)
    assert len(result.extras["ids"]) == 7
    assert len(store.deck("english")) == 7
    assert "말하기 2" in result.summary and "표현 5" in result.summary


def test_speaking_cards_are_never_crowded_out_by_words(config, store):
    """섞어서 뽑으면 표현 카드가 말하기를 밀어낸다. 오픽에서는 치명적이다."""
    config.data["english"]["speaking_cards"] = 2
    config.data["english"]["word_cards"] = 20
    body = tasks.get("english")(config, store).message.body
    assert body.count("🎤") == 2


def test_speaking_card_tells_you_to_speak_before_reading(config, store):
    config.data["english"]["speaking_cards"] = 1
    config.data["english"]["word_cards"] = 0
    body = tasks.get("english")(config, store).message.body
    assert "소리 내어" in body
    assert "뼈대" in body and "쓸 표현" in body


def test_english_tag_filter(config, store):
    config.data["english"]["tags"] = ["실무-도장"]
    result = tasks.get("english")(config, store)
    assert result.extras["ids"]


def test_english_tag_filter_can_isolate_roleplay(config, store):
    """롤플레이만 집중 훈련하고 싶을 때."""
    config.data["english"]["tags"] = ["오픽-롤플레이"]
    config.data["english"]["speaking_cards"] = 3
    config.data["english"]["word_cards"] = 5
    result = tasks.get("english")(config, store)
    assert len(result.extras["ids"]) == 3  # word 카드가 없는 태그
    assert all(i.startswith("o") for i in result.extras["ids"])


def test_brief_reports_progress(config, store):
    tasks.get("exam")(config, store)
    result = tasks.get("brief")(config, store)
    body = result.message.body
    assert "오늘의 학습량" in body
    assert "기술사" in body and "영어" in body


def test_brief_survives_weather_failure(config, store, monkeypatch):
    import requests

    from a3.tasks import brief as brief_mod

    config.data["brief"]["weather"] = True

    def boom(*a, **k):
        raise requests.RequestException("no network")

    monkeypatch.setattr(brief_mod.requests, "get", boom)
    result = tasks.get("brief")(config, store)
    assert result.message is not None


def test_radar_with_no_feeds_is_a_noop(config, store):
    config.data["radar"]["google_news_queries"] = []
    config.data["radar"]["feeds"] = []
    result = tasks.get("radar")(config, store)
    assert result.message is None


def test_selfupdate_outside_a_repo(config, store, monkeypatch, tmp_path):
    from a3.tasks import selfupdate as su

    monkeypatch.setattr(su, "REPO_ROOT", tmp_path)
    result = tasks.get("selfupdate")(config, store)
    assert "git 저장소" in result.message.body


def test_all_registered_tasks_have_help():
    assert set(tasks.names()) == {"exam", "english", "radar", "brief", "selfupdate"}
    assert all(tasks.help_text(n) for n in tasks.names())


def test_deck_progresses_even_if_the_user_never_grades(config, store, monkeypatch):
    """채점을 한 번도 안 해도 30일이면 새 문항을 계속 만나야 한다."""
    import datetime as dt

    from a3.tasks import exam as exam_mod

    config.data["exam"]["daily_cards"] = 3
    seen: set[str] = set()
    for i in range(30):
        day = dt.date(2026, 9, 20) + dt.timedelta(days=i)
        monkeypatch.setattr(exam_mod.util, "today", lambda d=day: d)
        seen |= set(tasks.get("exam")(config, store).extras["ids"])
    assert len(seen) == 90, f"30일 x 3문제인데 {len(seen)}문항만 접함"


def test_english_deck_is_fully_covered_in_two_months(config, store, monkeypatch):
    """시험 전까지 덱을 한 바퀴는 돌아야 한다."""
    import datetime as dt

    from a3.tasks import english as english_mod

    config.data["english"]["speaking_cards"] = 2
    config.data["english"]["word_cards"] = 5
    for i in range(60):
        day = dt.date(2026, 9, 20) + dt.timedelta(days=i)
        monkeypatch.setattr(english_mod.util, "today", lambda d=day: d)
        tasks.get("english")(config, store)
    from a3.tasks.decks import load_deck

    assert len(store.deck("english")) == len(load_deck("english_deck.yaml")["cards"])


def test_english_notification_fits_in_a_push_message(config, store, monkeypatch):
    """ntfy 본문 한도(3500자)를 넘으면 뒷부분이 잘려 나간다."""
    import datetime as dt

    from a3.notify import NTFY_BODY_LIMIT
    from a3.tasks import english as english_mod

    for i in range(60):
        day = dt.date(2026, 9, 20) + dt.timedelta(days=i)
        monkeypatch.setattr(english_mod.util, "today", lambda d=day: d)
        result = tasks.get("english")(config, store)
        assert len(result.message.body) < NTFY_BODY_LIMIT
