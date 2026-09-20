import datetime as dt

import pytest

from a3 import srs

TODAY = dt.date(2026, 9, 20)


def test_new_card_is_due_today():
    card = srs.new_card("x", TODAY)
    assert srs.is_due(card, TODAY)
    assert card["reps"] == 0


def test_successful_reviews_lengthen_interval():
    card = srs.new_card("x", TODAY)
    intervals = []
    for _ in range(4):
        card = srs.review(card, 5, TODAY)
        intervals.append(card["interval"])
    assert intervals == sorted(intervals)
    assert intervals[0] == 1 and intervals[1] == 6
    assert intervals[-1] > intervals[1]


def test_failure_resets_and_counts_lapse():
    card = srs.new_card("x", TODAY)
    card = srs.review(card, 5, TODAY)
    card = srs.review(card, 5, TODAY)
    card = srs.review(card, 1, TODAY)
    assert card["reps"] == 0
    assert card["interval"] == 1
    assert card["lapses"] == 1


def test_ease_never_below_floor():
    card = srs.new_card("x", TODAY)
    for _ in range(20):
        card = srs.review(card, 3, TODAY)
    assert card["ease"] >= srs.MIN_EASE


def test_review_does_not_mutate_input():
    card = srs.new_card("x", TODAY)
    snapshot = dict(card)
    srs.review(card, 5, TODAY)
    assert card == snapshot


def test_invalid_quality_rejected():
    with pytest.raises(ValueError):
        srs.review(srs.new_card("x", TODAY), 9, TODAY)


def _graded(due_offset: int) -> dict:
    return {"due": (TODAY + dt.timedelta(days=due_offset)).isoformat(), "reps": 2, "last": "2026-09-01"}


def test_pick_due_prefers_most_overdue_review():
    items = [{"id": str(i)} for i in range(5)]
    cards = {"0": _graded(-1), "1": _graded(-10), "2": _graded(5)}
    picked = srs.pick_due(items, cards, TODAY, 2)
    assert [p["id"] for p in picked] == ["1", "0"]


def test_graded_reviews_outrank_new_cards():
    items = [{"id": str(i)} for i in range(10)]
    picked = srs.pick_due(items, {"7": _graded(-1)}, TODAY, 3)
    assert picked[0]["id"] == "7"


def test_new_cards_outrank_ungraded_reserves():
    """채점하지 않은 카드가 새 카드를 밀어내면 덱을 영영 다 못 돈다."""
    items = [{"id": str(i)} for i in range(10)]
    cards = {"0": srs.new_card("0", TODAY), "1": srs.new_card("1", TODAY)}
    for c in cards.values():
        c["served"] = TODAY.isoformat()
    picked = [p["id"] for p in srs.pick_due(items, cards, TODAY, 3)]
    assert "0" not in picked and "1" not in picked


def test_ungraded_reserves_return_once_the_deck_is_exhausted():
    items = [{"id": "0"}, {"id": "1"}]
    cards = {"0": srs.new_card("0", TODAY), "1": srs.new_card("1", TODAY)}
    picked = [p["id"] for p in srs.pick_due(items, cards, TODAY, 2)]
    assert sorted(picked) == ["0", "1"]


def test_pick_due_falls_back_to_fresh_cards():
    items = [{"id": str(i)} for i in range(5)]
    cards = {"0": {"due": (TODAY + dt.timedelta(days=5)).isoformat()}}
    picked = srs.pick_due(items, cards, TODAY, 3)
    assert len(picked) == 3
    assert "0" not in [p["id"] for p in picked]


def test_pick_due_is_stable_within_a_day():
    items = [{"id": str(i)} for i in range(50)]
    a = srs.pick_due(items, {}, TODAY, 5)
    b = srs.pick_due(items, {}, TODAY, 5)
    assert a == b


def test_mark_served_defers_ungraded_cards():
    """채점을 건너뛰어도 같은 카드가 내일 또 뽑히면 안 된다."""
    cards: dict = {}
    srs.mark_served(cards, "x", TODAY)
    card = cards["x"]
    assert card["served"] == TODAY.isoformat()
    assert not srs.is_due(card, TODAY + dt.timedelta(days=1))
    assert srs.is_due(card, TODAY + dt.timedelta(days=srs.SERVE_RESERVE_DAYS))


def test_mark_served_does_not_push_future_cards_further_out():
    future = (TODAY + dt.timedelta(days=30)).isoformat()
    cards = {"x": {"id": "x", "due": future}}
    srs.mark_served(cards, "x", TODAY)
    assert cards["x"]["due"] == future


def test_grading_overrides_the_serve_deferral():
    cards: dict = {}
    srs.mark_served(cards, "x", TODAY)
    graded = srs.review(cards["x"], 5, TODAY)
    assert graded["due"] == (TODAY + dt.timedelta(days=1)).isoformat()
