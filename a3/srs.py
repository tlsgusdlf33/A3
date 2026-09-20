"""SM-2 기반 간격 반복.

품질(quality) 0~5. 3 미만이면 실패로 보고 처음부터 다시 돌린다.
기술사 서술형처럼 '봤다/못 봤다'만 기록해도 되게 grade 헬퍼를 둔다.
"""

from __future__ import annotations

import datetime as dt
import hashlib
from typing import Any

MIN_EASE = 1.3
DEFAULT_EASE = 2.5


def new_card(card_id: str, today: dt.date) -> dict[str, Any]:
    return {
        "id": card_id,
        "ease": DEFAULT_EASE,
        "interval": 0,
        "reps": 0,
        "lapses": 0,
        "due": today.isoformat(),
        "last": None,
    }


def review(card: dict[str, Any], quality: int, today: dt.date) -> dict[str, Any]:
    """SM-2 한 스텝. card 를 변형하지 않고 새 dict 를 돌려준다."""
    if not 0 <= quality <= 5:
        raise ValueError("quality 는 0~5 여야 합니다.")
    out = dict(card)
    ease = float(out.get("ease", DEFAULT_EASE))
    reps = int(out.get("reps", 0))

    if quality < 3:
        reps = 0
        interval = 1
        out["lapses"] = int(out.get("lapses", 0)) + 1
    else:
        reps += 1
        if reps == 1:
            interval = 1
        elif reps == 2:
            interval = 6
        else:
            interval = max(1, round(int(out.get("interval", 1)) * ease))
        ease = ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        ease = max(MIN_EASE, ease)

    out["ease"] = round(ease, 3)
    out["reps"] = reps
    out["interval"] = interval
    out["last"] = today.isoformat()
    out["due"] = (today + dt.timedelta(days=interval)).isoformat()
    return out


def is_due(card: dict[str, Any], today: dt.date) -> bool:
    due = card.get("due")
    if not due:
        return True
    return dt.date.fromisoformat(due) <= today


def _tiebreak(card_id: str, today: dt.date) -> int:
    """같은 날 같은 순위면 안정적이지만 날마다 달라지는 순서를 준다."""
    seed = f"{card_id}:{today.isoformat()}".encode()
    return int.from_bytes(hashlib.sha256(seed).digest()[:4], "big")


def pick_due(
    items: list[dict[str, Any]],
    cards: dict[str, dict[str, Any]],
    today: dt.date,
    limit: int,
    id_key: str = "id",
) -> list[dict[str, Any]]:
    """오늘 뽑을 항목을 고른다.

    우선순위는 세 단계다.
      1. 채점된 복습 카드 — 기억이 사라지기 전에 다시 봐야 한다. 연체가 클수록 먼저.
      2. 아직 한 번도 안 본 새 카드 — 진도가 나가야 한다.
      3. 출제됐지만 채점하지 않은 카드 — 다시 보여줄 가치는 있지만,
         새 카드를 밀어내면 덱을 영영 다 못 돈다. 그래서 맨 뒤.
    """
    graded: list[tuple[int, int, dict[str, Any]]] = []
    fresh: list[tuple[int, dict[str, Any]]] = []
    ungraded: list[tuple[int, int, dict[str, Any]]] = []

    for item in items:
        cid = str(item[id_key])
        card = cards.get(cid)
        if card is None:
            fresh.append((_tiebreak(cid, today), item))
            continue
        if not is_due(card, today):
            continue
        overdue = (today - dt.date.fromisoformat(card["due"])).days
        row = (-overdue, _tiebreak(cid, today), item)
        if int(card.get("reps", 0)) > 0 or card.get("last"):
            graded.append(row)
        else:
            ungraded.append(row)

    for bucket in (graded, ungraded):
        bucket.sort(key=lambda t: (t[0], t[1]))
    fresh.sort(key=lambda t: t[0])

    picked = [item for _, _, item in graded[:limit]]
    if len(picked) < limit:
        picked += [item for _, item in fresh[: limit - len(picked)]]
    if len(picked) < limit:
        picked += [item for _, _, item in ungraded[: limit - len(picked)]]
    return picked


# 출제했지만 채점하지 않은 카드를 며칠 뒤로 미뤄 둘 기간.
# 이게 없으면 채점을 건너뛴 카드가 매일 다시 뽑혀 진도가 나가지 않는다.
SERVE_RESERVE_DAYS = 7


def mark_served(
    cards: dict[str, dict[str, Any]],
    card_id: str,
    today: dt.date,
    reserve_days: int = SERVE_RESERVE_DAYS,
) -> dict[str, Any]:
    """카드를 '오늘 출제됨'으로 기록한다.

    채점(`review`)은 사용자가 별도로 한다. 채점이 없더라도 같은 카드가 다음 날
    다시 뽑히지 않도록 due 를 미뤄 둔다. 채점하면 `review` 가 due 를 덮어쓴다.
    """
    card = cards.get(card_id)
    if card is None:
        card = new_card(card_id, today)
        cards[card_id] = card
    card["served"] = today.isoformat()
    if is_due(card, today):
        card["due"] = (today + dt.timedelta(days=reserve_days)).isoformat()
    return card
