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


WORD_CARDS = [c for c in ENGLISH["cards"] if c.get("kind", "word") != "speaking"]
SPEAKING_CARDS = [c for c in ENGLISH["cards"] if c.get("kind") == "speaking"]


def test_english_deck_size_and_unique_ids():
    cards = ENGLISH["cards"]
    assert len(cards) == 134
    assert len({c["id"] for c in cards}) == 134


def test_deck_has_both_card_kinds():
    """오픽은 말하기 시험이다. 말하기 카드가 사라지면 이 덱은 의미가 없다."""
    assert len(SPEAKING_CARDS) >= 50
    assert len(WORD_CARDS) >= 50


@pytest.mark.parametrize("card", WORD_CARDS, ids=lambda c: c["id"])
def test_every_word_card_is_complete(card):
    for field in ("front", "back", "ex", "tag"):
        assert str(card.get(field, "")).strip(), f"{card['id']}: {field} 누락"
    assert card["tag"] in ENGLISH["meta"]["tags"]


@pytest.mark.parametrize("card", SPEAKING_CARDS, ids=lambda c: c["id"])
def test_every_speaking_card_is_complete(card):
    for field in ("q", "ko", "tip", "tag"):
        assert str(card.get(field, "")).strip(), f"{card['id']}: {field} 누락"
    assert card["tag"] in ENGLISH["meta"]["tags"]
    assert len(card.get("structure", [])) >= 3, "답변 뼈대가 3단계 미만이면 훈련이 안 된다"
    assert len(card.get("phrases", [])) >= 3, "쓸 표현이 3개 미만이면 말할 재료가 없다"
    assert 45 <= int(card.get("seconds", 0)) <= 120, "오픽 답변 길이는 45~120초"


def test_opic_covers_every_question_type():
    """한 유형이라도 빠지면 시험장에서 그 문항에 무너진다."""
    required = {
        "오픽-자기소개", "오픽-직업", "오픽-묘사", "오픽-습관",
        "오픽-경험", "오픽-비교", "오픽-롤플레이", "오픽-돌발",
    }
    assert required <= {c["tag"] for c in SPEAKING_CARDS}


def test_missing_deck_raises():
    with pytest.raises(FileNotFoundError):
        load_deck("does_not_exist.yaml")
