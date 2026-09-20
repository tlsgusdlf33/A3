"""덱은 이 프로그램의 실제 알맹이다. 구조가 깨지면 매일 아침 알림이 망가진다."""

import pytest

from a3.tasks.decks import load_deck

EXAM = load_deck("exam_deck.yaml")
ENGLISH = load_deck("english_deck.yaml")


def test_exam_deck_size_and_unique_ids():
    cards = EXAM["cards"]
    assert len(cards) == 120
    assert len({c["id"] for c in cards}) == 120


@pytest.mark.parametrize("card", EXAM["cards"], ids=lambda c: c["id"])
def test_every_exam_card_is_complete(card):
    assert card["q"].strip()
    assert card["type"] in ("용어형", "서술형")
    assert len(card.get("keywords", [])) >= 3, "채점 키워드가 3개 미만이면 훈련 가치가 없다"
    frame_key = card.get("frame_as") or card["category"]
    assert frame_key in EXAM["frames"], f"{frame_key} 에 대한 답안 전개 틀이 없다"


def test_every_frame_is_used():
    used = {c.get("frame_as") or c["category"] for c in EXAM["cards"]}
    assert set(EXAM["frames"]) == used


def test_english_deck_size_and_unique_ids():
    cards = ENGLISH["cards"]
    assert len(cards) == 110
    assert len({c["id"] for c in cards}) == 110


@pytest.mark.parametrize("card", ENGLISH["cards"], ids=lambda c: c["id"])
def test_every_english_card_is_complete(card):
    for field in ("front", "back", "ex", "tag"):
        assert str(card.get(field, "")).strip(), f"{card['id']}: {field} 누락"
    assert card["tag"] in ENGLISH["meta"]["tags"]


def test_missing_deck_raises():
    with pytest.raises(FileNotFoundError):
        load_deck("does_not_exist.yaml")
