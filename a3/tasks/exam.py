"""건설기계기술사 일일 훈련.

오늘 볼 문제를 간격 반복으로 골라, 답안 전개 틀과 채점 키워드를 함께 보낸다.
키워드는 접어두지 않는다 — 휴대폰에서는 '먼저 떠올리고 스크롤한다'가 현실적이다.
"""

from __future__ import annotations

from a3 import srs, util
from a3.config import Config
from a3.notify import Message
from a3.store import Store
from a3.tasks import TaskResult, register
from a3.tasks.decks import load_deck

DECK = "exam_deck.yaml"
DECK_KEY = "exam"


def _header(config: Config) -> tuple[str, str]:
    """(제목 접미사, 본문 머리말)"""
    raw = config.get("exam", "date", default="")
    name = config.get("exam", "name", default="기술사")
    date = util.parse_date(raw) if raw else None
    if not date:
        return "", f"📌 {name} (시험일 미설정 — config.yaml 의 exam.date)"
    label = util.dday_label(date)
    note = ""
    if config.get("exam", "provisional", default=False):
        rnd = config.get("exam", "round", default="")
        note = f" ※ {rnd} 추정일. Q-Net 공고 확인 필요"
    return f" {label}", f"📌 {name} {label} ({date.isoformat()}){note}"


def _render(card: dict, frames: dict, index: int, total: int) -> str:
    frame = frames.get(card.get("frame_as") or card["category"], [])
    lines = [
        f"【{index}/{total}】 {card['type']} · {card['category']}",
        f"Q. {card['q']}",
        "",
        "— 답안 전개 —",
    ]
    lines += [f"  {step}" for step in frame]
    lines += ["", "— 채점 키워드 (먼저 떠올려 보세요) —", "  " + " · ".join(card.get("keywords", []))]
    return "\n".join(lines)


@register("exam", "건설기계기술사 일일 문제 훈련 (간격 반복)")
def run(config: Config, store: Store) -> TaskResult:
    deck = load_deck(DECK)
    cards = deck["cards"]
    wanted = config.get("exam", "categories", default=[]) or []
    if wanted:
        cards = [c for c in cards if c["category"] in wanted]
        if not cards:
            raise ValueError(f"exam.categories 에 해당하는 문제가 없습니다: {wanted}")

    limit = int(config.get("exam", "daily_cards", default=3))
    today = util.today()
    state = store.deck(DECK_KEY)
    picked = srs.pick_due(cards, state, today, limit)

    suffix, head = _header(config)
    if not picked:
        body = f"{head}\n\n오늘 예정된 복습 카드가 없습니다. 쉬어가도 좋습니다. 👍"
        return TaskResult(
            "exam",
            Message(f"🏗️ 기술사 훈련{suffix}", body, tags=["hammer_and_wrench"]),
            "due 카드 없음",
        )

    total = len(picked)
    blocks = [_render(c, deck.get("frames", {}), i + 1, total) for i, c in enumerate(picked)]
    reviewed = len(state)
    body = "\n\n".join(
        [head, f"오늘 {total}문제 · 누적 학습 {reviewed}/{len(cards)}문항", *blocks]
    )
    body += "\n\n✍️ 답안을 써 본 뒤 `a3 grade exam <id> <0-5>` 로 기록하세요."

    # 출제 사실을 기록한다. 채점은 사용자가 `a3 grade` 로 따로 한다.
    for card in picked:
        srs.mark_served(state, str(card["id"]), today)

    ids = ", ".join(str(c["id"]) for c in picked)
    return TaskResult(
        "exam",
        Message(f"🏗️ 기술사 훈련{suffix}", body, tags=["hammer_and_wrench"], priority="default"),
        f"{total}문제 출제 ({ids})",
        changed=True,
        extras={"ids": [str(c["id"]) for c in picked]},
    )
