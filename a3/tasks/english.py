"""영어 일일 훈련 — 실무 표현 + 시험 어휘를 간격 반복으로."""

from __future__ import annotations

from a3 import srs, util
from a3.config import Config
from a3.notify import Message
from a3.store import Store
from a3.tasks import TaskResult, register
from a3.tasks.decks import load_deck

DECK = "english_deck.yaml"
DECK_KEY = "english"


@register("english", "영어 일일 표현/어휘 훈련 (간격 반복)")
def run(config: Config, store: Store) -> TaskResult:
    deck = load_deck(DECK)
    cards = deck["cards"]
    tags = config.get("english", "tags", default=[]) or []
    if tags:
        cards = [c for c in cards if c["tag"] in tags]
        if not cards:
            raise ValueError(f"english.tags 에 해당하는 카드가 없습니다: {tags}")

    limit = int(config.get("english", "daily_cards", default=7))
    today = util.today()
    state = store.deck(DECK_KEY)
    picked = srs.pick_due(cards, state, today, limit)

    head = "🗣️ 오늘의 영어"
    raw_date = config.get("english", "date", default="")
    exam_date = util.parse_date(raw_date) if raw_date else None
    if exam_date:
        head += f" · {config.get('english', 'name', default='영어 시험')} {util.dday_label(exam_date)}"

    if not picked:
        body = "오늘 예정된 복습 카드가 없습니다. 👍"
        return TaskResult("english", Message(head, body, tags=["speaking_head"]), "due 카드 없음")

    lines = [f"누적 학습 {len(state)}/{len(cards)}장", ""]
    for i, card in enumerate(picked, 1):
        lines.append(f"{i}. {card['front']}")
        lines.append(f"   → {card['back']}")
        if card.get("ex"):
            lines.append(f"   ▸ {card['ex']}")
        lines.append(f"   [{card['tag']} · {card['id']}]")
        lines.append("")
    lines.append("✍️ `a3 grade english <id> <0-5>` 로 기억한 정도를 기록하세요.")
    body = "\n".join(lines)

    for card in picked:
        srs.mark_served(state, str(card["id"]), today)

    return TaskResult(
        "english",
        Message(head, body, tags=["speaking_head"]),
        f"{len(picked)}장 출제",
        changed=True,
        extras={"ids": [str(c["id"]) for c in picked]},
    )
