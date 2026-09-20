"""모범답안은 '외워서 쓸 수 있는가'가 전부다. 분량과 도표 유무를 기계가 지킨다."""

import re

import pytest

from a3 import answers
from a3.tasks.decks import load_deck

EXAM = load_deck("exam_deck.yaml")
CARDS = {str(c["id"]): c for c in EXAM["cards"]}
WRITTEN = sorted(answers.available())


def test_at_least_one_answer_exists():
    assert WRITTEN, "모범답안이 한 편도 없다"


@pytest.mark.parametrize("cid", WRITTEN)
def test_answer_belongs_to_a_real_question(cid):
    assert cid in CARDS, f"{cid}번 문항이 덱에 없는데 답안만 있다"


@pytest.mark.parametrize("cid", WRITTEN)
def test_answer_metadata_matches_the_card(cid):
    a = answers.load(cid)
    card = CARDS[cid]
    assert a.kind.startswith(card["type"]), f"{cid}: 유형 불일치 ({a.kind} vs {card['type']})"
    assert a.category == card["category"], f"{cid}: 분야 불일치"


@pytest.mark.parametrize("cid", WRITTEN)
def test_answer_length_fits_a4_target(cid):
    """서술형은 A4 3~4장, 용어형은 1장. 분량이 안 맞으면 실전에서 못 쓴다."""
    a = answers.load(cid)
    lo, hi = a.target
    assert lo <= a.pages <= hi, f"{cid}: A4 {a.pages}장 — 목표 {lo}~{hi}장을 벗어남"


@pytest.mark.parametrize("cid", WRITTEN)
def test_answer_has_tables_and_figures(cid):
    """기술사 답안은 도표와 도해가 점수다. 줄글만 있으면 반쪽이다."""
    a = answers.load(cid)
    assert a.tables >= 3, f"{cid}: 표가 {a.tables}개뿐"
    assert a.figures >= 2, f"{cid}: 도해가 {a.figures}개뿐"


@pytest.mark.parametrize("cid", WRITTEN)
def test_answer_has_the_standard_section_structure(cid):
    """개요로 열고 결론으로 닫는 구조가 기술사 답안의 채점 기준이다."""
    a = answers.load(cid)
    heads = re.findall(r"^##\s+([IVX]+)\.\s*(.+?)\s*$", a.body, re.MULTILINE)
    assert len(heads) >= 4, f"{cid}: 대단원이 {len(heads)}개뿐"
    assert "개요" in heads[0][1], f"{cid}: 첫 장이 개요가 아니다 ({heads[0][1]})"
    assert "결론" in heads[-1][1], f"{cid}: 마지막 장이 결론이 아니다 ({heads[-1][1]})"
    numerals = [h[0] for h in heads]
    assert numerals == ["I", "II", "III", "IV", "V", "VI"][: len(numerals)], \
        f"{cid}: 대단원 번호가 순서대로가 아니다 — {numerals}"


def test_missing_answer_returns_none_not_error():
    assert answers.load("999") is None


def test_count_lines_measures_wrapping_and_width():
    assert answers.count_lines("") == 0  # 빈 내용은 지면을 차지하지 않는다
    assert answers.count_lines("짧은 줄") == 1
    # 한글은 두 칸으로 세므로 46자면 92폭 → 90폭 한 줄을 넘겨 두 줄
    assert answers.count_lines("가" * 46) == 2
    assert answers.count_lines("a\nb\n\nc") == 4


def test_page_target_differs_by_question_type():
    assert answers.PAGE_TARGET["용어형"][1] < answers.PAGE_TARGET["서술형"][0]
