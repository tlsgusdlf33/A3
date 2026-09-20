"""OPIc 일일 훈련 + 실무 영어.

오픽은 말하기 시험이라 카드를 눈으로 읽는 것만으로는 점수가 오르지 않는다.
그래서 카드를 두 종류로 나눠 매일 다른 방식으로 낸다.
  - speaking: 질문을 던지고 제한시간 동안 실제로 소리 내어 말하게 한다.
              답변 뼈대와 쓸 표현은 말한 뒤에 확인한다.
  - word:     표현 암기. 실무 어휘가 여기 들어간다.
두 종류는 각자 quota 를 갖는다. 말하기가 어휘에 밀려 사라지면 안 되기 때문이다.
"""

from __future__ import annotations

from a3 import srs, util
from a3.config import Config
from a3.notify import Message
from a3.store import Store
from a3.tasks import TaskResult, register
from a3.tasks.decks import load_deck

DECK = "english_deck.yaml"
DECK_KEY = "english"


def _render_speaking(card: dict, index: int) -> list[str]:
    lines = [
        f"{index}. 🎤 {card['q']}",
        f"   ({card['ko']})",
        f"   ⏱ {card.get('seconds', 90)}초 — 먼저 소리 내어 말한 뒤 아래를 보세요.",
        "   ── 뼈대 ──",
    ]
    lines += [f"   {i}) {step}" for i, step in enumerate(card.get("structure", []), 1)]
    lines.append("   ── 쓸 표현 ──")
    lines += [f"   · {p}" for p in card.get("phrases", [])]
    if card.get("tip"):
        lines.append(f"   💡 {card['tip']}")
    lines.append(f"   [{card['tag']} · {card['id']}]")
    return lines


def _render_word(card: dict, index: int) -> list[str]:
    lines = [f"{index}. {card['front']}", f"   → {card['back']}"]
    if card.get("ex"):
        lines.append(f"   ▸ {card['ex']}")
    lines.append(f"   [{card['tag']} · {card['id']}]")
    return lines


def _pick(cards: list[dict], state: dict, today, limit: int) -> list[dict]:
    if limit <= 0 or not cards:
        return []
    return srs.pick_due(cards, state, today, limit)


@register("english", "OPIc 말하기 훈련 + 실무 영어 표현 (간격 반복)")
def run(config: Config, store: Store) -> TaskResult:
    deck = load_deck(DECK)
    cards = deck["cards"]

    tags = config.get("english", "tags", default=[]) or []
    if tags:
        cards = [c for c in cards if c["tag"] in tags]
        if not cards:
            raise ValueError(f"english.tags 에 해당하는 카드가 없습니다: {tags}")

    speaking = [c for c in cards if c.get("kind") == "speaking"]
    words = [c for c in cards if c.get("kind", "word") != "speaking"]

    today = util.today()
    state = store.deck(DECK_KEY)
    picked_speaking = _pick(
        speaking, state, today, int(config.get("english", "speaking_cards", default=2))
    )
    picked_words = _pick(
        words, state, today, int(config.get("english", "word_cards", default=5))
    )
    picked = picked_speaking + picked_words

    name = config.get("english", "name", default="영어")
    head = f"🗣️ 오늘의 {name}"
    raw_date = config.get("english", "date", default="")
    exam_date = util.parse_date(raw_date) if raw_date else None
    if exam_date:
        head += f" {util.dday_label(exam_date)}"

    if not picked:
        body = "오늘 예정된 복습 카드가 없습니다. 👍"
        return TaskResult("english", Message(head, body, tags=["speaking_head"]), "due 카드 없음")

    target = config.get("english", "target_level", default="")
    intro = f"누적 학습 {len(state)}/{len(cards)}장"
    if target:
        intro += f" · 목표 {target}"
    lines = [intro, ""]

    index = 0
    if picked_speaking:
        lines.append("━━ 말하기 (입으로 소리 내기) ━━")
        for card in picked_speaking:
            index += 1
            lines += _render_speaking(card, index)
            lines.append("")
    if picked_words:
        lines.append("━━ 표현 ━━")
        for card in picked_words:
            index += 1
            lines += _render_word(card, index)
            lines.append("")
    lines.append("✍️ `a3 grade english <id> <0-5>` 로 기억한 정도를 기록하세요.")
    body = "\n".join(lines)

    for card in picked:
        srs.mark_served(state, str(card["id"]), today)

    summary = f"말하기 {len(picked_speaking)} · 표현 {len(picked_words)}"
    return TaskResult(
        "english",
        Message(head, body, tags=["speaking_head"]),
        summary,
        changed=True,
        extras={"ids": [str(c["id"]) for c in picked]},
    )
